# Validation

Run `PYTHONPATH=control-plane/src python3 -m pytest -q`. Live platform status requires versions, services, recorded independent agent processes, actual ONNX Runtime execution/provider, cryptographic signature/digest verification, control-plane interaction, failure/rollback/offline evidence, and environment assumptions. Simulated hardware values must remain labelled; never fabricate validation.
