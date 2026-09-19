from edge_platform.core import Activation, Device, Model, Route, compatible, reconcile, route
def model():return Model("classifier","v2",8192,12,"good")
def test_heterogeneous_compatibility():assert compatible(Device("low","mobile-low",4096,4096),model())=="INSUFFICIENT_MEMORY"
def test_privacy_overrides_cloud_availability():assert route(Device("low","mobile-low",4096,4096),model(),"restricted","LOCAL_PREFERRED")==Route.DENY
def test_cloud_fallback_and_offline_denial():
 assert route(Device("x","low",4096,4096),model(),"public","LOCAL_PREFERRED")==Route.CLOUD
 assert route(Device("x","low",4096,4096,False),model(),"public","LOCAL_PREFERRED")==Route.DENY
def test_reconciliation_fails_tampered_package():
 d=Device("x","high",16384,1000); assert reconcile(d,model(),"bad")==Activation.FAILED; assert reconcile(d,model(),"good")==Activation.ACTIVE
