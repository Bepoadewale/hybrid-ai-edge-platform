.PHONY: install bootstrap-local smoke demo-fleet demo-rollout demo-bad-rollout demo-tamper demo-offline verify clean-local cleanroom-validate
install:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e '.[dev]'
bootstrap-local:
	./scripts/bootstrap-local.sh
smoke:
	./scripts/smoke.sh
demo-fleet:
	./scripts/demo-fleet.sh
demo-rollout:
	./scripts/demo-rollout.sh
demo-bad-rollout:
	./scripts/demo-bad-rollout.sh
demo-tamper:
	./scripts/demo-tamper.sh
demo-offline:
	./scripts/demo-offline.sh
verify:
	.venv/bin/python -m ruff check control-plane/src scripts tests
	.venv/bin/python -m pytest -q
clean-local:
	./scripts/clean-local.sh
cleanroom-validate:
	./scripts/cleanroom-validate.sh
