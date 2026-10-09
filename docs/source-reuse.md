# Source and reuse guidance

Each record in `data/sources.json` is one of 21 selected pointers to a public James Software Help Center page. A pointer supports traceability; it is not a license grant and it is not a cached copy of that page.

`data/knowledge-base-index.json` and `docs/knowledge-base-index.md` are separate from those selected graph sources. They provide a title/URL-only, alphabetical list of 637 anonymous public article links from the October 8, 2026 archive snapshot. They are not a live verification of those URLs and are not an article mirror.

When extending this graph:

1. Read a public source directly and write a new, concise synthesis in your own words.
2. Add only the minimum metadata needed to identify a selected graph source: id, title, publisher, and direct URL.
3. Add `fact` only for behavior explicitly described by the source. Add `inference` for a stated logical synthesis. Keep unsupported topics in `unknowns`.
4. Do not import article text, images, files, videos, transcripts, article snapshots, author names, raw responses, or other mirrored material. The complete link index may contain only title and canonical public URL.
5. Do not use this graph or the link index to assert a physical data model, implementation architecture, complete API contract, or security design.

The original repository content is MIT-licensed only to the extent described in `README.md`. Third-party materials remain subject to their own terms and rights. A hyperlink list is not a republication of article text, but this repository makes no legal-clearance determination; rights in an exhaustive metadata index, including any database-rights question, remain for publication review.
