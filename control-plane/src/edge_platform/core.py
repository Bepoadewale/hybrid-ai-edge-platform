from dataclasses import dataclass
from enum import StrEnum
class Route(StrEnum): LOCAL="LOCAL"; CLOUD="CLOUD"; DENY="DENY"
class Activation(StrEnum): NOT_INSTALLED="NOT_INSTALLED"; VERIFYING="VERIFYING"; STAGED="STAGED"; ACTIVE="ACTIVE"; FAILED="FAILED"; ROLLED_BACK="ROLLED_BACK"
@dataclass
class Device: id:str; profile:str; ram_mb:int; storage_mb:int; online:bool=True; local_model:str|None=None
@dataclass
class Model: name:str; version:str; min_ram_mb:int; size_mb:int; digest:str
def compatible(device:Device,model:Model)->str:
 if device.ram_mb<model.min_ram_mb:return "INSUFFICIENT_MEMORY"
 if device.storage_mb<model.size_mb:return "INSUFFICIENT_STORAGE"
 return "COMPATIBLE"
def route(device:Device,model:Model,classification:str,profile:str)->Route:
 local=compatible(device,model)=="COMPATIBLE" and device.local_model==model.version
 if profile=="LOCAL_ONLY" or classification=="restricted":return Route.LOCAL if local else Route.DENY
 if local and profile!="CLOUD_ONLY":return Route.LOCAL
 return Route.CLOUD if device.online else Route.DENY
def reconcile(device:Device,model:Model,observed_digest:str)->Activation:
 if compatible(device,model)!="COMPATIBLE" or observed_digest!=model.digest:return Activation.FAILED
 device.local_model=model.version; return Activation.ACTIVE
