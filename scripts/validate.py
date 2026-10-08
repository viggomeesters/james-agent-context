#!/usr/bin/env python3
"""Validate the compact graph against its maintained JSON Schema; stdlib only."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "data" / "graph.json"
SOURCES = ROOT / "data" / "sources.json"
GRAPH_SCHEMA = ROOT / "schemas" / "graph.schema.json"
SOURCES_SCHEMA = ROOT / "schemas" / "sources.schema.json"
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
# Public records may not carry workstation or service filesystem provenance.
INTERNAL_PATH = re.compile(r"(?i)(?<![A-Za-z0-9:+._-])/(?:home|mnt|srv|var|opt|root|etc|private)(?:/|$)|[A-Z]:\\(?:Users|ProgramData|home)(?:\\|$)|file:/+")


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def issue(errors: list[str], message: str) -> None:
    errors.append(message)


def json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported JSON Schema type: {expected}")


def resolve_ref(schema: dict[str, Any], root_schema: dict[str, Any]) -> dict[str, Any]:
    reference = schema.get("$ref")
    if not reference:
        return schema
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported JSON Schema reference: {reference}")
    target: Any = root_schema
    for segment in reference[2:].split("/"):
        target = target[segment]
    if not isinstance(target, dict):
        raise ValueError(f"schema reference is not an object: {reference}")
    return target


def validate_schema(value: Any, schema: dict[str, Any], root_schema: dict[str, Any], location: str, errors: list[str]) -> None:
    """Apply the JSON Schema vocabulary used by this repository's two schemas."""
    schema = resolve_ref(schema, root_schema)
    expected = schema.get("type")
    if expected and not json_type_matches(value, expected):
        issue(errors, f"{location}: expected {expected}")
        return
    if "enum" in schema and value not in schema["enum"]:
        issue(errors, f"{location}: value is not an allowed enum member")
    if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
        issue(errors, f"{location}: does not match required pattern")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            issue(errors, f"{location}: requires at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            issue(errors, f"{location}: allows at most {schema['maxItems']} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                validate_schema(item, item_schema, root_schema, f"{location}[{index}]", errors)
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in value:
                issue(errors, f"{location}: missing required field {required!r}")
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                issue(errors, f"{location}: unknown fields are not permitted: {extra}")
        for key, item in value.items():
            if key in properties:
                validate_schema(item, properties[key], root_schema, f"{location}.{key}", errors)


def string_values(value: Any, location: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(location, value)]
    if isinstance(value, list):
        return [pair for index, item in enumerate(value) for pair in string_values(item, f"{location}[{index}]")]
    if isinstance(value, dict):
        return [pair for key, item in value.items() for pair in string_values(item, f"{location}.{key}")]
    return []


def validate(graph: dict[str, Any], sources: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    graph_schema = load(GRAPH_SCHEMA)
    sources_schema = load(SOURCES_SCHEMA)
    validate_schema(graph, graph_schema, graph_schema, "graph", errors)
    validate_schema(sources, sources_schema, sources_schema, "sources", errors)

    for document_name, document in (("graph", graph), ("sources", sources)):
        for location, value in string_values(document, document_name):
            if INTERNAL_PATH.search(value):
                issue(errors, f"{location}: forbidden absolute internal path")

    source_ids = [item.get("id") for item in sources.get("sources", []) if isinstance(item, dict)]
    if len(source_ids) != len(set(source_ids)):
        issue(errors, "source ids must be unique")
    for source in sources.get("sources", []):
        if not isinstance(source, dict):
            continue
        if not ID_RE.fullmatch(str(source.get("id", ""))):
            issue(errors, f"invalid source id: {source.get('id')}")
        if not str(source.get("url", "")).startswith("https://jamessoftware.zendesk.com/"):
            issue(errors, f"source must be a direct official help-center URL: {source.get('id')}")

    entities = graph.get("entities", [])
    entity_ids = [item.get("id") for item in entities if isinstance(item, dict)]
    if len(entity_ids) != len(set(entity_ids)):
        issue(errors, "entity ids must be unique")
    for bucket in ("entities", "relationships", "claims"):
        for item in graph.get(bucket, []):
            if not isinstance(item, dict):
                continue
            identifier = item.get("id")
            if not ID_RE.fullmatch(str(identifier or "")):
                issue(errors, f"invalid {bucket} id: {identifier}")
            if item.get("evidence_type") not in {"fact", "inference"}:
                issue(errors, f"{bucket}:{identifier} needs fact or inference evidence_type")
            refs = item.get("source_ids")
            if not isinstance(refs, list) or not refs:
                issue(errors, f"{bucket}:{identifier} needs selected source ids")
            elif unknown := set(refs) - set(source_ids):
                issue(errors, f"{bucket}:{identifier} references unknown sources: {sorted(unknown)}")
    for rel in graph.get("relationships", []):
        if isinstance(rel, dict) and (rel.get("from") not in entity_ids or rel.get("to") not in entity_ids):
            issue(errors, f"relationship {rel.get('id')} references unknown entity")
    for unknown in graph.get("unknowns", []):
        if not isinstance(unknown, dict):
            continue
        if not ID_RE.fullmatch(str(unknown.get("id", ""))) or not unknown.get("statement"):
            issue(errors, "unknowns require id and statement")
        if "evidence_type" in unknown or "source_ids" in unknown:
            issue(errors, f"unknown {unknown.get('id')} must not masquerade as a sourced claim")
    combined = " ".join(item.get("statement", "") for item in graph.get("unknowns", []) if isinstance(item, dict))
    if not all(term in combined.lower() for term in ("database", "api", "backend")):
        issue(errors, "unknowns must explicitly retain physical-schema, API, and backend boundaries")
    return errors


def main() -> int:
    errors = validate(load(GRAPH), load(SOURCES))
    if errors:
        print("validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    graph = load(GRAPH)
    print(f"valid graph: {len(graph['entities'])} entities, {len(graph['relationships'])} relationships, {len(graph['claims'])} claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
