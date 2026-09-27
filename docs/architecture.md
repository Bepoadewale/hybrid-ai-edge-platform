# Architecture

The local platform runs five independent agent processes, a FastAPI fleet control
plane, and a separate FastAPI cloud-fallback fixture. Each agent owns a state
directory containing its active model version, previous-good version, cached model
packages and bounded telemetry buffer.

```text
control plane (SQLite) -- desired state / signed package --> device agent
device agent -- heartbeat / metadata-only telemetry ------> control plane
device agent -- local ONNX Runtime --> response
device agent -- allowed fallback --> local cloud fixture
```

Agents authenticate control-plane traffic with a generated local token. Packages are
signed by the release-side Ed25519 key; devices receive only the public key and verify
both the canonical manifest signature and the model SHA-256 digest before staging.

Device memory, storage, architecture, network, battery and thermal values are
simulated profile inputs. The processes, HTTP communication, SQLite durability, ONNX
Runtime CPU execution, cryptographic verification, reconciliation and routing are not
simulated.
