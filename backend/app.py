from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings
from .database import get_db
from .azure_openai_service import get_openai_client
from .azure_keyvault import get_keyvault_client
from .tenant_middleware import TenantMiddleware
from sqlalchemy.orm import Session

app = FastAPI(title="IG Shop Agent API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware
app.add_middleware(TenantMiddleware)

@app.get("/")
async def root():
    return {"message": "IG Shop Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import and include routers
from .routers import auth, catalog, orders, conversations, kb

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(kb.router, prefix="/kb", tags=["knowledge-base"]) 