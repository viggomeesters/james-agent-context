# Source and reuse guidance

Each record in `data/sources.json` is a selected pointer to a public James Software Help Center page. A pointer supports traceability; it is not a license grant and it is not a cached copy of that page.

When extending this graph:

1. Read a public source directly and write a new, concise synthesis in your own words.
2. Add only the minimum metadata needed to identify the source: id, title, publisher, and direct URL.
3. Add `fact` only for behavior explicitly described by the source. Add `inference` for a stated logical synthesis. Keep unsupported topics in `unknowns`.
4. Do not import article text, images, files, videos, transcripts, article catalogs, snapshots, or other mirrored material.
5. Do not use this graph to assert a physical data model, implementation architecture, complete API contract, or security design.

The original repository content is MIT-licensed only to the extent described in `README.md`. Third-party materials remain subject to their own terms and rights.
