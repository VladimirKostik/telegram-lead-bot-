import asyncio

from sqlalchemy import select

from .database import get_session
from .models import Application, User
from .repositories import get_user_application_by_public_number


async def main():
    async with get_session() as session:
        users_result = await session.execute(
            select(User)
            .order_by(User.id.asc())
        )

        users = list(users_result.scalars().all())

        if len(users) < 2:
            print(
                "SECURITY TEST SKIPPED: "
                "need at least 2 users."
            )
            return

        first_user = users[0]
        second_user = users[1]

        application_result = await session.execute(
            select(Application)
            .where(Application.user_id == first_user.id)
            .order_by(Application.id.asc())
        )

        first_user_application = (
            application_result.scalars().first()
        )

        if first_user_application is None:
            print(
                "SECURITY TEST SKIPPED: "
                "first user has no applications."
            )
            return

        result_for_owner = await get_user_application_by_public_number(
            session=session,
            telegram_id=first_user.telegram_id,
            public_number=first_user_application.public_number,
        )

        result_for_other_user = await get_user_application_by_public_number(
            session=session,
            telegram_id=second_user.telegram_id,
            public_number=first_user_application.public_number,
        )

        print("=" * 60)
        print("IDOR SECURITY TEST")
        print("=" * 60)

        print(
            "Owner access:",
            "PASS" if result_for_owner is not None else "FAIL",
        )

        print(
            "Foreign user access:",
            "PASS" if result_for_other_user is None else "FAIL",
        )

        print(
            "Internal DB ID:",
            first_user_application.id,
        )

        print(
            "Public number:",
            first_user_application.public_number,
        )

        print("=" * 60)

        if result_for_owner is None:
            raise AssertionError(
                "Owner must be able to access own application."
            )

        if result_for_other_user is not None:
            raise AssertionError(
                "IDOR detected: "
                "foreign user accessed another user's application."
            )

        print("SECURITY TEST PASSED.")


if __name__ == "__main__":
    asyncio.run(main())