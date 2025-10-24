# QUICKSTART GUIDE

## Installation & Setup

1. Install dependencies:
```powershell
pip install -r requirements.txt
```

2. Run the application:
```powershell
python -m app.main
```

3. Open browser:
```
http://localhost:8000
```

4. Login with default credentials:
- Username: `admin`
- Password: `admin123`

## Features Implemented

✅ Borrower Management
  - Add/edit/delete borrowers
  - Track principal, interest rate, start date
  - Record monthly interest payments
  - Custom interest payments
  - Change principal with effective date tracking
  - Mark principal as recovered
  - View overdue payments
  - Payment history

✅ Holdings Management
  - Multi-currency support (INR, THB, RMB)
  - Add/edit/delete holders
  - Record deposits and withdrawals
  - Transfer between holders
  - Transaction history with running balance
  - Cumulative balance display

✅ Authentication
  - Secure login system
  - Session caching (30 days)
  - Mobile-friendly

✅ UI/UX
  - Minimalistic black & white theme
  - Mobile responsive
  - Clean, modern interface

## Security Notes

**IMPORTANT**: Change default credentials in production!

Set environment variables:
```powershell
$env:ADMIN_USERNAME = "your_username"
$env:ADMIN_PASSWORD = "your_password"
$env:SECRET_KEY = "your-secret-key-here"
```

## Project Structure

```
app/
├── config.py          - Settings & configuration
├── database.py        - Database setup
├── main.py            - FastAPI app entry point
├── models/
│   ├── borrower.py    - Borrower, Payment, PrincipalChange
│   └── holder.py      - Holder, Holding
├── routers/
│   ├── auth.py        - Login/logout routes
│   ├── borrowers.py   - Borrower management
│   └── holdings.py    - Holdings management
└── services/
    ├── auth.py        - Authentication logic
    └── utils.py       - Utility functions

templates/
├── base.html
├── login.html
├── borrowers/         - Borrower templates
└── holdings/          - Holdings templates

static/
└── style.css          - Black & white minimalistic CSS
```

## Usage

### Borrowers
1. Dashboard shows all borrowers with overdue status
2. Add new borrower with principal, rate, start date
3. View details to see payment history
4. Record payments (regular or custom amounts)
5. Change principal (auto-calculates new interest rate)
6. Mark principal as recovered

### Holdings
1. Dashboard shows all holders with balances
2. Add holder with name, currency (INR/THB/RMB)
3. View details to see transactions
4. Add deposits or transfers
5. Transfer funds between holders
6. View running balance history

## Mobile Access

Fully responsive! Your father can:
- Access from mobile browser
- Login once (session lasts 30 days)
- View/add borrowers and payments
- Manage holdings on-the-go

## Need Help?

Check the main README.md for detailed documentation.
