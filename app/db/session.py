# app/db/session.py

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from app.config import db_settings
from contextlib import asynccontextmanager

# ✅ Create engine
engine: AsyncEngine = create_async_engine(
    db_settings.MYSQL_URL,
    echo=True,
    future=True,
)

# ✅ Create sessionmaker once (correct usage for AsyncSession)
async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# ✅ Properly typed async generator return
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session