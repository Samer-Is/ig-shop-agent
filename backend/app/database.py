"""
Database connection and session management.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from .config import settings


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool if settings.debug else None,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with context management."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session."""
    async with get_db_session() as session:
        yield session


async def set_tenant_context(session: AsyncSession, tenant_id: int):
    """Set tenant context for Row-Level Security."""
    await session.execute(f"SET app.current_tenant = {tenant_id}")


async def init_database():
    """Initialize database and create tables."""
    from .models import Base
    
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Enable Row-Level Security
        await conn.execute("""
            -- Enable RLS on tables
            ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
            ALTER TABLE users ENABLE ROW LEVEL SECURITY;
            ALTER TABLE catalog_items ENABLE ROW LEVEL SECURITY;
            ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
            ALTER TABLE kb_documents ENABLE ROW LEVEL SECURITY;
            ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
            ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
            ALTER TABLE usage_stats ENABLE ROW LEVEL SECURITY;
            
            -- Create RLS policies
            CREATE POLICY tenant_isolation ON tenants FOR ALL TO authenticated USING (id = current_setting('app.current_tenant')::int);
            CREATE POLICY tenant_isolation ON users FOR ALL TO authenticated USING (tenant_id = current_setting('app.current_tenant')::int);
            CREATE POLICY tenant_isolation ON catalog_items FOR ALL TO authenticated USING (tenant_id = current_setting('app.current_tenant')::int);
            CREATE POLICY tenant_isolation ON orders FOR ALL TO authenticated USING (tenant_id = current_setting('app.current_tenant')::int);
            CREATE POLICY tenant_isolation ON kb_documents FOR ALL TO authenticated USING (tenant_id = current_setting('app.current_tenant')::int);
            CREATE POLICY tenant_isolation ON profiles FOR ALL TO authenticated USING (tenant_id = current_setting('app.current_tenant')::int);
            CREATE POLICY tenant_isolation ON conversations FOR ALL TO authenticated USING (tenant_id = current_setting('app.current_tenant')::int);
            CREATE POLICY tenant_isolation ON usage_stats FOR ALL TO authenticated USING (tenant_id = current_setting('app.current_tenant')::int);
            
            -- Create role for application
            CREATE ROLE authenticated;
        """)


async def close_database():
    """Close database connections."""
    await engine.dispose()
