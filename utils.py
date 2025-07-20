from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import locale

def calculate_months_between(start_date: date, end_date: date = None) -> int:
    """Calculate number of months between two dates"""
    if end_date is None:
        end_date = date.today()
    
    # Calculate the difference in months
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    
    # If we haven't reached the day of the month yet, subtract 1
    if end_date.day < start_date.day:
        months -= 1
    
    return max(0, months)

def calculate_overdue_months(start_date: date, payments_made: int) -> int:
    """Calculate how many months a borrower is overdue"""
    months_elapsed = calculate_months_between(start_date)
    return max(0, months_elapsed - payments_made)

def format_currency(amount: float) -> str:
    """Format currency with Indian Rupee symbol and commas"""
    try:
        # Format with commas for Indian numbering system
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.2f}"
    except:
        return f"₹{amount}"

def get_status_class(overdue_months: int) -> str:
    """Get CSS class based on overdue status"""
    if overdue_months == 0:
        return "status-good"
    elif overdue_months <= 2:
        return "status-warning"
    else:
        return "status-danger"