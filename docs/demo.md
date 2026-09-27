# Demo guide

Start from a clean project state:

```bash
make install
make bootstrap-local
make smoke
```

Use `make demo-fleet` for actual local inference, allowed fallback and privacy denial.
Use `make demo-rollout` for a staged compatible rollout and offline-device return.
Use `make demo-bad-rollout` for a valid candidate that fails readiness and retains v2,
`make demo-tamper` for post-signing corruption rejection, and `make demo-offline` for
offline local inference with telemetry buffering and reconnection.

The running dashboard is at `http://localhost:18100/`. It reports aggregate device,
route and rollback evidence without raw inference data.

Remove only resources created by this repository with `make clean-local`.
