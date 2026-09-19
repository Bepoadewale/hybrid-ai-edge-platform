# Project Status

## Current Maturity

FOUNDATION

## Executed and Verified

- Capability matching, deterministic routing and desired-state/domain tests.

## Implemented but Not End-to-End Validated

- Model/device policy core.

## Simulated

- Device profiles, hardware states and package digest values.

## Architecture / Contracts Only

- FastAPI control plane, device processes, ONNX inference, cloud fixture, signing, OTA, telemetry and rollback.

## Known Failures

- Model manifest uses a placeholder digest; remote fetch blocked by DNS on 2026-09-19.

## Current P0 Objective

Run one independently registered agent using a tiny signed ONNX package for local inference.

## Last Validation

- `PYTHONPATH=control-plane/src ../ai-platform-control-plane/.venv/bin/python -m pytest -q`: 4 passed.

## Last Updated

2026-09-19, baseline `47ff5cb`.
