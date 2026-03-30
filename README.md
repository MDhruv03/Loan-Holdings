# Loan Tracker
Modern FastAPI app for tracking loans & holdings with monthly interest.

## Features
- Borrower Management: Track loans, interest payments, overdue accounts
- Holdings Management: Multi-currency (INR/THB/RMB), transfers, balances
- Authentication: Secure login with 30-day session cache
- Mobile responsive black & white minimalistic UI

## Quick Start
```bash
pip install -r requirements.txt
python -m app.main
```
Login: admin/admin123 (Change in production!)
Access: http://localhost:8000

## PostgreSQL (Neon) Support
The app supports SQLite locally and PostgreSQL in production.

Use environment variable `DATABASE_URL`:

```bash
postgresql://USER:PASSWORD@HOST/DB_NAME?sslmode=require
```

Notes:
- Neon connection strings usually already include `sslmode=require`.
- `postgres://` URLs are auto-normalized to `postgresql://`.

## Deploy on Render
This repository includes `render.yaml` for one-click setup.

1. Push this repo to GitHub.
2. In Render, create a new Blueprint and select this repository.
3. Set required environment variables in Render:
	- `DATABASE_URL` = your Neon connection string
	- `ADMIN_PASSWORD` = secure admin password
	- (Optional) `ADMIN_USERNAME`
4. Deploy.

Default start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Structure
app/ - Application code (routers, models, services)
templates/ - HTML templates
static/ - CSS styles
loans.db - SQLite database (auto-created)
