from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import pytest
from edge_platform.models import DeviceProfile, compatibility
from edge_platform.packaging import build_package, load_or_create_signer, verify_package
from onnx import TensorProto, helper


def tiny_model(path: Path) -> None:
    input_info = helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 2])
    output_info = helper.make_tensor_value_info("prediction", TensorProto.INT64, [1])
    weights = helper.make_tensor("weights", TensorProto.FLOAT, [2, 2], [1.0, 0.0, 0.0, 1.0])
    graph = helper.make_graph([helper.make_node("ArgMax", ["input"], ["prediction"], axis=1, keepdims=0)], "test", [input_info], [output_info], [weights])
    proto = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    proto.ir_version = 13
    onnx.save(proto, path)


def test_signed_package_verifies_and_onnx_runtime_executes(tmp_path: Path) -> None:
    model = tmp_path / "model.onnx"; tiny_model(model)
    signer, public = load_or_create_signer(tmp_path / "keys")
    package = tmp_path / "classifier-v2.zip"
    build_package(model, package, version="v2", min_memory_mb=8192, bad_readiness=False, signer=signer)
    manifest = verify_package(package, public, tmp_path / "installed")
    session = ort.InferenceSession(str(tmp_path / "installed" / "model.onnx"), providers=["CPUExecutionProvider"])
    assert session.run(None, {"input": np.array([[0.0, 1.0]], dtype=np.float32)})[0].tolist() == [1]
    assert compatibility(DeviceProfile("high", "x86_64", 16384, 1000, False, "FAST"), manifest) == "COMPATIBLE"
    assert compatibility(DeviceProfile("low", "x86_64", 4096, 1000, False, "FAST"), manifest) == "INSUFFICIENT_MEMORY"


def test_tampered_signed_model_is_rejected(tmp_path: Path) -> None:
    model = tmp_path / "model.onnx"; tiny_model(model)
    signer, public = load_or_create_signer(tmp_path / "keys")
    package = tmp_path / "classifier-v2.zip"; build_package(model, package, version="v2", min_memory_mb=1, bad_readiness=False, signer=signer)
    altered = tmp_path / "altered.zip"
    with zipfile.ZipFile(package) as source, zipfile.ZipFile(altered, "w") as target:
        for name in source.namelist(): target.writestr(name, source.read(name) + b"x" if name == "model.onnx" else source.read(name))
    with pytest.raises(ValueError, match="digest mismatch"):
        verify_package(altered, public, tmp_path / "installed")
