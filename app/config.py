import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://lead_bot:lead_bot_password@127.0.0.1:5433/lead_bot",
)


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
        "BOT_TOKEN is not set in .env"
    )