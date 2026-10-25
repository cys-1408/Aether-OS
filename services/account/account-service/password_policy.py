"""Password policy shared by firstboot, settings and the installer."""
from user_create import password_score, validate_password  # noqa: F401


def policy() -> dict:
    return {"min_length": 8, "reject_common": True, "recommended_score": 3, "max_score": 5}
