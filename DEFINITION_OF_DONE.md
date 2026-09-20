# Definition of Done

# Portfolio Complete — Local-First Scope Gate

- [ ] FastAPI or chosen control plane runs with multiple independent device-agent processes/containers, identity, capability probe, heartbeats, and desired state.
- [ ] Tiny real ONNX model executes through ONNX Runtime and records actual latency/version/execution provider.
- [ ] Model package has SHA-256 digest and Ed25519 signature; device verifies both and rejects tampering while retaining prior known-good artifact.
- [ ] Compatibility uses runtime, memory, architecture/profile, and declared capabilities.
- [ ] Reconciliation performs desired model → download → validate → activate → report with current/candidate/previous-good state.
- [ ] Local cloud-fixture backend is actually called for allowed fallback; LOCAL_ONLY/privacy-constrained request never falls back.
- [ ] Claimed routing profiles execute deterministically: LOCAL_ONLY, LOCAL_PREFERRED, CLOUD_PREFERRED, CLOUD_ONLY, and PRIVACY_FIRST.
- [ ] Offline device continues allowed local operation, uses bounded telemetry buffering, reconnects, and reconciles state.
- [ ] Deterministic staged OTA spans canary/broader fleet stages; a bad OTA pauses or rolls back.
- [ ] Multiple heterogeneous profiles run; network/thermal/battery inputs are labeled simulated unless physical hardware provides them.
- [ ] Reproducible local demo, unit/integration/E2E/security/failure tests, and CI are green; docs distinguish real platform execution from mobile/NPU/cloud adapters.

## Maturity Levels

- **FOUNDATION:** routing/capability logic exists.
- **PARTIALLY VALIDATED:** real agent/runtime integration exists but central fleet story is incomplete.
- **LOCAL END-TO-END VALIDATED:** primary fleet path runs with material rollback/offline/observability gaps.
- **PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE:** every checked gate is executed with evidence.

# Clean-Room Reproducibility Gate

`PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE` requires two executed clean-room cycles: clone → install → bootstrap control plane, independent device agents, signed ONNX fixture, cloud fallback → smoke → local inference/privacy denial/staged rollout/offline demo → bad-OTA rollback demo → validation → project-scoped cleanup → second clean bootstrap/demo. Planned commands: `make install`, `make bootstrap-local`, `make smoke`, `make demo-fleet`, `make demo-rollout`, `make demo-offline`, `make verify`, `make clean-local`.

- [ ] Clean clone/bootstrap has no hidden state; primary and failure demos pass.
- [ ] Cleanup removes only this project and unrelated resources survive.
- [ ] Post-cleanup absence and second bootstrap/demo are recorded in `docs/VALIDATION.md`.
