# Public boundary

## What belongs here

- Compact, original functional synthesis written for this graph.
- Selected direct public source links and minimal source metadata.
- Synthetic, non-personal examples only when an example is necessary.
- Explicit fact, inference, and unknown labels.

## What does not belong here

- Article text, captures, media, attachments, raw responses, downloaded pages, or a catalog intended to substitute for the help center.
- A crawler, archive importer, source mirror, bulk index, or opaque local retrieval corpus.
- Personal names, patient data, customer data, credentials, local-machine paths, or internal provenance.
- Claims about data storage, schema, API protocol, authentication design, infrastructure, security controls, or product behavior beyond a cited source.

`python3 scripts/validate.py` applies the maintained JSON Schema vocabulary used by both public JSON documents, rejects unknown fields at every defined record level, and rejects internal absolute paths in every string value. `python3 scripts/public_boundary.py` scans the whole candidate public tree: tracked/index paths plus non-ignored candidate files, including root files, `.go`, scripts, schemas, tests, documentation, data, assets, and the license.

No candidate line or source file is exempt from the scanner. Its own marker constants and synthetic negative-test probes are assembled from harmless source fragments, so the scanner still inspects every candidate line, including `scripts/public_boundary.py` and `tests/test_graph.py`. `make check` validates the graph, runs regressions, scans the full candidate tree, and fails when `docs/public-safety-audit.md` is stale. Regenerate the deterministic audit with `make audit`.

Passing these checks does not establish legal clearance or automatically detect every paraphrase or copyright infringement. Before publication, review the exact staged tree, source terms, database-rights questions where applicable, and the current public visibility decision.
