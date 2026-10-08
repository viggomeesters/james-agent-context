GO_STACK ?= ../go-workflow-stack

.PHONY: check
check:
	python3 $(GO_STACK)/cli/go.py validate .
	python3 $(GO_STACK)/cli/go.py readback .
