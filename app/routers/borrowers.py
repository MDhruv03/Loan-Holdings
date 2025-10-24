"""
Borrower management routes
"""
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import date
from typing import Optional

from app.database import get_session
from app.models.borrower import Borrower, Payment, PrincipalChange
from app.services.auth import require_auth
from app.services.utils import calculate_overdue_months, format_currency
from app.config import TEMPLATES_DIR

router = APIRouter(prefix="/borrowers", tags=["borrowers"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Add custom filters
templates.env.filters["format_currency"] = format_currency
templates.env.filters["calculate_overdue"] = calculate_overdue_months


@router.get("", response_class=HTMLResponse)
async def list_borrowers(
    request: Request,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Dashboard showing all borrowers"""
    borrowers = session.exec(select(Borrower)).all()
    
    borrower_data = []
    for borrower in borrowers:
        payments = session.exec(
            select(Payment).where(Payment.borrower_id == borrower.id)
        ).all()
        
        overdue_months = calculate_overdue_months(borrower.start_date, len(payments))
        borrower_data.append({
            "borrower": borrower,
            "overdue_months": overdue_months,
            "payment_count": len(payments)
        })
    
    return templates.TemplateResponse(
        "borrowers/dashboard.html",
        {"request": request, "borrower_data": borrower_data}
    )


@router.get("/add", response_class=HTMLResponse)
async def add_borrower_form(
    request: Request,
    _: str = Depends(require_auth)
):
    """Form to add new borrower"""
    return templates.TemplateResponse("borrowers/add.html", {"request": request})


@router.post("/add")
async def add_borrower(
    request: Request,
    name: str = Form(...),
    principal: float = Form(...),
    interest_rate: float = Form(...),
    start_date: date = Form(...),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Add new borrower to database"""
    borrower = Borrower(
        name=name,
        principal=principal,
        interest_rate=interest_rate,
        start_date=start_date
    )
    session.add(borrower)
    session.commit()
    
    return RedirectResponse(url="/borrowers", status_code=303)


@router.get("/{borrower_id}", response_class=HTMLResponse)
async def borrower_detail(
    request: Request,
    borrower_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Detailed view of specific borrower"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    payments = session.exec(
        select(Payment).where(Payment.borrower_id == borrower_id).order_by(Payment.payment_date.desc())
    ).all()
    
    principal_changes = session.exec(
        select(PrincipalChange).where(PrincipalChange.borrower_id == borrower_id).order_by(PrincipalChange.effective_date.desc())
    ).all()
    
    overdue_months = calculate_overdue_months(borrower.start_date, len(payments))
    expected_interest = (borrower.principal * borrower.interest_rate) / 100
    
    return templates.TemplateResponse(
        "borrowers/detail.html",
        {
            "request": request,
            "borrower": borrower,
            "payments": payments,
            "principal_changes": principal_changes,
            "overdue_months": overdue_months,
            "expected_interest": expected_interest
        }
    )


@router.get("/{borrower_id}/edit", response_class=HTMLResponse)
async def edit_borrower_form(
    request: Request,
    borrower_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Form to edit borrower details"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    return templates.TemplateResponse(
        "borrowers/edit.html",
        {"request": request, "borrower": borrower}
    )


@router.post("/{borrower_id}/edit")
async def edit_borrower(
    borrower_id: int,
    name: str = Form(...),
    principal: float = Form(...),
    interest_rate: float = Form(...),
    start_date: date = Form(...),
    principal_recovered: bool = Form(False),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Update borrower details"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    borrower.name = name
    borrower.principal = principal
    borrower.interest_rate = interest_rate
    borrower.start_date = start_date
    borrower.principal_recovered = principal_recovered
    
    session.add(borrower)
    session.commit()
    
    return RedirectResponse(url=f"/borrowers/{borrower_id}", status_code=303)


@router.post("/{borrower_id}/delete")
async def delete_borrower(
    borrower_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Delete borrower and all associated data"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    session.delete(borrower)
    session.commit()
    
    return RedirectResponse(url="/borrowers", status_code=303)


@router.post("/{borrower_id}/payment")
async def add_payment(
    borrower_id: int,
    amount: float = Form(...),
    payment_date: date = Form(...),
    note: Optional[str] = Form(None),
    is_custom: bool = Form(False),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Add payment for borrower"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    payment = Payment(
        borrower_id=borrower_id,
        amount=amount,
        payment_date=payment_date,
        note=note,
        is_custom=is_custom
    )
    session.add(payment)
    session.commit()
    
    return RedirectResponse(url=f"/borrowers/{borrower_id}", status_code=303)


@router.post("/{borrower_id}/change-principal")
async def change_principal(
    borrower_id: int,
    new_principal: float = Form(...),
    effective_date: date = Form(...),
    note: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Change principal amount and recalculate interest rate"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    # Calculate new interest rate based on new principal
    old_monthly_interest = (borrower.principal * borrower.interest_rate) / 100
    new_interest_rate = (old_monthly_interest / new_principal) * 100 if new_principal > 0 else 0
    
    # Record the change
    principal_change = PrincipalChange(
        borrower_id=borrower_id,
        old_principal=borrower.principal,
        new_principal=new_principal,
        old_interest_rate=borrower.interest_rate,
        new_interest_rate=new_interest_rate,
        effective_date=effective_date,
        note=note
    )
    session.add(principal_change)
    
    # Update borrower
    borrower.principal = new_principal
    borrower.interest_rate = new_interest_rate
    session.add(borrower)
    
    session.commit()
    
    return RedirectResponse(url=f"/borrowers/{borrower_id}", status_code=303)


@router.post("/{borrower_id}/toggle-principal")
async def toggle_principal_recovery(
    borrower_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Toggle principal recovery status"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    borrower.principal_recovered = not borrower.principal_recovered
    session.add(borrower)
    session.commit()
    
    return RedirectResponse(url=f"/borrowers/{borrower_id}", status_code=303)
