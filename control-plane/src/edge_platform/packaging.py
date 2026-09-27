"""Build and verify Ed25519-signed, zip-based model packages."""
from __future__ import annotations

import base64
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from edge_platform.models import ModelManifest


def canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_or_create_signer(directory: Path) -> tuple[Ed25519PrivateKey, bytes]:
    directory.mkdir(parents=True, exist_ok=True)
    private_path = directory / "signing-private.pem"
    public_path = directory / "signing-public.pem"
    if private_path.exists():
        private = serialization.load_pem_private_key(private_path.read_bytes(), password=None)
        if not isinstance(private, Ed25519PrivateKey):
            raise TypeError("local model signer must be Ed25519")
    else:
        private = Ed25519PrivateKey.generate()
        private_path.write_bytes(private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        private_path.chmod(0o600)
        public_path.write_bytes(private.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    return private, public_path.read_bytes()


def build_package(model_path: Path, destination: Path, *, version: str, min_memory_mb: int, bad_readiness: bool, signer: Ed25519PrivateKey) -> dict[str, Any]:
    model_bytes = model_path.read_bytes()
    manifest = {
        "model": "classifier", "version": version, "runtime": "onnxruntime", "architecture": ["x86_64", "arm64"],
        "min_memory_mb": min_memory_mb, "package_size_bytes": len(model_bytes), "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "signing_key_id": "local-ed25519-v1", "readiness_failure": bad_readiness,
    }
    signature = base64.b64encode(signer.sign(canonical(manifest))).decode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", canonical(manifest))
        archive.writestr("metadata.json", json.dumps({"input": "float32[1,2]", "output": "int64[1]"}))
        archive.writestr("signature", signature)
        archive.writestr("model.onnx", model_bytes)
    return manifest


def verify_package(package: Path, public_pem: bytes, destination: Path) -> ModelManifest:
    public_key = serialization.load_pem_public_key(public_pem)
    if not isinstance(public_key, Ed25519PublicKey):
        raise TypeError("model verification key must be Ed25519")
    with zipfile.ZipFile(package) as archive:
        manifest_raw = archive.read("manifest.json")
        manifest_dict = json.loads(manifest_raw)
        public_key.verify(base64.b64decode(archive.read("signature")), canonical(manifest_dict))
        model = archive.read("model.onnx")
        if hashlib.sha256(model).hexdigest() != manifest_dict["model_sha256"]:
            raise ValueError("model digest mismatch")
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "model.onnx").write_bytes(model)
        (destination / "manifest.json").write_bytes(canonical(manifest_dict))
    return ModelManifest.from_dict(manifest_dict)
