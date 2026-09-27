# Local versus production scope

Executed locally: FastAPI control plane and cloud fixture, SQLite persistence,
independent agents, token-authenticated device calls, Ed25519 package signing,
ONNX Runtime CPU inference, staged rollout/rollback, offline buffering and a local
dashboard.

Simulated: device RAM/storage/architecture profiles, network quality, thermal state
and battery state. They are policy inputs only; this project makes no physical-device
performance claim.

Not executed: real mobile or embedded devices, NPU execution providers, llama.cpp,
ExecuTorch, mTLS/attestation, hosted object storage, managed control plane,
multi-region rollout, cloud metrics backends and production key management.
