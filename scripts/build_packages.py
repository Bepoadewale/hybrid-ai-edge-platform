from __future__ import annotations

from pathlib import Path

import onnx
from edge_platform.packaging import build_package, load_or_create_signer
from onnx import TensorProto, helper

root=Path(__file__).resolve().parents[1]; models=root/"models"/"packages"/"models"; models.mkdir(parents=True,exist_ok=True)
def model(path:Path,bias:float)->None:
    x=helper.make_tensor_value_info("input",TensorProto.FLOAT,[1,2]); y=helper.make_tensor_value_info("prediction",TensorProto.INT64,[1])
    weights=helper.make_tensor("weights",TensorProto.FLOAT,[2,2],[1.0,0.0,0.0,1.0]); b=helper.make_tensor("bias",TensorProto.FLOAT,[2],[bias,0.0])
    graph=helper.make_graph([helper.make_node("Gemm",["input","weights","bias"],["scores"]),helper.make_node("ArgMax",["scores"],["prediction"],axis=1,keepdims=0)],"tiny-classifier",[x],[y],[weights,b])
    proto=helper.make_model(graph,opset_imports=[helper.make_opsetid("",13)])
    proto.ir_version=13
    onnx.save(proto,path)
signer,public=load_or_create_signer(root/".local")
(root/".local"/"signing-public.pem").write_bytes(public)
for version,bias,memory,bad in [("v1",0.0,2048,False),("v2",0.2,8192,False),("v3",0.3,8192,True),("v4",0.4,8192,False)]:
    path=models/f"classifier-{version}.onnx"; model(path,bias); build_package(path,root/"models"/"packages"/f"classifier-{version}.zip",version=version,min_memory_mb=memory,bad_readiness=bad,signer=signer)
print("built signed ONNX packages: v1, v2, v3, v4")
