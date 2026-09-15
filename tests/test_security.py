import pytest

from app.security import (
    ALLOWED_STATUSES,
    ALLOWED_TRANSITIONS,
    can_access_application,
    can_modify_application,
    can_transition_status,
    is_admin,
)


# ============================================================
# STATUS SET
# ============================================================


def test_all_expected_statuses_exist():
    assert ALLOWED_STATUSES == {
        "NEW",
        "IN_PROGRESS",
        "DONE",
        "CANCELLED",
    }


def test_new_status_has_expected_transitions():
    assert ALLOWED_TRANSITIONS["NEW"] == {
        "IN_PROGRESS",
        "CANCELLED",
    }


def test_in_progress_status_has_expected_transitions():
    assert ALLOWED_TRANSITIONS["IN_PROGRESS"] == {
        "DONE",
        "CANCELLED",
    }


def test_done_is_terminal():
    assert ALLOWED_TRANSITIONS["DONE"] == set()


def test_cancelled_is_terminal():
    assert ALLOWED_TRANSITIONS["CANCELLED"] == set()


# ============================================================
# STATUS TRANSITIONS — ALLOWED
# ============================================================


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        ("NEW", "IN_PROGRESS"),
        ("NEW", "CANCELLED"),
        ("IN_PROGRESS", "DONE"),
        ("IN_PROGRESS", "CANCELLED"),
    ],
)
def test_allowed_status_transitions(current_status, new_status):
    assert can_transition_status(
        current_status=current_status,
        new_status=new_status,
    ) is True


# ============================================================
# STATUS TRANSITIONS — FORBIDDEN
# ============================================================


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        ("NEW", "NEW"),
        ("IN_PROGRESS", "NEW"),
        ("IN_PROGRESS", "IN_PROGRESS"),
        ("DONE", "NEW"),
        ("DONE", "IN_PROGRESS"),
        ("DONE", "CANCELLED"),
        ("DONE", "DONE"),
        ("CANCELLED", "NEW"),
        ("CANCELLED", "IN_PROGRESS"),
        ("CANCELLED", "DONE"),
        ("CANCELLED", "CANCELLED"),
    ],
)
def test_forbidden_status_transitions(current_status, new_status):
    assert can_transition_status(
        current_status=current_status,
        new_status=new_status,
    ) is False


# ============================================================
# INVALID STATUSES
# ============================================================


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        ("UNKNOWN", "DONE"),
        ("NEW", "UNKNOWN"),
        ("UNKNOWN", "UNKNOWN"),
        ("", "DONE"),
        ("NEW", ""),
        ("new", "IN_PROGRESS"),
        ("IN_PROGRESS", "done"),
    ],
)
def test_invalid_statuses_are_rejected(current_status, new_status):
    assert can_transition_status(
        current_status=current_status,
        new_status=new_status,
    ) is False


# ============================================================
# ADMIN AUTHORIZATION
# ============================================================


def test_configured_admin_is_admin():
    configured_admin_ids = list(__import__("app.config", fromlist=["ADMIN_IDS"]).ADMIN_IDS)

    if not configured_admin_ids:
        pytest.skip("No ADMIN_IDS configured in environment.")

    assert is_admin(configured_admin_ids[0]) is True


def test_unknown_user_is_not_admin():
    configured_admin_ids = __import__(
        "app.config",
        fromlist=["ADMIN_IDS"],
    ).ADMIN_IDS

    unknown_user_id = 999999999999999

    while unknown_user_id in configured_admin_ids:
        unknown_user_id += 1

    assert is_admin(unknown_user_id) is False


def test_zero_is_not_admin():
    assert is_admin(0) is False


def test_negative_id_is_not_admin():
    assert is_admin(-1) is False


# ============================================================
# APPLICATION ACCESS / OWNERSHIP
# ============================================================


def test_owner_can_access_application():
    assert can_access_application(
        user_id=100,
        owner_user_id=100,
    ) is True


def test_foreign_user_cannot_access_application():
    assert can_access_application(
        user_id=100,
        owner_user_id=200,
    ) is False


def test_same_user_id_is_required_for_access():
    assert can_access_application(
        user_id=123456,
        owner_user_id=123457,
    ) is False


# ============================================================
# ADMIN APPLICATION MODIFICATION
# ============================================================


