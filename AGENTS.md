# Hybrid AI Edge Platform — Agent Guide

Mission: operate policy-controlled local/cloud inference and safe model rollout across heterogeneous simulated devices; distinguish simulated hardware from real platform behavior.

Stack: Python 3.12 foundation; future FastAPI, ONNX Runtime, device-agent processes, SQLite and local cloud fixture.

Commands: `PYTHONPATH=control-plane/src python3 -m pytest -q`; add real process/demo targets only after they execute.

Rules: no fake inference/OTA/rollback claims; model packages require real signatures and digest verification; privacy overrides fallback; no secrets/main pushes; update factual status/backlog after validation.
