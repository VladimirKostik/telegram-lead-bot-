from .config import ADMIN_IDS


ALLOWED_STATUSES = {
    "NEW",
    "IN_PROGRESS",
    "DONE",
    "CANCELLED",
}


ALLOWED_TRANSITIONS = {
    "NEW": {
        "IN_PROGRESS",
        "CANCELLED",
    },
    "IN_PROGRESS": {
        "DONE",
        "CANCELLED",
    },
    "DONE": set(),
    "CANCELLED": set(),
}


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def can_transition_status(
    current_status: str,
    new_status: str,
) -> bool:
    if current_status not in ALLOWED_STATUSES:
        return False

    if new_status not in ALLOWED_STATUSES:
        return False

    return new_status in ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )


def can_modify_application(
    user_id: int,
    current_status: str,
    new_status: str,
) -> bool:
    if not is_admin(user_id):
        return False

    return can_transition_status(
        current_status=current_status,
        new_status=new_status,
    )


def can_access_application(
    user_id: int,
    owner_user_id: int,
) -> bool:
    return user_id == owner_user_id