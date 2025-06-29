# Routes package for IG-Shop-Agent FastAPI backend
from .auth import router as auth_router
from .catalog import router as catalog_router
from .orders import router as orders_router

__all__ = ["auth_router", "catalog_router", "orders_router"]