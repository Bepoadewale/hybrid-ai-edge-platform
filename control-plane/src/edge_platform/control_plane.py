"""Durable local fleet control plane and local cloud inference fixture."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel


class Registration(BaseModel):
    device_id: str
    profile: str
    capabilities: dict[str, Any]


class Heartbeat(BaseModel):
    active_version: str | None = None
    health: str = "ONLINE"
    online: bool = True
    activation: str = "NOT_INSTALLED"
    telemetry: list[dict[str, Any]] = []


class Desired(BaseModel):
    version: str | None


class Rollout(BaseModel):
    version: str
    stage: str
    device_ids: list[str]


class FleetStore:
    def __init__(self, database: str) -> None:
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(database, check_same_thread=False)
        self.lock = threading.RLock()
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS devices (device_id TEXT PRIMARY KEY, profile TEXT, capabilities TEXT, active_version TEXT, health TEXT, activation TEXT, last_seen REAL, desired_version TEXT);
        CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY, device_id TEXT, event TEXT, payload TEXT, created_at REAL);
        CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, event TEXT, device_id TEXT, detail TEXT, created_at REAL);
        CREATE TABLE IF NOT EXISTS rollouts (version TEXT, stage TEXT, device_ids TEXT, created_at REAL);
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        self.db.commit()

    def audit(self, event: str, device_id: str = "fleet", **detail: Any) -> None:
        with self.lock:
            self.db.execute("INSERT INTO audit(event,device_id,detail,created_at) VALUES(?,?,?,?)", (event, device_id, json.dumps(detail, sort_keys=True), time.time()))
            self.db.commit()

    def register(self, body: Registration) -> None:
        with self.lock:
            self.db.execute("""INSERT INTO devices(device_id,profile,capabilities,health,activation,last_seen)
            VALUES(?,?,?,?,?,?) ON CONFLICT(device_id) DO UPDATE SET profile=excluded.profile,capabilities=excluded.capabilities,last_seen=excluded.last_seen""", (body.device_id, body.profile, json.dumps(body.capabilities), "ONLINE", "NOT_INSTALLED", time.time()))
            self.db.commit(); self.audit("DEVICE_REGISTERED", body.device_id, profile=body.profile)

    def heartbeat(self, device_id: str, body: Heartbeat) -> None:
        with self.lock:
            self.db.execute("UPDATE devices SET active_version=?,health=?,activation=?,last_seen=? WHERE device_id=?", (body.active_version, body.health, body.activation, time.time(), device_id))
            for event in body.telemetry:
                self.db.execute("INSERT INTO telemetry(device_id,event,payload,created_at) VALUES(?,?,?,?)", (device_id, event.get("event", "INFERENCE"), json.dumps(event, sort_keys=True), time.time()))
            self.db.commit(); self.audit("DEVICE_HEARTBEAT", device_id, buffered=len(body.telemetry))

    def desired(self, device_id: str) -> str | None:
        with self.lock:
            row = self.db.execute("SELECT desired_version FROM devices WHERE device_id=?", (device_id,)).fetchone()
            if row and row["desired_version"]: return row["desired_version"]
            global_desired = self.db.execute("SELECT value FROM settings WHERE key='fleet_desired'").fetchone()
            return global_desired["value"] if global_desired else None

    def rollout(self, body: Rollout) -> None:
        with self.lock:
            for device_id in body.device_ids:
                self.db.execute("UPDATE devices SET desired_version=? WHERE device_id=?", (body.version, device_id))
            if body.stage in {"BASELINE", "EXPAND"}:
                self.db.execute("INSERT INTO settings(key,value) VALUES('fleet_desired',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (body.version,))
            self.db.execute("INSERT INTO rollouts VALUES(?,?,?,?)", (body.version, body.stage, json.dumps(body.device_ids), time.time()))
            self.db.commit(); self.audit("ROLLOUT_" + body.stage, detail={"version": body.version, "devices": body.device_ids})

    def devices(self) -> list[dict[str, Any]]:
        with self.lock: return [dict(row) for row in self.db.execute("SELECT * FROM devices ORDER BY device_id")]


def create_control_plane() -> FastAPI:
    root = Path(os.environ.get("EDGE_STATE_DIR", ".local"))
    store = FleetStore(str(root / "control-plane.db"))
    packages = Path(os.environ.get("EDGE_PACKAGES_DIR", "models/packages"))
    public_key = root / "signing-public.pem"
    device_token = os.environ.get("EDGE_DEVICE_TOKEN")
    app = FastAPI(title="Hybrid AI Edge Fleet Control Plane", version="0.2.0")

    def require_device_token(x_edge_device_token: str | None = Header(default=None)) -> None:
        if not device_token or x_edge_device_token != device_token:
            raise HTTPException(401, "invalid device identity token")

    @app.get("/healthz")
    def health() -> dict[str, str]: return {"status": "ok"}
    @app.post("/api/v1/devices/register")
    def register(body: Registration, _: None = Depends(require_device_token)) -> dict[str, str]: store.register(body); return {"status": "registered"}
    @app.post("/api/v1/devices/{device_id}/heartbeat")
    def heartbeat(device_id: str, body: Heartbeat, _: None = Depends(require_device_token)) -> dict[str, str]: store.heartbeat(device_id, body); return {"status": "recorded"}
    @app.get("/api/v1/devices/{device_id}/desired")
    def desired(device_id: str, _: None = Depends(require_device_token)) -> dict[str, str | None]: return {"version": store.desired(device_id)}
    @app.get("/api/v1/devices")
    def devices() -> dict[str, Any]: return {"devices": store.devices()}
    @app.get("/api/v1/audit")
    def audit() -> dict[str, Any]: return {"events": [dict(row) for row in store.db.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 100")]}
    @app.post("/api/v1/rollouts")
    def rollout(body: Rollout) -> dict[str, str]: store.rollout(body); return {"status": "assigned", "stage": body.stage}
    @app.get("/api/v1/packages/{version}")
    def package(version: str, _: None = Depends(require_device_token)) -> FileResponse:
        artifact = packages / f"classifier-{version}.zip"
        if not artifact.exists(): raise HTTPException(404, "unknown model package")
        return FileResponse(artifact, media_type="application/zip")
    @app.get("/api/v1/signing-key")
    def signing_key(_: None = Depends(require_device_token)) -> FileResponse:
        if not public_key.exists(): raise HTTPException(503, "signing key unavailable")
        return FileResponse(public_key, media_type="application/x-pem-file")
    @app.get("/api/v1/dashboard")
    def dashboard_data() -> dict[str, Any]:
        rows = store.devices(); counts = {"LOCAL": 0, "CLOUD": 0, "DENY": 0, "ROLLBACK": 0}
        for row in store.db.execute("SELECT event FROM telemetry"):
            event = row["event"]
            if event in counts: counts[event] += 1
        counts["ROLLBACK"] = sum(1 for row in rows if row["activation"] == "ROLLED_BACK")
        return {"devices": rows, "counts": counts, "simulated_hardware": True}
    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        return """<html><head><title>Hybrid AI Edge Fleet</title><style>body{background:#07111f;color:#e8f0fb;font:16px system-ui;margin:auto;max-width:1100px;padding:34px}.card{display:inline-block;vertical-align:top;background:#10213a;border:1px solid #28476b;border-radius:12px;padding:18px;margin:8px;min-width:170px}.n{font-size:32px;font-weight:800;color:#70b7ff}table{width:100%;border-collapse:collapse;background:#10213a;margin-top:18px}td,th{padding:12px;text-align:left;border-bottom:1px solid #28476b}.note{color:#a7bdd9}.ok{color:#44d49b}</style></head><body><h1>Hybrid AI Edge Fleet</h1><p class=note>Real local control-plane and agent evidence · auto-refreshes every 5 seconds</p><p class=note><b>SIMULATED HARDWARE:</b> profile memory, network, thermal and battery signals are inputs on one development machine. ONNX Runtime, signing, HTTP reconciliation, routing, and telemetry are real local behavior.</p><div id=c></div><table><thead><tr><th>Device</th><th>Profile</th><th>Desired</th><th>Active</th><th>Activation</th><th>Health</th></tr></thead><tbody id=t></tbody></table><script>async function r(){let d=await fetch('/api/v1/dashboard').then(x=>x.json()),c=d.counts;document.querySelector('#c').innerHTML=[['Devices',d.devices.length],['Local inference',c.LOCAL],['Cloud fallback',c.CLOUD],['Policy denials',c.DENY],['Rollbacks',c.ROLLBACK]].map(x=>`<div class=card><div class=n>${x[1]}</div><div>${x[0]}</div></div>`).join('');document.querySelector('#t').innerHTML=d.devices.map(x=>`<tr><td>${x.device_id}</td><td>${x.profile}</td><td>${x.desired_version||'—'}</td><td>${x.active_version||'—'}</td><td class=ok>${x.activation}</td><td>${x.health}</td></tr>`).join('')}r();setInterval(r,5000)</script></body></html>"""
    return app


def create_cloud_fixture() -> FastAPI:
    root = Path(os.environ.get("EDGE_PACKAGES_DIR", "models/packages"))
    app = FastAPI(title="Local Cloud Fallback Fixture")
    session: ort.InferenceSession | None = None
    @app.get("/healthz")
    def health() -> dict[str, str]: return {"status": "ok"}
    @app.post("/v1/infer")
    def infer(body: dict[str, Any]) -> dict[str, Any]:
        nonlocal session
        if session is None: session = ort.InferenceSession(str(root / "models" / "classifier-v2.onnx"), providers=["CPUExecutionProvider"])
        started=time.perf_counter(); output=session.run(None,{session.get_inputs()[0].name:np.array([body.get("input",[1.0,0.0])],dtype=np.float32)})[0].tolist()
        return {"prediction": output, "route":"CLOUD", "model":"cloud-classifier:v2", "latency_ms":round((time.perf_counter()-started)*1000,3)}
    return app
