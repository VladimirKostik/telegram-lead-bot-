import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Application, User
from ..security import can_transition_status


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
) -> User:
    result = await session.execute(
        select(User).where(
            User.telegram_id == telegram_id
        )
    )

    user = result.scalar_one_or_none()

    if user is not None:
        return user

    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
    )

    session.add(user)

    await session.flush()

    return user


async def generate_public_number(
    session: AsyncSession,
) -> int:
    while True:
        public_number = secrets.randbelow(900000) + 100000

        result = await session.execute(
            select(Application.id).where(
                Application.public_number == public_number
            )
        )

        if result.scalar_one_or_none() is None:
            return public_number


async def create_application(
    session: AsyncSession,
    user: User,
    name: str,
    phone: str,
    service: str,
    comment: str | None,
) -> Application:
    public_number = await generate_public_number(session)

    application = Application(
        public_number=public_number,
        user_id=user.id,
        name=name,
        phone=phone,
        service=service,
        comment=comment,
        status="NEW",
    )

    session.add(application)

    await session.flush()

    return application


async def get_user_applications(
    session: AsyncSession,
    telegram_id: int,
) -> list[Application]:
    result = await session.execute(
        select(Application)
        .join(User)
        .where(
            User.telegram_id == telegram_id
        )
        .order_by(
            Application.created_at.desc()
        )
    )

    return list(result.scalars().all())


async def get_new_applications(
    session: AsyncSession,
) -> list[Application]:
    result = await session.execute(
        select(Application)
        .where(
            Application.status == "NEW"
        )
        .order_by(
            Application.created_at.asc()
        )
    )

    return list(result.scalars().all())


async def get_application_by_id(
    session: AsyncSession,
    application_id: int,
) -> Application | None:
    result = await session.execute(
        select(Application).where(
            Application.id == application_id
        )
    )

    return result.scalar_one_or_none()


async def get_application_by_public_number(
    session: AsyncSession,
    public_number: int,
) -> Application | None:
    result = await session.execute(
        select(Application).where(
            Application.public_number == public_number
        )
    )

    return result.scalar_one_or_none()


async def get_user_application_by_public_number(
    session: AsyncSession,
    telegram_id: int,
    public_number: int,
) -> Application | None:
    result = await session.execute(
        select(Application)
        .join(User)
        .where(
            User.telegram_id == telegram_id,
            Application.public_number == public_number,
        )
    )

    return result.scalar_one_or_none()


async def update_application_status(
    session: AsyncSession,
    application_id: int,
    status: str,
) -> Application | None:
    application = await get_application_by_id(
        session=session,
        application_id=application_id,
    )

    if application is None:
        return None

    if not can_transition_status(
        current_status=application.status,
        new_status=status,
    ):
        raise ValueError(
            f"Invalid status transition: "
            f"{application.status} -> {status}"
        )

    application.status = status

    await session.flush()

    return application


async def update_application_status_by_public_number(
    session: AsyncSession,
    public_number: int,
    status: str,
) -> Application | None:
    application = await get_application_by_public_number(
        session=session,
        public_number=public_number,
    )

    if application is None:
        return None

    return await update_application_status(
        session=session,
        application_id=application.id,
        status=status,
    )