def test_non_admin_cannot_modify_application(monkeypatch):
    monkeypatch.setattr(
        "app.security.is_admin",
        lambda user_id: False,
    )

    assert can_modify_application(
        user_id=100,
        current_status="NEW",
        new_status="IN_PROGRESS",
    ) is False


def test_admin_can_modify_application_with_valid_transition(monkeypatch):
    monkeypatch.setattr(
        "app.security.is_admin",
        lambda user_id: True,
    )

    assert can_modify_application(
        user_id=100,
        current_status="NEW",
        new_status="IN_PROGRESS",
    ) is True


def test_admin_can_cancel_new_application(monkeypatch):
    monkeypatch.setattr(
        "app.security.is_admin",
        lambda user_id: True,
    )

    assert can_modify_application(
        user_id=100,
        current_status="NEW",
        new_status="CANCELLED",
    ) is True


def test_admin_can_complete_in_progress_application(monkeypatch):
    monkeypatch.setattr(
        "app.security.is_admin",
        lambda user_id: True,
    )

    assert can_modify_application(
        user_id=100,
        current_status="IN_PROGRESS",
        new_status="DONE",
    ) is True


def test_admin_can_cancel_in_progress_application(monkeypatch):
    monkeypatch.setattr(
        "app.security.is_admin",
        lambda user_id: True,
    )

    assert can_modify_application(
        user_id=100,
        current_status="IN_PROGRESS",
        new_status="CANCELLED",
    ) is True


# ============================================================
# ADMIN FORBIDDEN TRANSITIONS
# ============================================================


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        ("IN_PROGRESS", "NEW"),
        ("DONE", "NEW"),
        ("DONE", "IN_PROGRESS"),
        ("DONE", "CANCELLED"),
        ("CANCELLED", "NEW"),
        ("CANCELLED", "IN_PROGRESS"),
        ("CANCELLED", "DONE"),
    ],
)
def test_admin_cannot_make_forbidden_transition(
    monkeypatch,
    current_status,
    new_status,
):
    monkeypatch.setattr(
        "app.security.is_admin",
        lambda user_id: True,
    )

    assert can_modify_application(
        user_id=100,
        current_status=current_status,
        new_status=new_status,
    ) is False


# ============================================================
# TERMINAL STATUS PROTECTION
# ============================================================


@pytest.mark.parametrize(
    "terminal_status",
    [
        "DONE",
        "CANCELLED",
    ],
)
@pytest.mark.parametrize(
    "new_status",
    [
        "NEW",
        "IN_PROGRESS",
        "DONE",
        "CANCELLED",
    ],
)
def test_terminal_status_cannot_be_changed(
    monkeypatch,
    terminal_status,
    new_status,
):
    monkeypatch.setattr(
        "app.security.is_admin",
        lambda user_id: True,
    )

    assert can_modify_application(
        user_id=100,
        current_status=terminal_status,
        new_status=new_status,
    ) is False


# ============================================================
# FINAL SECURITY INVARIANTS
# ============================================================


def test_regular_user_cannot_change_even_valid_transition(monkeypatch):
    monkeypatch.setattr(
        "app.security.is_admin",
        lambda user_id: False,
    )

    valid_transitions = [
        ("NEW", "IN_PROGRESS"),
        ("NEW", "CANCELLED"),
        ("IN_PROGRESS", "DONE"),
        ("IN_PROGRESS", "CANCELLED"),
    ]

    for current_status, new_status in valid_transitions:
        assert can_modify_application(
            user_id=100,
            current_status=current_status,
            new_status=new_status,
        ) is False


def test_access_requires_exact_owner_id():
    owner_id = 8409425334

    assert can_access_application(
        user_id=owner_id,
        owner_user_id=owner_id,
    ) is True

    assert can_access_application(
        user_id=owner_id + 1,
        owner_user_id=owner_id,
    ) is False


def test_status_transition_function_does_not_allow_partial_matches():
    assert can_transition_status(
        current_status="NEW",
        new_status="IN_PROGRESS_EXTRA",
    ) is False

    assert can_transition_status(
        current_status="IN_PROGRESS_EXTRA",
        new_status="DONE",
    ) is False


def test_status_transition_is_case_sensitive():
    assert can_transition_status(
        current_status="new",
        new_status="IN_PROGRESS",
    ) is False

    assert can_transition_status(
        current_status="NEW",
        new_status="in_progress",
    ) is False