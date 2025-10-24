"""
FastAPI Application - Personal Loan and Holdings Tracker
"""
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import APP_TITLE, APP_VERSION, SECRET_KEY, STATIC_DIR, TEMPLATES_DIR
from app.database import create_db_and_tables
from app.routers import auth, borrowers, holdings
from app.services.auth import get_current_user

# Create FastAPI app
app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# Add session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include routers
app.include_router(auth.router)
app.include_router(borrowers.router)
app.include_router(holdings.router)


@app.on_event("startup")
def on_startup():
    """Initialize database on startup"""
    create_db_and_tables()


@app.get("/")
async def root(request: Request):
    """Redirect to appropriate page based on auth status"""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/borrowers")
    return RedirectResponse(url="/login")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
