"""
Utility functions for calculations and formatting
"""
from datetime import date
from typing import Optional


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


def calculate_expected_monthly_interest(principal: float, interest_rate: float) -> float:
    """Calculate fixed monthly interest amount for a borrower."""
    return max(0.0, (principal * interest_rate) / 100)


def calculate_interest_due(
    start_date: date,
    principal: float,
    interest_rate: float,
    total_interest_paid: float,
    as_of_date: Optional[date] = None,
) -> float:
    """Calculate outstanding interest due till a date.

    Interest in this business model does not reduce principal. We therefore compute
    due as: elapsed_months * monthly_interest - total_interest_paid.
    """
    months_elapsed = calculate_months_between(start_date, as_of_date)
    expected_total_interest = months_elapsed * calculate_expected_monthly_interest(principal, interest_rate)
    return max(0.0, expected_total_interest - max(0.0, total_interest_paid))


def calculate_total_due(
    principal: float,
    interest_due: float,
    principal_recovered: bool = False,
    is_defaulted: bool = False,
) -> float:
    """Total due amount = pending principal (if active) + outstanding interest."""
    principal_due = 0.0 if principal_recovered or is_defaulted else max(0.0, principal)
    return principal_due + max(0.0, interest_due)


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
