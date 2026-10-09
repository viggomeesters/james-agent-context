#!/usr/bin/env python3
"""Compile a public-safe, deterministic James Help Center link index."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ENTRY_COUNT = 637
SCOPE = "Public anonymous James Help Center article links; link-only index."
URL_RE = re.compile(
    r"^https://jamessoftware\.zendesk\.com/hc/nl/articles/[0-9]+(?:-[^/?#]+)?$"
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def source_entries(catalog: Any) -> list[dict[str, Any]]:
    if isinstance(catalog, list):
        entries = catalog
    elif isinstance(catalog, dict) and set(catalog) == {"snapshot_date", "scope", "entries"}:
        entries = catalog["entries"]
    else:
        raise ValueError("catalog must be a list of article records or a public index object")
    if not isinstance(entries, list):
        raise ValueError("catalog entries must be a list")
    return entries


def compile_entries(catalog: Any) -> list[dict[str, str]]:
    compiled: list[dict[str, str]] = []
    for index, record in enumerate(source_entries(catalog)):
        if not isinstance(record, dict):
            raise ValueError(f"catalog entry {index} must be an object")
        title = record.get("title")
        url = record.get("url")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"catalog entry {index} needs a non-empty title")
        if not isinstance(url, str) or not URL_RE.fullmatch(url):
            raise ValueError(f"catalog entry {index} has a non-canonical public article URL")
        compiled.append({"title": title.strip(), "url": url})
    compiled.sort(key=lambda entry: (entry["title"].casefold(), entry["title"], entry["url"]))
    if len(compiled) != EXPECTED_ENTRY_COUNT:
        raise ValueError(f"catalog must contain exactly {EXPECTED_ENTRY_COUNT} entries")
    urls = [entry["url"] for entry in compiled]
    titles = [entry["title"] for entry in compiled]
    if len(set(urls)) != len(urls):
        raise ValueError("catalog contains duplicate URLs")
    if len(set(titles)) != len(titles):
        raise ValueError("catalog contains duplicate titles")
    return compiled


def index_document(entries: list[dict[str, str]], snapshot_date: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", snapshot_date):
        raise ValueError("snapshot date must use YYYY-MM-DD")
    return {"snapshot_date": snapshot_date, "scope": SCOPE, "entries": entries}


def markdown_document(entries: list[dict[str, str]], snapshot_date: str) -> str:
    lines = [
        "# James knowledge-base article index",
        "",
        f"Link-only alphabetical index of {len(entries)} anonymous public James Help Center articles from the {snapshot_date} archive snapshot. It is not a live availability check.",
        "",
    ]
    lines.extend(f"- [{entry['title']}]({entry['url']})" for entry in entries)
    return "\n".join(lines) + "\n"


def json_text(document: dict[str, Any]) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def index_digest(document: dict[str, Any]) -> str:
    return hashlib.sha256(json_text(document).encode("utf-8")).hexdigest()


def read_document(path: Path) -> dict[str, Any]:
    document = load_json(path)
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain an object")
    return document


def check_equal(expected: dict[str, Any], output_path: Path, markdown_path: Path | None) -> list[str]:
    errors: list[str] = []
    if not output_path.exists() or read_document(output_path) != expected:
        errors.append(f"index differs: {output_path}")
    if markdown_path is not None:
        expected_markdown = markdown_document(expected["entries"], expected["snapshot_date"])
        if not markdown_path.exists() or markdown_path.read_text(encoding="utf-8") != expected_markdown:
            errors.append(f"markdown index differs: {markdown_path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path, help="caller-supplied JSON catalog")
    parser.add_argument("--snapshot-date", default="2026-10-08")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "knowledge-base-index.json")
    parser.add_argument("--markdown", type=Path, default=ROOT / "docs" / "knowledge-base-index.md")
    parser.add_argument("--fixture", type=Path, help="write the projected public inventory fixture")
    parser.add_argument("--check", action="store_true", help="verify existing output against catalog without writing")
    args = parser.parse_args()
    try:
        expected = index_document(compile_entries(load_json(args.catalog)), args.snapshot_date)
        if args.check:
            errors = check_equal(expected, args.output, args.markdown)
            if errors:
                print("index check failed:", *[f"- {error}" for error in errors], sep="\n")
                return 1
            print(f"knowledge-base index check passed: {len(expected['entries'])} entries sha256={index_digest(expected)}")
            return 0
        args.output.write_text(json_text(expected), encoding="utf-8")
        args.markdown.write_text(markdown_document(expected["entries"], expected["snapshot_date"]), encoding="utf-8")
        if args.fixture is not None:
            args.fixture.write_text(json_text(expected), encoding="utf-8")
        print(f"knowledge-base index generated: {len(expected['entries'])} entries sha256={index_digest(expected)}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"knowledge-base index failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
