@echo off
echo ================================================
echo    Starting Loan Tracker Application
echo ================================================
echo.
echo Server will start at: http://localhost:8000
echo Default Login: admin / admin123
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
