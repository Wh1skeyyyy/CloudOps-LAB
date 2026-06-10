from urllib.parse import urlparse

from app.utils.errors import APIError


def require_fields(data: dict, fields: list[str]) -> None:
    """Raise APIError if any of the listed fields is missing or blank."""
    missing = []
    for f in fields:
        v = data.get(f)
        if v is None or (isinstance(v, str) and not v.strip()):
            missing.append(f)
    if missing:
        raise APIError(f"Missing required fields: {', '.join(missing)}")


def validate_enum(value, allowed, field_name: str) -> None:
    """Raise APIError if the value is provided and not in the allowed set."""
    if value is not None and value not in allowed:
        raise APIError(f"{field_name} must be one of: {', '.join(allowed)}")


def validate_url(value, field_name: str) -> None:
    """Raise APIError if the value is provided and not a valid http(s) URL."""
    if value is None or value == "":
        return
    try:
        parsed = urlparse(value)
    except (TypeError, ValueError):
        raise APIError(f"{field_name} must be a valid http(s) URL")
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise APIError(f"{field_name} must be a valid http(s) URL")
