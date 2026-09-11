from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Application, User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
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


async def create_application(
    session: AsyncSession,
    user: User,
    name: str,
    phone: str,
    service: str,
    comment: str | None,
) -> Application:
    application = Application(
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