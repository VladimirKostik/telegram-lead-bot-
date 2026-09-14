from app.security import (
    can_access_application,
    can_modify_application,
    can_transition_status,
    is_admin,
)


ADMIN_ID = 8409425334
USER_ID = 999999999


def test_admin_is_recognized():
    assert is_admin(ADMIN_ID) is True


def test_regular_user_is_not_admin():
    assert is_admin(USER_ID) is False


def test_new_can_move_to_in_progress():
    assert can_transition_status(
        current_status="NEW",
        new_status="IN_PROGRESS",
    ) is True


def test_new_can_be_cancelled():
    assert can_transition_status(
        current_status="NEW",
        new_status="CANCELLED",
    ) is True


def test_in_progress_can_move_to_done():
    assert can_transition_status(
        current_status="IN_PROGRESS",
        new_status="DONE",
    ) is True


def test_in_progress_can_be_cancelled():
    assert can_transition_status(
        current_status="IN_PROGRESS",
        new_status="CANCELLED",
    ) is True


def test_done_is_final():
    assert can_transition_status(
        current_status="DONE",
        new_status="IN_PROGRESS",
    ) is False

    assert can_transition_status(
        current_status="DONE",
        new_status="CANCELLED",
    ) is False

    assert can_transition_status(
        current_status="DONE",
        new_status="NEW",
    ) is False


def test_cancelled_is_final():
    assert can_transition_status(
        current_status="CANCELLED",
        new_status="NEW",
    ) is False

    assert can_transition_status(
        current_status="CANCELLED",
        new_status="IN_PROGRESS",
    ) is False

    assert can_transition_status(
        current_status="CANCELLED",
        new_status="DONE",
    ) is False


def test_in_progress_cannot_return_to_new():
    assert can_transition_status(
        current_status="IN_PROGRESS",
        new_status="NEW",
    ) is False


def test_done_cannot_be_modified_by_admin():
    assert can_modify_application(
        user_id=ADMIN_ID,
        current_status="DONE",
        new_status="IN_PROGRESS",
    ) is False


def test_cancelled_cannot_be_modified_by_admin():
    assert can_modify_application(
        user_id=ADMIN_ID,
        current_status="CANCELLED",
        new_status="DONE",
    ) is False


def test_regular_user_cannot_modify_application():
    assert can_modify_application(
        user_id=USER_ID,
        current_status="NEW",
        new_status="IN_PROGRESS",
    ) is False


def test_admin_can_modify_new_application():
    assert can_modify_application(
        user_id=ADMIN_ID,
        current_status="NEW",
        new_status="IN_PROGRESS",
    ) is True


def test_admin_can_cancel_new_application():
    assert can_modify_application(
        user_id=ADMIN_ID,
        current_status="NEW",
        new_status="CANCELLED",
    ) is True


def test_admin_can_complete_in_progress_application():
    assert can_modify_application(
        user_id=ADMIN_ID,
        current_status="IN_PROGRESS",
        new_status="DONE",
    ) is True


def test_admin_can_cancel_in_progress_application():
    assert can_modify_application(
        user_id=ADMIN_ID,
        current_status="IN_PROGRESS",
        new_status="CANCELLED",
    ) is True


def test_owner_can_access_application():
    assert can_access_application(
        user_id=USER_ID,
        owner_user_id=USER_ID,
    ) is True


def test_foreign_user_cannot_access_application():
    assert can_access_application(
        user_id=USER_ID,
        owner_user_id=ADMIN_ID,
    ) is False