"""Independent edge-agent process: reconciliation, signed activation and hybrid routing."""
from __future__ import annotations

import argparse
import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort
import uvicorn
from edge_platform.models import Activation, DeviceProfile, Route, compatibility
from edge_platform.packaging import verify_package
from edge_platform.routing import choose_route
from fastapi import FastAPI, HTTPException

PROFILES = {
    "laptop-high": DeviceProfile("laptop-high", "x86_64", 16384, 51200, False, "FAST"),
    "mobile-high": DeviceProfile("mobile-high", "arm64", 8192, 16384, True, "FLAKY"),
    "mobile-low": DeviceProfile("mobile-low", "arm64", 4096, 4096, True, "INTERMITTENT"),
    "edge-gateway": DeviceProfile("edge-gateway", "x86_64", 8192, 32768, False, "FAST"),
    "offline-simulated": DeviceProfile("offline-simulated", "x86_64", 8192, 16384, False, "OFFLINE"),
}


def _json(url: str, data: dict[str, Any] | None = None, token: str | None = None) -> dict[str, Any]:
    request = urllib.request.Request(url, method="POST" if data is not None else "GET")
    if data is not None:
        request.data = json.dumps(data).encode(); request.add_header("Content-Type", "application/json")
    if token: request.add_header("X-Edge-Device-Token", token)
    with urllib.request.urlopen(request, timeout=3) as response:
        return json.loads(response.read())


class DeviceAgent:
    def __init__(self, device_id: str, profile: DeviceProfile, control_plane: str, cloud: str, state: Path, online: bool = True) -> None:
        self.id, self.profile, self.control_plane, self.cloud, self.state, self.online = device_id, profile, control_plane.rstrip("/"), cloud.rstrip("/"), state, online
        self.state.mkdir(parents=True, exist_ok=True); (self.state / "models").mkdir(exist_ok=True)
        self.active: str | None = self._read("active-version"); self.previous: str | None = self._read("previous-version")
        self.activation = Activation.ACTIVE if self.active else Activation.NOT_INSTALLED
        self.buffer: list[dict[str, Any]] = json.loads((self.state / "telemetry.json").read_text()) if (self.state / "telemetry.json").exists() else []
        self.session: ort.InferenceSession | None = None
        self.reconcile_lock = threading.Lock()
        self.token = os.environ.get("EDGE_DEVICE_TOKEN")
        if self.active: self._load_active()

    def _read(self, name: str) -> str | None:
        path = self.state / name
        return path.read_text().strip() if path.exists() else None
    def _write(self, name: str, value: str) -> None: (self.state / name).write_text(value)
    def _record(self, event: str, **data: Any) -> None:
        self.buffer.append({"event":event,"device_id":self.id,"at":time.time(),**data})
        self.buffer=self.buffer[-100:]; (self.state / "telemetry.json").write_text(json.dumps(self.buffer))
    def _load_active(self) -> None:
        if self.active:
            self.session=ort.InferenceSession(str(self.state / "models" / self.active / "model.onnx"),providers=["CPUExecutionProvider"])

    def register(self) -> None:
        if not self.online: return
        _json(self.control_plane+"/api/v1/devices/register", {"device_id":self.id,"profile":self.profile.name,"capabilities":{"architecture":self.profile.architecture,"memory_mb":self.profile.memory_mb,"storage_mb":self.profile.storage_mb,"onnx_providers":list(self.profile.onnx_providers),"network":"SIMULATED_"+self.profile.network,"battery":"SIMULATED_"+self.profile.battery,"thermal":"SIMULATED_"+self.profile.thermal}}, self.token)

    def heartbeat(self) -> None:
        if not self.online: return
        queued=list(self.buffer)
        _json(self.control_plane+f"/api/v1/devices/{self.id}/heartbeat", {"active_version":self.active,"health":"ONLINE","activation":self.activation,"online":True,"telemetry":queued}, self.token)
        self.buffer=[]; (self.state / "telemetry.json").write_text("[]")

    def reconcile(self) -> str:
        if not self.reconcile_lock.acquire(blocking=False): return "BUSY"
        try:
            return self._reconcile_once()
        finally:
            self.reconcile_lock.release()

    def _reconcile_once(self) -> str:
        if not self.online: return "OFFLINE"
        try:
            desired=_json(self.control_plane+f"/api/v1/devices/{self.id}/desired", token=self.token)["version"]
            if not desired or desired == self.active: self.heartbeat(); return "CURRENT"
            return self._install(desired)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            self._record("CONTROL_PLANE_UNAVAILABLE", error=type(exc).__name__); return "DEFERRED"

    def _install(self, version: str) -> str:
        self.activation=Activation.VERIFYING; staging=self.state / "candidate.zip"; extracted=self.state / "models" / version
        try:
            package_request=urllib.request.Request(self.control_plane+f"/api/v1/packages/{version}", headers={"X-Edge-Device-Token": self.token or ""})
            key_request=urllib.request.Request(self.control_plane+"/api/v1/signing-key", headers={"X-Edge-Device-Token": self.token or ""})
            with urllib.request.urlopen(package_request,timeout=5) as response: staging.write_bytes(response.read())
            public=urllib.request.urlopen(key_request,timeout=3).read()
            manifest=verify_package(staging,public,extracted)
            result=compatibility(self.profile,manifest)
            if result!="COMPATIBLE": self.activation=Activation.FAILED; self._record("INCOMPATIBLE",version=version,reason=result); self.heartbeat(); return result
            self.activation=Activation.STAGED
            candidate=ort.InferenceSession(str(extracted / "model.onnx"),providers=["CPUExecutionProvider"])
            candidate.run(None,{candidate.get_inputs()[0].name:np.array([[1.0,0.0]],dtype=np.float32)})
            if manifest.readiness_failure: raise RuntimeError("intentional readiness gate failure")
            self.previous=self.active
            if self.previous: self._write("previous-version",self.previous)
            self.active=version; self._write("active-version",version); self.session=candidate; self.activation=Activation.ACTIVE
            self._record("MODEL_ACTIVATED",version=version); self.heartbeat(); return "ACTIVE"
        except (OSError, RuntimeError, ValueError, urllib.error.URLError) as exc:
            # The candidate never replaces the active symlink/state before readiness succeeds.
            # A rejected package therefore preserves the current known-good version.
            self.activation=Activation.ROLLED_BACK if self.active else Activation.FAILED
            if self.active: self._load_active()
            self._record("MODEL_VERIFICATION_OR_READINESS_FAILED",version=version,error=type(exc).__name__); self.heartbeat(); return "ROLLED_BACK"

    def infer(self, input_values: list[float], classification: str, routing_profile: str, required_version: str | None = None) -> dict[str, Any]:
        local_ready=self.session is not None and (required_version is None or self.active==required_version)
        decision=choose_route(local_ready=local_ready,online=self.online,classification=classification,profile=routing_profile)
        if decision == Route.LOCAL:
            started=time.perf_counter(); output=self.session.run(None,{self.session.get_inputs()[0].name:np.array([input_values],dtype=np.float32)})[0].tolist(); latency=round((time.perf_counter()-started)*1000,3)
            result={"prediction":output,"route":Route.LOCAL,"reason":"local_model_available","model":f"classifier:{self.active}","latency_ms":latency,"provider":"CPUExecutionProvider"}; self._record("LOCAL",latency_ms=latency,model=self.active); return result
        if decision == Route.DENY:
            self._record("DENY",reason="privacy_or_offline",classification=classification); raise HTTPException(403,"cloud fallback denied by privacy policy or offline state")
        try:
            cloud=_json(self.cloud+"/v1/infer",{"input":input_values}); self._record("CLOUD",latency_ms=cloud["latency_ms"],reason="local_model_unavailable"); return cloud | {"reason":"local_model_unavailable","device_id":self.id}
        except (OSError, RuntimeError, ValueError, urllib.error.URLError) as exc:
            self._record("DENY",reason="cloud_unavailable"); raise HTTPException(503,f"cloud fallback unavailable: {type(exc).__name__}") from exc


