PYTHON ?= python3

.PHONY: check validate test scan audit audit-check query
check: validate test scan audit-check

validate:
	$(PYTHON) scripts/validate.py

test:
	$(PYTHON) -m unittest discover -s tests -v

scan:
	$(PYTHON) scripts/public_boundary.py

audit:
	$(PYTHON) scripts/public_boundary.py --audit docs/public-safety-audit.md

audit-check:
	$(PYTHON) scripts/public_boundary.py --check-audit docs/public-safety-audit.md

query:
	$(PYTHON) scripts/query.py --list
