"""
Utility functions for calculations and formatting
"""
from datetime import date
from typing import Dict


def calculate_months_between(start_date: date, end_date: date = None) -> int:
    """Calculate number of months between two dates"""
    if end_date is None:
        end_date = date.today()
    
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    
    if end_date.day < start_date.day:
        months -= 1
    
    return max(0, months)


def calculate_overdue_months(start_date: date, payments_made: int) -> int:
    """Calculate how many months a borrower is overdue"""
    months_elapsed = calculate_months_between(start_date)
    return max(0, months_elapsed - payments_made)


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format currency with appropriate symbol"""
    symbols = {
        "INR": "₹",
        "THB": "฿",
        "RMB": "¥"
    }
    
    symbol = symbols.get(currency, "₹")
    
    try:
        abs_amount = abs(amount)
        if currency == "INR":
            if abs_amount >= 10000000:  # 1 crore
                return f"{symbol}{amount/10000000:.2f} Cr"
            elif abs_amount >= 100000:  # 1 lakh
                return f"{symbol}{amount/100000:.2f} L"
        
        return f"{symbol}{amount:,.2f}"
    except:
        return f"{symbol}{amount}"


def get_currency_symbol(currency: str) -> str:
    """Get currency symbol"""
    symbols = {
        "INR": "₹",
        "THB": "฿",
        "RMB": "¥"
    }
    return symbols.get(currency, "₹")
