# Hybrid AI Edge Platform

A local-first fleet operations platform for policy-controlled AI inference across
heterogeneous edge devices. It decides whether an inference request should run on a
device, use an allowed local cloud-fallback fixture, or be denied because privacy
overrides availability.

## What it demonstrates

```text
Fleet control plane → desired model state → independent device agents
         ↓                         ↓
signed ONNX package → verify → stage → readiness inference → activate / retain known-good
         ↓
local inference OR policy-controlled cloud fallback OR privacy denial
```

Five independent local device-agent processes simulate laptop-high, mobile-high,
mobile-low, edge-gateway, and initially offline hardware profiles. The hardware
properties are clearly simulated; the control plane, HTTP reconciliation, ONNX
Runtime inference, signatures, model package verification, routing, telemetry, staged
rollout, and rollback behavior are real local software execution.

## Run locally

Requires Python 3.12+ and no cloud account, GPU, phone, or paid API.

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

Dashboard: `http://localhost:18100/`

## Executed scenarios

| Scenario | Result |
| --- | --- |
| Local-compatible request | Real ONNX Runtime CPU inference; actual latency and `CPUExecutionProvider` returned. |
| Missing local model, public data | Separate local cloud-fixture service is called. |
| Restricted / `LOCAL_ONLY` request | `403`; cloud fixture is never called. |
| Heterogeneous v2 rollout | Representative laptop-high and mobile-high canary activate v2; mobile-low stays on compatible v1. |
| Offline device return | Local device reconnects, registers, fetches desired v2, verifies, and activates it. |
| Bad signed v3 | Candidate executes readiness inference, fails its configured readiness gate, and canaries retain active v2. |
| Tampered signed v4 | SHA-256 verification fails before activation; v2 remains active. |
| Offline operation | Local inference continues under local-only privacy policy; bounded telemetry buffers then uploads on reconnect. |

## Security and safety model

- Model packages contain a canonical manifest, SHA-256 model digest, and Ed25519 signature.
- Each locally simulated device authenticates its control-plane/package requests with a generated per-project device token. Production mTLS, attestation and key rotation remain future adapters.
- Devices receive only the public verification key; the generated local private key remains
  under ignored project state.
- Candidate packages never overwrite the active model before verification and readiness.
- Privacy policy is evaluated before cloud fallback. Restricted data is never silently
  retried against the cloud fixture.
- Telemetry records metadata only—not raw inference inputs or outputs.

## Evidence boundary

This repository does not claim real mobile deployment, NPU/CoreML/NNAPI/QNN behavior,
battery or thermal measurement, llama.cpp/ExecuTorch execution, managed cloud fleet
control, or production PKI. Those are documented future adapters. The local CPU ONNX
path is the executed core runtime.

## Documentation

- [Architecture](docs/architecture.md)
- [Demo guide](docs/demo.md)
- [Security boundary](docs/security.md)
- [Local versus production scope](docs/production-vs-local.md)
- [Executed validation evidence](docs/VALIDATION.md)
