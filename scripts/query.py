#!/usr/bin/env python3
"""Offline query utility for the compact graph; stdlib only."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str) -> dict:
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the James functional context graph offline.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="list entity ids and labels")
    group.add_argument("--search", metavar="TEXT", help="search original graph summaries and claims")
    group.add_argument("--neighbors", metavar="ENTITY_ID", help="show an entity and directly connected relationships")
    group.add_argument("--claim", metavar="CLAIM_ID", help="show one claim with its selected source pointers")
    args = parser.parse_args()
    graph, sources = load("graph.json"), load("sources.json")
    source_by_id = {item["id"]: item for item in sources["sources"]}
    entities = {item["id"]: item for item in graph["entities"]}
    if args.list:
        emit([{"id": item["id"], "label": item["label"], "evidence_type": item["evidence_type"]} for item in graph["entities"]])
        return 0
    if args.neighbors:
        node = entities.get(args.neighbors)
        if not node:
            print(f"unknown entity: {args.neighbors}", file=sys.stderr)
            return 2
        links = [item for item in graph["relationships"] if args.neighbors in (item["from"], item["to"])]
        emit({"entity": node, "relationships": links, "sources": [source_by_id[x] for x in node["source_ids"]]})
        return 0
    if args.claim:
        claim = next((item for item in graph["claims"] if item["id"] == args.claim), None)
        if not claim:
            print(f"unknown claim: {args.claim}", file=sys.stderr)
            return 2
        emit({"claim": claim, "sources": [source_by_id[x] for x in claim["source_ids"]]})
        return 0
    needle = args.search.casefold()
    records = []
    for kind, values in (("entity", graph["entities"]), ("relationship", graph["relationships"]), ("claim", graph["claims"]), ("unknown", graph["unknowns"])):
        for value in values:
            if needle in json.dumps(value, ensure_ascii=False).casefold():
                records.append({"kind": kind, "record": value})
    emit(records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
