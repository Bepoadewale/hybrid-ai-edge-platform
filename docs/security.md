# Security boundary

The local demonstration establishes these invariants:

- Device API calls require a generated project-scoped device token.
- The Ed25519 private signing key stays in ignored local state; agents fetch only its
  public verification key through their authenticated control-plane path.
- A digest or signature mismatch prevents activation.
- Candidate validation occurs before the active version changes; a failed candidate
  preserves the known-good active version.
- Restricted and `LOCAL_ONLY` requests never call the cloud fixture when local
  inference is unavailable.
- Telemetry carries operational metadata only, not raw input or output values.

Production additions not executed here include per-device certificates/mTLS, hardware
attestation, signing-key rotation, tenant credentials and a managed secret service.
