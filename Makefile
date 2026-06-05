.PHONY: help test install clean ask

help:		## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

test:		## Run the offline test suite (no API key needed)
	cd .. && python -m unittest discover -s chain_of_verification/tests -t . -v

install:	## Editable install of the package
	pip install -e .

ask:		## Verify an answer: make ask ARGS='"Name politicians born in NYC" --show-steps'
	python -m chain_of_verification $(ARGS)

clean:		## Remove caches and build artifacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf *.egg-info build dist .eggs
