import os

from dotenv import load_dotenv

load_dotenv()


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url

    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://"):]

    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]

    return url


BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_URL_RAW = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://lead_bot:lead_bot_password@127.0.0.1:5433/lead_bot",
)

DATABASE_URL = normalize_database_url(DATABASE_URL_RAW)

ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")

ADMIN_IDS: set[int] = set()

for value in ADMIN_IDS_RAW.split(","):
    value = value.strip()

    if not value:
        continue

    try:
        ADMIN_IDS.add(int(value))
    except ValueError:
        raise ValueError(
            f"Invalid ADMIN_IDS value: {value}"
        )


if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is not set in environment variables"
    )