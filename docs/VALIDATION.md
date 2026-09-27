# Validation

## Commands

```bash
make install
make bootstrap-local
make smoke
make demo-fleet
make demo-rollout
make demo-bad-rollout
make demo-tamper
make demo-offline
make verify
make clean-local
```

`make bootstrap-local` builds a tiny signed ONNX package family, starts the FastAPI
control plane and local cloud fixture, then starts five independent device agents.
`clean-local` only stops PIDs stored under `.local`, removes `.local`, and removes
generated package artifacts under this repository. It never runs a global Docker,
Kubernetes, or host cleanup.

## Clean-Room Validation

Before completion, record date, commit SHA, operating system, Python/ONNX Runtime
versions, clean-state verification, exact command output, successful/failed scenario
evidence, teardown verification, and a second clean bootstrap/demo result.

The final required sequence is:

```bash
make cleanroom-validate
make cleanroom-validate
```

No existing `.local` state, cached packages, manual service process, or simulated
hardware profile is evidence by itself.

## Executed Clean-Room Evidence

- **Date:** 2026-09-27
- **Implementation commit:** `f8da794` (`feat: execute local hybrid edge fleet lifecycle`).
- **Environment:** macOS; Python 3.14.0; ONNX Runtime 1.30.0; CPUExecutionProvider.
- **Starting state:** project `.local` and generated `models/packages` absent; no agent/control-plane process retained by this project.

Two clean-room cycles ran:

```bash
make cleanroom-validate
make cleanroom-validate
```

Each cycle built v1/v2/v3/v4 signed ONNX packages, started the FastAPI control plane,
local cloud fixture, and five independent agent processes; then executed smoke, real
local inference, cloud fallback, privacy denial, canary/expand v2 rollout, offline
return, bad v3 readiness rollback, post-signing v4 tamper rejection, offline telemetry
buffer/reconnect, unauthenticated device-token rejection, Ruff, and seven tests. Both
cycles completed with project-scoped cleanup.

Observed local inference latency varied from 0.061ms to 0.206ms for the deliberately
tiny fixture model. These values are development-machine measurements only, not a
mobile/GPU/NPU benchmark claim. After each cleanup, `.local` and generated package
artifacts were absent.
