# James Agent Context

![Graph nodes connected by evidence-aware links](assets/hero.svg)

A small, offline, JSON-first functional knowledge graph for agents working with James Software. It is an **independent synthesis** of selected public documentation: 17 entities, 12 relationships, 4 claims, 3 explicit unknowns, and 21 source pointers.

## Installation

No installation is required beyond Python 3. Run the repository directly:

```bash
make check
```

## Usage

```bash
python3 scripts/query.py --neighbors consultation
python3 scripts/query.py --claim claim-financial-hold
python3 scripts/query.py --search portal
```

No package install, network request, crawler, or source archive is required to validate or query the graph.

## Agent loading order

1. Load `data/graph.json` and keep each record's `evidence_type` intact.
2. Resolve cited `source_ids` through `data/sources.json` when a user needs the public supporting page.
3. Treat `fact` as a compact statement of documented functional behavior; present `inference` as an inference, not product internals.
4. Preserve `unknowns`. Do not fabricate physical schema, backend, API, security, or deployment details.
5. Re-open a cited public page before relying on it for changing operational guidance.

## Boundaries and reuse

- This is **not** a James Software product, official documentation, or endorsement.
- It contains original compact graph descriptions and selected source metadata only: no article body, screenshot, media, download, crawler output, or full article index.
- The MIT license applies to this repository's original tooling and original graph expression. It does not grant rights in third-party documentation or trademarks. Source-page terms and applicable database or copyright rights remain relevant.
- This is informational engineering context, not legal, clinical, financial, security, or implementation advice.

See [`docs/public-boundary.md`](docs/public-boundary.md) for the publication boundary and [`docs/source-reuse.md`](docs/source-reuse.md) for source use rules.

## Layout

- `data/graph.json` — graph records and uncertainty boundaries.
- `data/sources.json` — selected direct public source pointers.
- `schemas/` — JSON Schema contracts.
- `scripts/validate.py` — deterministic semantic validation.
- `scripts/query.py` — offline graph query CLI.
- `scripts/public_boundary.py` — payload and local-provenance scanner.
- `tests/` — standard-library regression tests.

## Development

```bash
make check
```

The project intentionally uses local validation instead of GitHub Actions. Any public release or publication requires an independent review of the exact staged tree, sources, and residual rights/privacy boundary.

## License

MIT for the repository's original software and original graph expression; see [`LICENSE`](LICENSE).
