# Completion Target

PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE

# Current Completion Blockers

None for the local-first completion gate.

# P0 — Required for Portfolio Claim

P0 blocks PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE; do not select P1/P2 work first.

- [x] Verify ONNX Runtime and create a tiny real local model fixture.
- [x] Build FastAPI control plane plus independent device agents with registration/heartbeat.
- [x] Sign model package using Ed25519 and verify signature/digest before activation.
- [x] Add unified inference, local route, local cloud-fallback fixture and LOCAL_ONLY denial.
- [x] Extend to multiple agents, desired-state reconciliation and staged canary rollout.
- [x] Demonstrate bad-model rollback, tamper rejection and offline telemetry/reconnect.

# P1 — Production Hardening

- SQLite persistence, rate limits, metrics/OTel, cache bounds, key rotation and rollout recovery.

# P2 — Enhancements

- CLI, benchmark reports and dashboard.

# P3 — Future / Cloud / Hardware

- llama.cpp, ExecuTorch, mobile, NPU, battery/thermal hardware and cloud control plane.
# Clean-Room Completion Blocker

- [x] Pass the full clean-room reproducibility gate: deterministic bootstrap, smoke, fleet/rollout/offline demos, safe cleanup, a second clean bootstrap, and recorded evidence.
