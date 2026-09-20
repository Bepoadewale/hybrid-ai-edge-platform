# Completion Target

PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE

# Current Completion Blockers

- Run control plane and multiple independent agents with real ONNX inference and signed package reconciliation.
- Demonstrate permitted fallback, privacy denial, offline buffering/reconnect, heterogeneous rollout, tamper rejection, and bad-OTA rollback.

# P0 — Required for Portfolio Claim

P0 blocks PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE; do not select P1/P2 work first.

- Verify current ONNX Runtime and create a tiny real local model fixture.
- Build FastAPI control plane plus one independent device agent with registration/heartbeat.
- Sign model package using Ed25519 and verify signature/digest before activation.
- Add unified inference, local route, local cloud-fallback fixture and LOCAL_ONLY denial.
- Extend to multiple agents, desired-state reconciliation and staged canary rollout.
- Demonstrate bad-model rollback, tamper rejection and offline telemetry/reconnect.

# P1 — Production Hardening

- SQLite persistence, rate limits, metrics/OTel, cache bounds, key rotation and rollout recovery.

# P2 — Enhancements

- CLI, benchmark reports and dashboard.

# P3 — Future / Cloud / Hardware

- llama.cpp, ExecuTorch, mobile, NPU, battery/thermal hardware and cloud control plane.
