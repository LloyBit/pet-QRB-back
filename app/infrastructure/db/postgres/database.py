from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings

DATABASE_URL = settings.db_url.replace("postgresql://", "postgresql+asyncpg://")

# Configure the engine with connection pooling for async
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,  # Reduced pool size for better management
    max_overflow=20,  # Additional connections that can be created beyond pool_size
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
)

# Create session factory with pool configuration
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    '''
    Dependency function for FastAPI to inject database sessions
    
    This uses connection pooling for better performance and resource management.
    Sessions are automatically managed by FastAPI's dependency injection system.
    '''
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Optional: Function to get session pool stats
async def get_pool_stats():
    """Get connection pool statistics for monitoring"""
    try:
        checked_in = engine.pool.checkedin()
        checked_out = engine.pool.checkedout()
        pool_size = engine.pool.size()
        overflow = engine.pool.overflow()
        
        return {
            "pool_size": pool_size,
            "checked_in": max(0, checked_in),
            "checked_out": max(0, checked_out),
            "overflow": max(0, overflow),
            "pool_status": "active",
            "total_connections": checked_in + checked_out,
            "available_connections": max(0, checked_in),
            "busy_connections": max(0, checked_out),
            "pool_utilization": f"{((checked_out / pool_size) * 100):.1f}%" if pool_size > 0 else "0%",
            "overflow_usage": f"{((overflow / pool_size) * 100):.1f}%" if pool_size > 0 and overflow > 0 else "0%"
        }
    except Exception as e:
        return {
            "pool_size": 0,
            "checked_in": 0,
            "checked_out": 0,
            "overflow": 0,
            "pool_status": "error",
            "error": str(e)
        }
