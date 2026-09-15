# Telegram Lead Bot

Production-ready Telegram bot template for collecting client requests, storing them in PostgreSQL, processing them through an admin workflow, and sending status notifications.

## Demo

Telegram bot: https://t.me/VladimirLeadTemplateBot

GitHub repository: https://github.com/VladimirKostik/telegram-lead-bot-

## Features

- Telegram `/start` entry point
- Application form based on FSM (finite-state machine)
- User data stored in PostgreSQL
- Unique public application numbers
- Separate internal database ID and public application number
- User view: `📋 Мої заявки`
- Admin view: `📥 Нові заявки`
- Application status workflow
- User notifications when application status changes
- Admin notifications for new applications
- Admin authorization by Telegram ID
- Ownership checks for user application access
- IDOR protection for application access
- Automated security and authorization tests
- Async SQLAlchemy + asyncpg
- Dockerized application
- PostgreSQL container for local development
- Alembic database migrations
- Railway deployment
- GitHub-based automatic deployment

## Application Status Workflow

Allowed transitions:

```text
NEW → IN_PROGRESS
NEW → CANCELLED

IN_PROGRESS → DONE
IN_PROGRESS → CANCELLED

Terminal statuses:

DONE
CANCELLED

No transitions are allowed from terminal statuses.

Tech Stack
Python 3.14
aiogram 3
SQLAlchemy 2
asyncpg
PostgreSQL 16
Alembic
Docker / Docker Compose
pytest
Railway
GitHub
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

Production architecture:

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
├── alembic/
│   ├── versions/
│   │   ├── 1e8d1d635706_initial_database_schema.py
│   │   └── e0f06859f146_normalize_public_number_index.py
│   ├── env.py
│   ├── script.py.mako
│   └── README
│
├── tests/
│   └── test_security.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
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
Security
Admin Authorization

Administrative actions are restricted to Telegram IDs configured in ADMIN_IDS.

A regular user cannot:

open the admin queue
change application status
perform administrative actions through callbacks
Application Ownership

A user can access only their own applications.

The user-facing application lookup uses both:

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
ADMIN_IDS=123456789
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

For production, configure environment variables in Railway.

Never commit:

.env
Telegram bot tokens
database passwords
private credentials
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

PostgreSQL itself listens on port 5432 inside the container.

6. Run database migrations
alembic upgrade head

Check migration state:

alembic current

Check that the models and database are synchronized:

alembic check
7. Run the bot locally
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

Alembic

Alembic is used for versioned database schema migrations.

Current migration chain:

<base>
   ↓
1e8d1d635706
initial database schema
   ↓
e0f06859f146
normalize public number index

Useful commands:

alembic current
alembic history
alembic upgrade head
alembic downgrade -1
alembic check

Production uses:

alembic upgrade head

as the Railway pre-deploy command.

Testing

Run the automated test suite:

python -m pytest -q

Current verified baseline:

58 passed

The test suite covers:

administrator authorization
regular user access restrictions
allowed status transitions
forbidden status transitions
application ownership
foreign-user access denial
IDOR-related access control
Notifications

Notifications are isolated in:

app/services/notifications.py

Two main flows are supported:

New application
      ↓
Administrators

and:

Application status changed
      ↓
Application owner

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

Production variables:

BOT_TOKEN
ADMIN_IDS
DATABASE_URL

The production GitHub branch is:

main

Automatic deployment is enabled.

Railway pre-deploy command:

alembic upgrade head

Application start command:

python -m app.main
Deployment Flow
Local changes
     ↓
pytest
     ↓
Alembic verification
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
alembic upgrade head
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

Security smoke testing should verify:

Regular user
   ↓
No admin menu

User A
   ↓
Cannot access User B applications

DONE
   ↓
No further status transitions

CANCELLED
   ↓
No further status transitions
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

Check migration state:

alembic check

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
Project Status

Current template status:

✅ Telegram application flow
✅ PostgreSQL persistence
✅ Admin workflow
✅ Status transition security
✅ User notifications
✅ Admin notifications
✅ Ownership checks
✅ IDOR protection
✅ Automated security tests
✅ Docker support
✅ Railway deployment
✅ GitHub Auto Deploy
✅ Alembic migrations
✅ Production smoke testing
✅ Technical documentation

Current automated test baseline:

58 passed

Current Alembic head:

e0f06859f146
Release

The stable release is intended to be tagged as:

v1.0.0
License

This project is a reusable freelance development template.

Add a project-specific license before distributing the source code to third parties.