# Hybrid AI Edge Platform — Agent Guide

Mission: operate policy-controlled local/cloud inference and safe model rollout across heterogeneous simulated devices; distinguish simulated hardware from real platform behavior.

Stack: Python 3.12 foundation; future FastAPI, ONNX Runtime, device-agent processes, SQLite and local cloud fixture.

Commands: `PYTHONPATH=control-plane/src python3 -m pytest -q`; add real process/demo targets only after they execute.

Rules: no fake inference/OTA/rollback claims; model packages require real signatures and digest verification; privacy overrides fallback; no secrets/main pushes; update factual status/backlog after validation.

Completion rule: do not mark **PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE** unless `DEFINITION_OF_DONE.md` has executed evidence. Device objects, routing tests, package placeholders, manifests, and documentation do not prove edge operations. Multiple independent agents, real ONNX inference, signed OTA, policy routing, rollback, and offline recovery must execute locally; simulated hardware and unexecuted mobile/NPU adapters remain explicit.

## Clean-room reproducibility

Clean-room reproducibility is a mandatory completion criterion. Do not mark this repository
`PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE` until a new engineer can reproduce the platform from a
clean project state using documented commands, execute the primary and required failure demos, run
validation, and safely tear down only this project's local resources. Do not infer reproducibility
from an existing developer environment; execute it after project-specific cleanup.
