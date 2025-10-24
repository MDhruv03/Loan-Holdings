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

## Structure
app/ - Application code (routers, models, services)
templates/ - HTML templates
static/ - CSS styles
loans.db - SQLite database (auto-created)
