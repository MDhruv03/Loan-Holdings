# 🚀 Starting Your Loan Tracker Application

## ⚠️ IMPORTANT: Old Files Renamed

The old application files have been renamed with `.old` extensions:
- `main.py.old` (was causing the 500 error)
- `database.py.old`
- `models.py.old`
- `utils.py.old`

**These are backups only. Do not delete them yet in case you need to reference anything.**

---

## 🎯 How to Start the Server

**Option 1 (Recommended):**
```powershell
python start.bat
```

**Option 2:**
```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 Accessing the Application

Once the server starts, open your browser to:
```
http://localhost:8000
```

You'll see the **login page** first.

---

## 🔐 Default Login Credentials

**Username:** `admin`  
**Password:** `admin123`

*Change these in `app/services/auth.py` after your first login!*

---

## 📱 Features Available

### Borrowers Management
- **Dashboard:** View all borrowers with balances
- **Add Borrower:** Create new loan records
- **Borrower Details:** 
  - View payment history
  - Record new payments
  - Track principal changes with effective dates
  - Auto-calculate new interest rates

### Holdings Management
- **Dashboard:** View all holders with balances
- **Add Holder:** Create new holder accounts (INR/THB/RMB)
- **Holder Details:**
  - Record deposits
  - Make transfers between holders
  - View transaction history with running balances
  - Multi-currency support

---

## 🎨 Design

- **Black & White Theme:** Minimalistic, clean design
- **Mobile Responsive:** Works on all screen sizes
- **Touch Friendly:** Large buttons and inputs for mobile

---

## 🔧 Troubleshooting

### If you see a 500 error:
1. Make sure you stopped the old server (Ctrl+C in terminal)
2. Use the start command above
3. Clear your browser cache (Ctrl+Shift+Delete)
4. Try incognito/private browsing mode

### If database errors occur:
```powershell
Remove-Item loans.db
python -m uvicorn app.main:app --reload
```
This will create a fresh database.

### Check if imports work:
```powershell
python -c "from app.main import app; print('✅ App imports successfully!')"
```

---

## 📚 Documentation

- `README.md` - Full feature documentation
- `QUICKSTART.md` - Quick reference guide
- `PROJECT_SUMMARY.md` - Technical architecture
- `COMPLETE.md` - Detailed completion report

---

## 🗂️ Project Structure

```
Loan/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models/
│   │   ├── borrower.py      # Loan models
│   │   └── holder.py        # Holdings models
│   ├── routers/
│   │   ├── auth.py          # Authentication
│   │   ├── borrowers.py     # Loan routes
│   │   └── holdings.py      # Holdings routes
│   └── services/
│       ├── auth.py          # Auth utilities
│       └── utils.py         # Helper functions
├── templates/               # HTML templates
├── static/                  # CSS styles
└── loans.db                 # SQLite database
```

---

## ✅ Next Steps

1. **Stop any running servers** (Ctrl+C)
2. **Run:** `python start.bat`
3. **Open:** http://localhost:8000
4. **Login** with admin/admin123
5. **Start tracking loans and holdings!**

---

*For questions or issues, refer to the documentation files or check the terminal output for errors.*
