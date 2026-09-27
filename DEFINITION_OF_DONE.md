# Definition of Done

# Portfolio Complete — Local-First Scope Gate

- [x] FastAPI control plane runs with five independent device-agent processes, capability probe, heartbeats, and desired state.
- [x] Tiny real ONNX model executes through ONNX Runtime and records actual latency/version/`CPUExecutionProvider`.
- [x] Model package has SHA-256 digest and Ed25519 signature; device verifies both and rejects tampering while retaining prior known-good artifact.
- [x] Compatibility uses runtime, memory, architecture/profile, and declared capabilities.
- [x] Reconciliation performs desired model → download → validate → activate → report with current/candidate/previous-good state.
- [x] Local cloud-fixture backend is actually called for allowed fallback; LOCAL_ONLY/privacy-constrained request never falls back.
- [x] LOCAL_ONLY, LOCAL_PREFERRED, CLOUD_PREFERRED, CLOUD_ONLY, and PRIVACY_FIRST have deterministic router behavior; local-first/privacy paths execute in the local demo.
- [x] Offline device continues allowed local operation, uses bounded telemetry buffering, reconnects, and reconciles state.
- [x] Deterministic staged OTA spans canary/broader fleet stages; a bad OTA retains active v2 and blocks expansion.
- [x] Multiple heterogeneous profiles run; network/thermal/battery inputs are explicitly simulated.
- [x] Reproducible local demo, unit/integration/E2E/security/failure tests, and local validation are green; docs distinguish real platform execution from mobile/NPU/cloud adapters.

## Maturity Levels

- **FOUNDATION:** routing/capability logic exists.
- **PARTIALLY VALIDATED:** real agent/runtime integration exists but central fleet story is incomplete.
- **LOCAL END-TO-END VALIDATED:** primary fleet path runs with material rollback/offline/observability gaps.
- **PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE:** every checked gate is executed with evidence.

# Clean-Room Reproducibility Gate

`PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE` requires two executed clean-room cycles: clone → install → bootstrap control plane, independent device agents, signed ONNX fixture, cloud fallback → smoke → local inference/privacy denial/staged rollout/offline demo → bad-OTA rollback demo → validation → project-scoped cleanup → second clean bootstrap/demo. Planned commands: `make install`, `make bootstrap-local`, `make smoke`, `make demo-fleet`, `make demo-rollout`, `make demo-offline`, `make verify`, `make clean-local`.

- [x] Clean bootstrap has no hidden project state; primary and failure demos passed in two cycles.
- [x] Cleanup removes only this project’s `.local`, generated packages, and PID-tracked processes; it does not use global cleanup.
- [x] Post-cleanup absence and two clean-room cycles are recorded in `docs/VALIDATION.md`.
