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
from app.services.utils import (
    calculate_months_between,
    calculate_expected_monthly_interest,
    calculate_interest_due,
    calculate_total_due,
    format_currency,
)
from app.config import TEMPLATES_DIR

router = APIRouter(prefix="/borrowers", tags=["borrowers"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Add custom filters
templates.env.filters["format_currency"] = format_currency


@router.get("", response_class=HTMLResponse)
async def list_borrowers(
    request: Request,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Dashboard showing all borrowers"""
    borrowers = session.exec(select(Borrower).order_by(Borrower.created_at.desc())).all()

    summary = {
        "borrower_count": 0,
        "active_count": 0,
        "recovered_count": 0,
        "defaulted_count": 0,
        "principal_outstanding": 0.0,
        "principal_recovered": 0.0,
        "money_lost": 0.0,
        "monthly_interest_expected": 0.0,
        "interest_due": 0.0,
        "interest_recovered": 0.0,
        "total_due": 0.0,
    }

    borrower_data = []
    for borrower in borrowers:
        payments = session.exec(
            select(Payment).where(Payment.borrower_id == borrower.id)
        ).all()

        total_interest_paid = sum(p.amount for p in payments)
        expected_monthly_interest = calculate_expected_monthly_interest(
            borrower.principal, borrower.interest_rate
        )
        interest_due = calculate_interest_due(
            borrower.start_date,
            borrower.principal,
            borrower.interest_rate,
            total_interest_paid,
        )
        overdue_months = int(interest_due // expected_monthly_interest) if expected_monthly_interest else 0
        total_due = calculate_total_due(
            borrower.principal,
            interest_due,
            principal_recovered=borrower.principal_recovered,
            is_defaulted=borrower.is_defaulted,
        )

        status = "active"
        if borrower.is_defaulted:
            status = "defaulted"
        elif borrower.principal_recovered:
            status = "recovered"

        if status == "defaulted":
            interest_due = 0.0
            overdue_months = 0
            total_due = 0.0

        summary["borrower_count"] += 1
        summary["interest_recovered"] += total_interest_paid

        if status == "active":
            summary["active_count"] += 1
            summary["principal_outstanding"] += borrower.principal
            summary["monthly_interest_expected"] += expected_monthly_interest
            summary["interest_due"] += interest_due
            summary["total_due"] += total_due
        elif status == "recovered":
            summary["recovered_count"] += 1
            summary["principal_recovered"] += borrower.principal
        else:
            summary["defaulted_count"] += 1
            summary["money_lost"] += borrower.principal

        borrower_data.append({
            "borrower": borrower,
            "status": status,
            "expected_monthly_interest": expected_monthly_interest,
            "interest_recovered": total_interest_paid,
            "interest_due": interest_due,
            "total_due": total_due,
            "overdue_months": overdue_months,
            "payment_count": len(payments)
        })

    summary["total_recovered"] = summary["interest_recovered"] + summary["principal_recovered"]
    
    return templates.TemplateResponse(
        "borrowers/dashboard.html",
        {
            "request": request,
            "borrower_data": borrower_data,
            "summary": summary,
        }
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

    total_interest_paid = sum(p.amount for p in payments)
    expected_interest = calculate_expected_monthly_interest(borrower.principal, borrower.interest_rate)
    interest_due = calculate_interest_due(
        borrower.start_date,
        borrower.principal,
        borrower.interest_rate,
        total_interest_paid,
    )
    overdue_months = int(interest_due // expected_interest) if expected_interest else 0
    total_due = calculate_total_due(
        borrower.principal,
        interest_due,
        principal_recovered=borrower.principal_recovered,
        is_defaulted=borrower.is_defaulted,
    )
    months_elapsed = calculate_months_between(borrower.start_date)

    status = "active"
    if borrower.is_defaulted:
        status = "defaulted"
    elif borrower.principal_recovered:
        status = "recovered"

    if status == "defaulted":
        interest_due = 0.0
        overdue_months = 0
        total_due = 0.0
    
    return templates.TemplateResponse(
        "borrowers/detail.html",
        {
            "request": request,
            "borrower": borrower,
            "payments": payments,
            "principal_changes": principal_changes,
            "status": status,
            "months_elapsed": months_elapsed,
            "overdue_months": overdue_months,
            "expected_interest": expected_interest,
            "interest_recovered": total_interest_paid,
            "interest_due": interest_due,
            "total_due": total_due,
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

    if borrower.principal_recovered:
        borrower.is_defaulted = False
        borrower.defaulted_on = None
        borrower.default_note = None
    
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

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than 0")
    
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


@router.post("/{borrower_id}/payment/{payment_id}/delete")
async def delete_payment(
    borrower_id: int,
    payment_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Delete a recorded payment."""
    payment = session.get(Payment, payment_id)
    if not payment or payment.borrower_id != borrower_id:
        raise HTTPException(status_code=404, detail="Payment not found")

    session.delete(payment)
    session.commit()

    return RedirectResponse(url=f"/borrowers/{borrower_id}", status_code=303)


@router.post("/{borrower_id}/adjust-terms")
async def adjust_terms(
    borrower_id: int,
    effective_date: date = Form(...),
    additional_principal: float = Form(0.0),
    new_interest_rate: Optional[float] = Form(None),
    note: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Adjust borrower terms when more principal is lent or interest changes."""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    if additional_principal < 0:
        raise HTTPException(status_code=400, detail="Additional principal cannot be negative")

    if new_interest_rate is not None and new_interest_rate <= 0:
        raise HTTPException(status_code=400, detail="Interest rate must be greater than 0")

    updated_principal = borrower.principal + additional_principal
    updated_rate = new_interest_rate if new_interest_rate is not None else borrower.interest_rate

    if abs(updated_principal - borrower.principal) < 1e-9 and abs(updated_rate - borrower.interest_rate) < 1e-9:
        return RedirectResponse(url=f"/borrowers/{borrower_id}", status_code=303)

    detail_parts = []
    if additional_principal > 0:
        detail_parts.append(f"Added principal: {additional_principal:.2f}")
    if abs(updated_rate - borrower.interest_rate) >= 1e-9:
        detail_parts.append(f"Rate changed: {borrower.interest_rate:.4f}% -> {updated_rate:.4f}%")

    final_note = " | ".join(detail_parts)
    if note:
        final_note = f"{final_note} | {note}" if final_note else note

    principal_change = PrincipalChange(
        borrower_id=borrower_id,
        old_principal=borrower.principal,
        new_principal=updated_principal,
        old_interest_rate=borrower.interest_rate,
        new_interest_rate=updated_rate,
        effective_date=effective_date,
        note=final_note,
    )
    session.add(principal_change)

    borrower.principal = updated_principal
    borrower.interest_rate = updated_rate
    borrower.principal_recovered = False
    borrower.is_defaulted = False
    borrower.defaulted_on = None
    borrower.default_note = None
    session.add(borrower)

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

    if new_principal <= 0:
        raise HTTPException(status_code=400, detail="Principal must be greater than 0")
    
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


@router.post("/{borrower_id}/mark-defaulted")
async def mark_defaulted(
    borrower_id: int,
    note: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Mark borrower as defaulted/conned and count principal as lost."""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    borrower.is_defaulted = True
    borrower.defaulted_on = date.today()
    borrower.default_note = note
    borrower.principal_recovered = False

    session.add(borrower)
    session.commit()

    return RedirectResponse(url=f"/borrowers/{borrower_id}", status_code=303)


@router.post("/{borrower_id}/clear-defaulted")
async def clear_defaulted(
    borrower_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Move borrower back to active status from defaulted."""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    borrower.is_defaulted = False
    borrower.defaulted_on = None
    borrower.default_note = None

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

    if borrower.principal_recovered:
        borrower.is_defaulted = False
        borrower.defaulted_on = None
        borrower.default_note = None

    session.add(borrower)
    session.commit()
    
    return RedirectResponse(url=f"/borrowers/{borrower_id}", status_code=303)
