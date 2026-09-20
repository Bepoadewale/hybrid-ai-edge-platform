# Validation

Run `PYTHONPATH=control-plane/src python3 -m pytest -q`. Live platform status requires versions, services, recorded independent agent processes, actual ONNX Runtime execution/provider, cryptographic signature/digest verification, control-plane interaction, failure/rollback/offline evidence, and environment assumptions. Simulated hardware values must remain labelled; never fabricate validation.

## Clean-Room Validation

Do not populate this section until executed. Record: date, commit SHA, OS/environment, Docker/kind/Kubernetes and key dependency versions where applicable; clean starting state; exact install/bootstrap/smoke/demo/failure/validation/cleanup commands; observed results; post-cleanup absence verification; and the second-bootstrap result. No prior local state or fabricated evidence is acceptable.
