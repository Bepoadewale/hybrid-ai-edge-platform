# Project Status

## Current Maturity

FOUNDATION

## Maturity Model

`FOUNDATION` → `PARTIALLY VALIDATED` → `LOCAL END-TO-END VALIDATED` → `PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE`.

## Executed and Verified

- Capability matching, deterministic routing and desired-state/domain tests.

## Implemented but Not End-to-End Validated

- Model/device policy core.

## Simulated

- Device profiles, hardware states and package digest values.

## Architecture / Contracts Only

- FastAPI control plane, device processes, ONNX inference, cloud fixture, signing, OTA, telemetry and rollback.

## Known Failures

- Model manifest uses a placeholder digest because model signing is not implemented. GitHub CI rerun is pending after changing the initialization workflow to install test tooling without packaging fixture directories.

## Current P0 Objective

Run one independently registered agent using a tiny signed ONNX package for local inference.

## Completion Blockers

- FastAPI control plane, independent device agents, ONNX inference, signing, cloud fixture, and telemetry are not live.
- Desired-state activation, multi-device compatibility, privacy routing, offline buffering/reconnect, staged OTA, tamper rejection, and rollback are unexecuted.

## Explicitly Unexecuted Production Adapters

- Real mobile/NPU hardware, llama.cpp/ExecuTorch, battery/thermal sensors, cloud fleet control plane, and production PKI.

## Last Validation

- `PYTHONPATH=control-plane/src ../ai-platform-control-plane/.venv/bin/python -m pytest -q`: 4 passed.

## Last Updated

2026-09-19, baseline `47ff5cb`.
