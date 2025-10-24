"""
Holdings management routes
"""
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

from app.database import get_session
from app.models.holder import Holder, Holding
from app.services.auth import require_auth
from app.services.utils import format_currency, get_currency_symbol
from app.config import TEMPLATES_DIR, SUPPORTED_CURRENCIES

router = APIRouter(prefix="/holdings", tags=["holdings"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Add custom filters
templates.env.filters["format_currency"] = format_currency
templates.env.filters["get_currency_symbol"] = get_currency_symbol


@router.get("", response_class=HTMLResponse)
async def list_holders(
    request: Request,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Dashboard showing all holders with their balances"""
    holders = session.exec(select(Holder)).all()
    
    holder_data = []
    for holder in holders:
        # Calculate balance
        holdings = session.exec(
            select(Holding).where(Holding.holder_id == holder.id)
        ).all()
        
        balance = sum(
            h.amount if h.transaction_type in ["deposit", "transfer_in"] else -h.amount
            for h in holdings
        )
        
        # Calculate transfers out
        transfers_out = sum(
            h.amount for h in holdings if h.transaction_type == "transfer_out"
        )
        
        holder_data.append({
            "holder": holder,
            "balance": balance,
            "transfers_out": transfers_out,
            "available": balance,
            "transaction_count": len(holdings)
        })
    
    return templates.TemplateResponse(
        "holdings/dashboard.html",
        {"request": request, "holder_data": holder_data}
    )


@router.get("/add", response_class=HTMLResponse)
async def add_holder_form(
    request: Request,
    _: str = Depends(require_auth)
):
    """Form to add new holder"""
    return templates.TemplateResponse(
        "holdings/add.html",
        {"request": request, "currencies": SUPPORTED_CURRENCIES}
    )


@router.post("/add")
async def add_holder(
    name: str = Form(...),
    currency: str = Form(...),
    phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Add new holder to database"""
    holder = Holder(
        name=name,
        currency=currency,
        phone=phone,
        notes=notes
    )
    session.add(holder)
    session.commit()
    
    return RedirectResponse(url="/holdings", status_code=303)


@router.get("/{holder_id}", response_class=HTMLResponse)
async def holder_detail(
    request: Request,
    holder_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Detailed view of specific holder"""
    holder = session.get(Holder, holder_id)
    if not holder:
        raise HTTPException(status_code=404, detail="Holder not found")
    
    # Get all transactions
    transactions = session.exec(
        select(Holding).where(Holding.holder_id == holder_id).order_by(Holding.transaction_date.desc())
    ).all()
    
    # Calculate balances
    balance = 0
    transactions_with_balance = []
    
    for txn in reversed(transactions):
        if txn.transaction_type in ["deposit", "transfer_in"]:
            balance += txn.amount
        else:
            balance -= txn.amount
        
        transactions_with_balance.append({
            "transaction": txn,
            "balance_after": balance
        })
    
    transactions_with_balance.reverse()
    
    # Get all holders for transfer dropdown
    all_holders = session.exec(select(Holder).where(Holder.id != holder_id)).all()
    
    return templates.TemplateResponse(
        "holdings/detail.html",
        {
            "request": request,
            "holder": holder,
            "transactions": transactions_with_balance,
            "current_balance": balance,
            "all_holders": all_holders
        }
    )


@router.get("/{holder_id}/edit", response_class=HTMLResponse)
async def edit_holder_form(
    request: Request,
    holder_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Form to edit holder details"""
    holder = session.get(Holder, holder_id)
    if not holder:
        raise HTTPException(status_code=404, detail="Holder not found")
    
    return templates.TemplateResponse(
        "holdings/edit.html",
        {"request": request, "holder": holder, "currencies": SUPPORTED_CURRENCIES}
    )


@router.post("/{holder_id}/edit")
async def edit_holder(
    holder_id: int,
    name: str = Form(...),
    currency: str = Form(...),
    phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Update holder details"""
    holder = session.get(Holder, holder_id)
    if not holder:
        raise HTTPException(status_code=404, detail="Holder not found")
    
    holder.name = name
    holder.currency = currency
    holder.phone = phone
    holder.notes = notes
    
    session.add(holder)
    session.commit()
    
    return RedirectResponse(url=f"/holdings/{holder_id}", status_code=303)


@router.post("/{holder_id}/delete")
async def delete_holder(
    holder_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Delete holder and all associated transactions"""
    holder = session.get(Holder, holder_id)
    if not holder:
        raise HTTPException(status_code=404, detail="Holder not found")
    
    session.delete(holder)
    session.commit()
    
    return RedirectResponse(url="/holdings", status_code=303)


@router.post("/{holder_id}/deposit")
async def add_deposit(
    holder_id: int,
    amount: float = Form(...),
    note: Optional[str] = Form(None),
    transaction_date: Optional[datetime] = Form(None),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Add deposit to holder account"""
    holder = session.get(Holder, holder_id)
    if not holder:
        raise HTTPException(status_code=404, detail="Holder not found")
    
    holding = Holding(
        holder_id=holder_id,
        amount=amount,
        transaction_type="deposit",
        note=note,
        transaction_date=transaction_date or datetime.now()
    )
    session.add(holding)
    session.commit()
    
    return RedirectResponse(url=f"/holdings/{holder_id}", status_code=303)


@router.post("/{holder_id}/withdrawal")
async def add_withdrawal(
    holder_id: int,
    amount: float = Form(...),
    note: Optional[str] = Form(None),
    transaction_date: Optional[datetime] = Form(None),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Add withdrawal from holder account"""
    holder = session.get(Holder, holder_id)
    if not holder:
        raise HTTPException(status_code=404, detail="Holder not found")
    
    holding = Holding(
        holder_id=holder_id,
        amount=amount,
        transaction_type="withdrawal",
        note=note,
        transaction_date=transaction_date or datetime.now()
    )
    session.add(holding)
    session.commit()
    
    return RedirectResponse(url=f"/holdings/{holder_id}", status_code=303)


@router.post("/transfer")
async def transfer_funds(
    from_holder_id: int = Form(...),
    to_holder_id: int = Form(...),
    amount: float = Form(...),
    note: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    _: str = Depends(require_auth)
):
    """Transfer funds between holders"""
    from_holder = session.get(Holder, from_holder_id)
    to_holder = session.get(Holder, to_holder_id)
    
    if not from_holder or not to_holder:
        raise HTTPException(status_code=404, detail="Holder not found")
    
    now = datetime.now()
    
    # Debit from sender
    debit = Holding(
        holder_id=from_holder_id,
        amount=amount,
        transaction_type="transfer_out",
        related_holder_id=to_holder_id,
        note=f"Transfer to {to_holder.name}" + (f": {note}" if note else ""),
        transaction_date=now
    )
    session.add(debit)
    
    # Credit to receiver
    credit = Holding(
        holder_id=to_holder_id,
        amount=amount,
        transaction_type="transfer_in",
        related_holder_id=from_holder_id,
        note=f"Transfer from {from_holder.name}" + (f": {note}" if note else ""),
        transaction_date=now
    )
    session.add(credit)
    
    session.commit()
    
    return RedirectResponse(url=f"/holdings/{from_holder_id}", status_code=303)
