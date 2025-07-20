from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from datetime import datetime, date
from typing import Optional
import uvicorn

from database import get_session, create_db_and_tables
from models import Borrower, Payment,Holder, Holding
from utils import calculate_months_between, format_currency, calculate_overdue_months

app = FastAPI(title="Personal Loan Tracker", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Add custom template filters
templates.env.filters["format_currency"] = format_currency
templates.env.filters["calculate_overdue"] = calculate_overdue_months

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    """Main dashboard showing all borrowers"""
    borrowers = session.exec(select(Borrower)).all()
    
    # Calculate overdue months for each borrower
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
        "dashboard.html", 
        {"request": request, "borrower_data": borrower_data}
    )

@app.get("/add", response_class=HTMLResponse)
async def add_borrower_form(request: Request):
    """Form to add new borrower"""
    return templates.TemplateResponse("add_borrower.html", {"request": request})

@app.post("/add")
async def add_borrower(
    name: str = Form(...),
    principal: float = Form(...),
    interest_rate: float = Form(...),
    start_date: date = Form(...),
    session: Session = Depends(get_session)
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
    
    return RedirectResponse(url="/", status_code=303)

@app.get("/borrower/{borrower_id}", response_class=HTMLResponse)
async def borrower_detail(
    request: Request, 
    borrower_id: int, 
    session: Session = Depends(get_session)
):
    """Detailed view of specific borrower"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    payments = session.exec(
        select(Payment).where(Payment.borrower_id == borrower_id).order_by(Payment.payment_date.desc())
    ).all()
    
    overdue_months = calculate_overdue_months(borrower.start_date, len(payments))
    expected_interest = (borrower.principal * borrower.interest_rate) / 100
    
    return templates.TemplateResponse(
        "borrower_detail.html",
        {
            "request": request,
            "borrower": borrower,
            "payments": payments,
            "overdue_months": overdue_months,
            "expected_interest": expected_interest
        }
    )

@app.get("/borrower/{borrower_id}/edit", response_class=HTMLResponse)
async def edit_borrower_form(
    request: Request,
    borrower_id: int,
    session: Session = Depends(get_session)
):
    """Form to edit borrower details"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    return templates.TemplateResponse(
        "edit_borrower.html",
        {"request": request, "borrower": borrower}
    )

@app.post("/borrower/{borrower_id}/edit")
async def edit_borrower(
    borrower_id: int,
    name: str = Form(...),
    principal: float = Form(...),
    interest_rate: float = Form(...),
    start_date: date = Form(...),
    principal_recovered: bool = Form(False),
    session: Session = Depends(get_session)
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
    
    return RedirectResponse(url=f"/borrower/{borrower_id}", status_code=303)

@app.post("/borrower/{borrower_id}/delete")
async def delete_borrower(
    borrower_id: int,
    session: Session = Depends(get_session)
):
    """Delete borrower and all associated payments"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    # Delete associated payments first
    payments = session.exec(select(Payment).where(Payment.borrower_id == borrower_id)).all()
    for payment in payments:
        session.delete(payment)
    
    # Delete borrower
    session.delete(borrower)
    session.commit()
    
    return RedirectResponse(url="/", status_code=303)

@app.post("/borrower/{borrower_id}/payment")
async def add_payment(
    borrower_id: int,
    amount: float = Form(...),
    payment_date: date = Form(...),
    session: Session = Depends(get_session)
):
    """Add payment for borrower"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    payment = Payment(
        borrower_id=borrower_id,
        amount=amount,
        payment_date=payment_date
    )
    session.add(payment)
    session.commit()
    
    return RedirectResponse(url=f"/borrower/{borrower_id}", status_code=303)

@app.post("/borrower/{borrower_id}/toggle-principal")
async def toggle_principal_recovery(
    borrower_id: int,
    session: Session = Depends(get_session)
):
    """Toggle principal recovery status"""
    borrower = session.get(Borrower, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    borrower.principal_recovered = not borrower.principal_recovered
    session.add(borrower)
    session.commit()
    
    return RedirectResponse(url=f"/borrower/{borrower_id}", status_code=303)


@app.get("/holders", response_class=HTMLResponse)
async def view_holders(request: Request, session: Session = Depends(get_session)):
    holders = session.exec(select(Holder)).all()
    return templates.TemplateResponse("holders.html", {"request": request, "holders": holders})

@app.get("/holder/{holder_id}", response_class=HTMLResponse)
async def holder_detail(holder_id: int, request: Request, session: Session = Depends(get_session)):
    holder = session.get(Holder, holder_id)
    if not holder:
        raise HTTPException(status_code=404, detail="Holder not found")
    
    transactions = session.exec(
        select(Holding).where(Holding.holder_id == holder_id).order_by(Holding.created_at.desc())
    ).all()

    return templates.TemplateResponse("holder_detail.html", {
        "request": request,
        "holder": holder,
        "transactions": transactions
    })


@app.post("/holder/{holder_id}/deposit")
async def deposit(holder_id: int, amount: float = Form(...), note: str = Form(None), session: Session = Depends(get_session)):
    holding = Holding(
        holder_id=holder_id,
        amount=amount,
        type="deposit",
        direction="credit",
        note=note
    )
    session.add(holding)
    session.commit()
    return RedirectResponse(url=f"/holder/{holder_id}", status_code=303)

@app.post("/transfer")
async def transfer(
    from_holder_id: int = Form(...),
    to_holder_id: int = Form(...),
    amount: float = Form(...),
    note: str = Form(None),
    session: Session = Depends(get_session)
):
    # Debit from sender
    debit = Holding(
        holder_id=from_holder_id,
        amount=amount,
        type="transfer",
        direction="debit",
        note=f"Transfer to Holder {to_holder_id}. " + (note or "")
    )
    session.add(debit)

    # Credit to receiver
    credit = Holding(
        holder_id=to_holder_id,
        amount=amount,
        type="transfer",
        direction="credit",
        note=f"Transfer from Holder {from_holder_id}. " + (note or "")
    )
    session.add(credit)

    session.commit()
    return RedirectResponse(url=f"/holder/{from_holder_id}", status_code=303)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)