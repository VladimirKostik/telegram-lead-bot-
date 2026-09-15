Telegram Lead Bot

Production-ready Telegram bot template for collecting client requests, storing them in PostgreSQL, processing them through an admin workflow, and sending status notifications.

Demo

Telegram bot: https://t.me/VladimirLeadTemplateBot

GitHub repository: https://github.com/VladimirKostik/telegram-lead-bot-

Features

Telegram /start entry point

Application form based on FSM (finite-state machine)

User data stored in PostgreSQL

Unique public application numbers

Separate internal database ID and public application number

User view: 📋 Мої заявки

Admin view: 📥 Нові заявки

Application status workflow:

NEW → IN_PROGRESS

NEW → CANCELLED

IN_PROGRESS → DONE

IN_PROGRESS → CANCELLED

Terminal statuses: DONE, CANCELLED

User notifications when application status changes

Admin notifications for new applications

Admin authorization by Telegram ID

Ownership checks for user application access

IDOR protection for application access

Automated security and authorization tests

Async SQLAlchemy + asyncpg

Dockerized application

PostgreSQL container for local development

Railway deployment for production

GitHub-based automatic deployment

Tech Stack

Python 3.14

aiogram 3

SQLAlchemy 2

asyncpg

PostgreSQL 16

Docker / Docker Compose

pytest

Alembic — planned migration layer

Railway — production deployment

GitHub — source control and deployment trigger

Architecture

Telegram User
     │
     ▼
aiogram handlers
     │
     ├── FSM / form flow
     ├── admin workflow
     └── notifications
     │
     ▼
Repositories / business logic
     │
     ▼
SQLAlchemy Async
     │
     ▼
PostgreSQL

Production:

GitHub
   │
   ▼
Railway
   ├── Telegram Bot service
   └── PostgreSQL service

Project Structure

telegram-lead-bot-/
│
├── app/
│   ├── database/
│   │   ├── database.py
│   │   ├── init_database.py
│   │   ├── models.py
│   │   └── repositories.py
│   │
│   ├── handlers/
│   │   ├── admin.py
│   │   └── application.py
│   │
│   ├── keyboards/
│   │   ├── admin.py
│   │   ├── application.py
│   │   └── main.py
│   │
│   ├── services/
│   │   └── notifications.py
│   │
│   ├── states/
│   │   └── application.py
│   │
│   ├── config.py
│   ├── main.py
│   └── security.py
│
├── tests/
│   └── test_security.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md

Application Workflow

User

/start
   ↓
Main menu
   ↓
📝 Залишити заявку
   ↓
Name
   ↓
Phone
   ↓
Service
   ↓
Comment
   ↓
Confirmation
   ↓
Application created
   ↓
Public application number
   ↓
Notification to administrators

Administrator

📥 Нові заявки
   ↓
NEW
   ├── 🟡 Взяти в роботу
   │      ↓
   │   IN_PROGRESS
   │      ├── 🟢 Виконано
   │      │      ↓
   │      │     DONE
   │      └── 🔴 Скасувати
   │             ↓
   │          CANCELLED
   │
   └── 🔴 Скасувати
          ↓
       CANCELLED

DONE and CANCELLED are terminal statuses.

Security

Admin authorization

Administrative actions are restricted to Telegram IDs configured in ADMIN_IDS.

A regular user cannot:

open the admin queue;

change application status;

perform administrative actions through callbacks.

Application ownership

A user can access only their own applications.

The application lookup for user-facing actions is performed with both:

telegram_id
+
public_number

This prevents a user from accessing another user's application by guessing a number.

Internal ID vs Public Number

The database primary key:

applications.id

is an internal identifier.

The user-facing number:

applications.public_number

is a separate generated value.

The public number is not the database primary key and is intended for communication with users.

Database Model

users

Main fields:

id
telegram_id
username
first_name
phone
language
created_at
updated_at

applications

Main fields:

id
public_number
user_id
name
phone
service
comment
status
created_at
updated_at

Relationship:

users 1 ─────── N applications

Environment Variables

Create .env locally from .env.example.

Required variables:

BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=1234567890
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

For production, environment variables are configured in Railway.

Never commit .env.

Local Development

1. Clone the repository

git clone https://github.com/VladimirKostik/telegram-lead-bot-.git
cd telegram-lead-bot-

2. Create and activate a virtual environment

Windows / Git Bash:

python -m venv .venv
source .venv/Scripts/activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Create:

.env

based on:

.env.example

5. Start PostgreSQL

docker compose up -d db

The local PostgreSQL service is exposed on:

127.0.0.1:5433

while PostgreSQL itself listens on port 5432 inside the container.

6. Run the bot locally

python -m app.main

Docker

Build the image:

docker build -t telegram-lead-bot .

Run the full local stack:

docker compose up -d --build

Check services:

docker compose ps

View bot logs:

docker compose logs bot

Stop the local bot:

docker compose stop bot

When production is running on Railway, do not run a second long-polling instance with the same Telegram bot token at the same time.

Testing

Run the automated tests:

python -m pytest -q

Current test baseline:

18 passed

The current test suite focuses on authorization, status transitions, ownership, and IDOR-related access control.

Status Transition Rules

Allowed:

NEW → IN_PROGRESS
NEW → CANCELLED

IN_PROGRESS → DONE
IN_PROGRESS → CANCELLED

Forbidden:

IN_PROGRESS → NEW

DONE → NEW
DONE → IN_PROGRESS
DONE → CANCELLED

CANCELLED → NEW
CANCELLED → IN_PROGRESS
CANCELLED → DONE

The transition rules are enforced in app/security.py.

Notifications

Notifications are isolated in:

app/services/notifications.py

Two main flows are supported:

New application → administrators

Application status changed → application owner

Notifications are sent only after the corresponding database operation has been successfully committed.

Production Deployment

The project is deployed to Railway.

Production architecture:

Railway Project
│
├── telegram-lead-bot-
│   └── Python / aiogram / Docker
│
└── Postgres
    └── PostgreSQL database

The application receives these production variables from Railway:

BOT_TOKEN
ADMIN_IDS
DATABASE_URL

The production PostgreSQL URL is normalized to the async SQLAlchemy driver format:

postgresql+asyncpg://...

The GitHub branch connected to production is:

main

Automatic deployment is enabled, so pushes to the production branch can trigger a new Railway deployment.

Deployment Flow

Local changes
     ↓
pytest
     ↓
Docker verification
     ↓
git commit
     ↓
git push origin main
     ↓
GitHub
     ↓
Railway build
     ↓
Railway deployment
     ↓
Production bot

Production Verification

A production smoke test should verify:

Telegram
   ↓
Create application
   ↓
NEW
   ↓
Admin notification
   ↓
IN_PROGRESS
   ↓
DONE / CANCELLED
   ↓
User notification
   ↓
Application stored in Railway PostgreSQL

Client Customization

This repository is intended to be reused as a client template.

Typical client-specific changes:

bot name and username

company name

contact information

FAQ content

application form fields

service list

administrator Telegram IDs

notification texts

branding and emojis

additional integrations

The core architecture can remain unchanged.

Development Rules

Before pushing changes:

python -m pytest -q

Check Git state:

git status

Commit:

git add .
git commit -m "describe the change"

Push:

git push origin main

Never commit:

.env
Telegram bot tokens
database passwords
private credentials

Roadmap

Planned production hardening:

Alembic database migrations

Expanded integration tests

More structured application logging

Improved error handling

Final template cleanup

Release tags and versioning

Additional client integrations when required

License

This project is a reusable freelance development template. Add a project-specific license before distributing the source code to third parties.