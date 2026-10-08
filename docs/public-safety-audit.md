# Public-safety audit

Automated current-candidate-tree inventory. It is generated deterministically from tracked/index paths plus non-ignored candidate files; it does not certify legal clearance, detect all paraphrase or copyright infringement, or replace human publication review.

No candidate path or line has a scanner exemption. Scanner marker constants and synthetic probes are assembled from harmless source fragments so the scanner can inspect every candidate line, including its own implementation and tests.

| File | Automated boundary scan | Rendered/nonblank |
|---|---|---|
| `.gitignore` | clear at generation time | n/a |
| `.go/architecture-principles.json` | clear at generation time | n/a |
| `.go/decisions/events.jsonl` | clear at generation time | n/a |
| `.go/evidence/events.jsonl` | clear at generation time | n/a |
| `.go/hierarchy.json` | clear at generation time | n/a |
| `.go/project.json` | clear at generation time | n/a |
| `.go/runs/events.jsonl` | clear at generation time | n/a |
| `.go/tasks/done/JAC-001.json` | clear at generation time | n/a |
| `.go/vision.json` | clear at generation time | n/a |
| `AGENTS.md` | clear at generation time | n/a |
| `CHANGELOG.md` | clear at generation time | n/a |
| `CONTRIBUTING.md` | clear at generation time | n/a |
| `LICENSE` | clear at generation time | n/a |
| `Makefile` | clear at generation time | n/a |
| `README.md` | clear at generation time | n/a |
| `SECURITY.md` | clear at generation time | n/a |
| `assets/hero.svg` | clear at generation time | yes |
| `data/graph.json` | clear at generation time | n/a |
| `data/sources.json` | clear at generation time | n/a |
| `docs/public-boundary.md` | clear at generation time | n/a |
| `docs/public-safety-audit.md` | clear at generation time | n/a |
| `docs/source-reuse.md` | clear at generation time | n/a |
| `docs/vision.json` | clear at generation time | n/a |
| `go` | clear at generation time | n/a |
| `schemas/graph.schema.json` | clear at generation time | n/a |
| `schemas/sources.schema.json` | clear at generation time | n/a |
| `scripts/bootstrap-stack.sh` | clear at generation time | n/a |
| `scripts/check.sh` | clear at generation time | n/a |
| `scripts/public_boundary.py` | clear at generation time | n/a |
| `scripts/query.py` | clear at generation time | n/a |
| `scripts/validate-go.sh` | clear at generation time | n/a |
| `scripts/validate.py` | clear at generation time | n/a |
| `tests/test_graph.py` | clear at generation time | n/a |

**Automated scope:** 33 candidate files; scanner findings at generation time: 0.
Reproduce: `python3 scripts/public_boundary.py --audit docs/public-safety-audit.md` followed by `python3 scripts/public_boundary.py` and `git diff --exit-code -- docs/public-safety-audit.md`.
