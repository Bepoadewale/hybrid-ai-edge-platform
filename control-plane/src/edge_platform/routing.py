from __future__ import annotations

from edge_platform.models import Route


def choose_route(*, local_ready: bool, online: bool, classification: str, profile: str) -> Route:
    privacy = classification == "restricted" or profile in {"LOCAL_ONLY", "PRIVACY_FIRST"}
    if privacy: return Route.LOCAL if local_ready else Route.DENY
    if profile == "CLOUD_ONLY": return Route.CLOUD if online else Route.DENY
    if profile == "CLOUD_PREFERRED": return Route.CLOUD if online else (Route.LOCAL if local_ready else Route.DENY)
    if local_ready: return Route.LOCAL
    return Route.CLOUD if online else Route.DENY
