from .auth import router as auth_router
from .borrowers import router as borrowers_router
from .holdings import router as holdings_router

__all__ = ["auth_router", "borrowers_router", "holdings_router"]
