from edge_platform.models import Route
from edge_platform.routing import choose_route


def test_all_routing_profiles_are_deterministic():
    assert choose_route(local_ready=True,online=True,classification="public",profile="LOCAL_ONLY") == Route.LOCAL
    assert choose_route(local_ready=False,online=True,classification="public",profile="LOCAL_ONLY") == Route.DENY
    assert choose_route(local_ready=True,online=True,classification="public",profile="LOCAL_PREFERRED") == Route.LOCAL
    assert choose_route(local_ready=False,online=True,classification="public",profile="LOCAL_PREFERRED") == Route.CLOUD
    assert choose_route(local_ready=True,online=True,classification="public",profile="CLOUD_PREFERRED") == Route.CLOUD
    assert choose_route(local_ready=True,online=True,classification="public",profile="CLOUD_ONLY") == Route.CLOUD
    assert choose_route(local_ready=False,online=True,classification="restricted",profile="PRIVACY_FIRST") == Route.DENY