def create_agent_app(agent: DeviceAgent) -> FastAPI:
    app=FastAPI(title=f"Hybrid Edge Agent {agent.id}")
    @app.get("/healthz")
    def health() -> dict[str, Any]: return {"status":"ok","device_id":agent.id,"active_version":agent.active,"activation":agent.activation}
    @app.get("/state")
    def state() -> dict[str, Any]: return {"device_id":agent.id,"profile":agent.profile.name,"active":agent.active,"previous":agent.previous,"activation":agent.activation,"online":agent.online,"telemetry_buffered":len(agent.buffer)}
    @app.post("/v1/infer")
    def infer(body: dict[str, Any]) -> dict[str, Any]: return agent.infer(body.get("input",[1.0,0.0]),body.get("data_classification","public"),body.get("routing_profile","LOCAL_PREFERRED"),body.get("required_version"))
    @app.post("/admin/online")
    def online(body: dict[str, Any]) -> dict[str, bool]:
        agent.online=bool(body["online"])
        if agent.online: agent.register()
        return {"online":agent.online}
    @app.post("/admin/reconcile")
    def reconcile() -> dict[str,str]: return {"result":agent.reconcile()}
    return app


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--id",required=True); parser.add_argument("--profile",required=True,choices=PROFILES); parser.add_argument("--port",type=int,required=True); parser.add_argument("--state",required=True); parser.add_argument("--control-plane",default="http://127.0.0.1:18100"); parser.add_argument("--cloud",default="http://127.0.0.1:18101"); parser.add_argument("--offline",action="store_true"); args=parser.parse_args()
    agent=DeviceAgent(args.id,PROFILES[args.profile],args.control_plane,args.cloud,Path(args.state),not args.offline)
    if not args.offline: agent.register(); agent.reconcile()
    def loop() -> None:
        while True: agent.reconcile(); time.sleep(1)
    threading.Thread(target=loop,daemon=True).start(); uvicorn.run(create_agent_app(agent),host="127.0.0.1",port=args.port)


if __name__=="__main__": main()
