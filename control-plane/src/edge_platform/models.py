"""Shared durable contracts for the local hybrid edge platform."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Route(StrEnum):
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"
    DENY = "DENY"


class Activation(StrEnum):
    NOT_INSTALLED = "NOT_INSTALLED"
    VERIFYING = "VERIFYING"
    STAGED = "STAGED"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass(frozen=True)
class DeviceProfile:
    name: str
    architecture: str
    memory_mb: int
    storage_mb: int
    battery_powered: bool
    network: str
    thermal: str = "NORMAL"
    battery: str = "HIGH"
    onnx_providers: tuple[str, ...] = ("CPUExecutionProvider",)


@dataclass(frozen=True)
class ModelManifest:
    model: str
    version: str
    runtime: str
    architecture: tuple[str, ...]
    min_memory_mb: int
    package_size_bytes: int
    model_sha256: str
    signing_key_id: str
    readiness_failure: bool = False

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ModelManifest:
        return cls(
            model=value["model"], version=value["version"], runtime=value["runtime"],
            architecture=tuple(value["architecture"]), min_memory_mb=int(value["min_memory_mb"]),
            package_size_bytes=int(value["package_size_bytes"]), model_sha256=value["model_sha256"],
            signing_key_id=value["signing_key_id"], readiness_failure=bool(value.get("readiness_failure", False)),
        )


def compatibility(profile: DeviceProfile, manifest: ModelManifest) -> str:
    if profile.architecture not in manifest.architecture:
        return "INCOMPATIBLE_ARCHITECTURE"
    if profile.memory_mb < manifest.min_memory_mb:
        return "INSUFFICIENT_MEMORY"
    if profile.storage_mb * 1024 * 1024 < manifest.package_size_bytes:
        return "INSUFFICIENT_STORAGE"
    if manifest.runtime != "onnxruntime" or "CPUExecutionProvider" not in profile.onnx_providers:
        return "UNSUPPORTED_RUNTIME"
    return "COMPATIBLE"
