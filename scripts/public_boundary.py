#!/usr/bin/env python3
"""Fail closed on payload-like material and internal provenance in the candidate public tree."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Build scanner marker strings from fragments so this scanner is itself scanned
# without a bypass. Candidate lines never receive exemptions.
PAYLOAD_MARKERS = tuple(
    left + right
    for left, right in (
        ("content", "_b64"),
        ("content", "_bytes"),
        ("raw", "_html"),
        ("article", "_body"),
        ("article", "_markdown"),
        ("local", "_markdown_path"),
        ("local", "_json_path"),
        ("snapshot", "_path"),
    )
)
INTERNAL_PATH_MARKERS = tuple(
    prefix + name + suffix
    for prefix, name, suffix in (
        ("/", "home", "/"),
        ("/", "mnt", "/"),
        ("/", "srv", "/"),
        ("/", "var", "/"),
        ("/", "opt", "/"),
        ("/", "root", "/"),
        ("/", "etc", "/"),
        ("/", "private", "/"),
        ("file", "://", ""),
    )
)
SECRET_MARKERS = tuple(
    left + right
    for left, right in (
        ("ghp", "_"),
        ("gho", "_"),
        ("ghu", "_"),
        ("ghs", "_"),
        ("api", "_key"),
        ("api", "-key"),
        ("pass", "word"),
        ("private", "_key"),
        ("private", "-key"),
    )
)


def git_paths(*args: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [value.decode("utf-8") for value in completed.stdout.split(b"\0") if value]


def candidates() -> list[Path]:
    """Return every tracked/index path plus every non-ignored candidate new file."""
    names = set(git_paths())
    names.update(git_paths("--others", "--exclude-standard"))
    files: list[Path] = []
    for name in sorted(names):
        path = ROOT / name
        if not path.exists():
            raise ValueError(f"candidate public path is missing from working tree: {name}")
        if path.is_symlink():
            raise ValueError(f"candidate public path must not be a symlink: {name}")
        if path.is_file():
            files.append(path)
    return files


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def line_findings(path: Path, line: str, line_number: int) -> list[str]:
    lowered = line.lower()
    findings: list[str] = []
    if any(marker in lowered for marker in PAYLOAD_MARKERS):
        findings.append(f"payload marker in {display_path(path)}:{line_number}")
    if any(marker in lowered for marker in INTERNAL_PATH_MARKERS) or (len(line) > 3 and line[1:3] == ":\\"):
        findings.append(f"internal-path marker in {display_path(path)}:{line_number}")
    if any(marker in lowered for marker in SECRET_MARKERS):
        findings.append(f"secret marker in {display_path(path)}:{line_number}")
    return findings


def scan(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"binary file is not allowed in public candidate tree: {display_path(path)}")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            findings.extend(line_findings(path, line, line_number))
    return findings


def audit(paths: list[Path]) -> str:
    rows = [
        "# Public-safety audit",
        "",
        "Automated current-candidate-tree inventory. It is generated deterministically from tracked/index paths plus non-ignored candidate files; it does not certify legal clearance, detect all paraphrase or copyright infringement, or replace human publication review.",
        "",
        "No candidate path or line has a scanner exemption. Scanner marker constants and synthetic probes are assembled from harmless source fragments so the scanner can inspect every candidate line, including its own implementation and tests.",
        "",
        "| File | Automated boundary scan | Rendered/nonblank |",
        "|---|---|---|",
    ]
    for path in paths:
        suffix = path.suffix.lower()
        rendered = "yes" if suffix in {".svg", ".html"} and path.read_text(encoding="utf-8").strip() else "n/a"
        rows.append(f"| `{display_path(path)}` | clear at generation time | {rendered} |")
    rows.extend(
        [
            "",
            f"**Automated scope:** {len(paths)} candidate files; scanner findings at generation time: 0.",
            "Reproduce: `python3 scripts/public_boundary.py --audit docs/public-safety-audit.md` followed by `python3 scripts/public_boundary.py` and `git diff --exit-code -- docs/public-safety-audit.md`.",
        ]
    )
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    audit_group = parser.add_mutually_exclusive_group()
    audit_group.add_argument("--audit", metavar="PATH", help="write a deterministic candidate-tree inventory")
    audit_group.add_argument("--check-audit", metavar="PATH", help="fail if a committed inventory is stale")
    args = parser.parse_args()
    try:
        paths = candidates()
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"public-boundary scan failed: {error}")
        return 1
    findings = scan(paths)
    if findings:
        print("public-boundary scan failed:", *[f"- {finding}" for finding in findings], sep="\n")
        return 1
    expected_audit = audit(paths)
    if args.check_audit:
        audit_path = ROOT / args.check_audit
        if not audit_path.exists() or audit_path.read_text(encoding="utf-8") != expected_audit:
            print(f"public-boundary scan failed: stale or missing audit: {display_path(audit_path)}")
            return 1
    if args.audit:
        audit_path = ROOT / args.audit
        audit_path.write_text(expected_audit, encoding="utf-8")
        print(f"public-safety audit generated: {display_path(audit_path)} ({len(paths)} files)")
    print(f"public-boundary scan passed: {len(paths)} candidate files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
