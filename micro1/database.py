from logger import log
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from settings import settings
import asyncpg


# from schema import DeclarativeBase, CounterName


class DatabaseController:
    def __init__(self):
        log.info(f"Setting connect to database to {settings.database_user}:{settings.database_pwd}@{settings.database_host}/{settings.database_name}'")
        self.engine = create_async_engine(
            # f"postgresql+asyncpg://postgres:postgres@postgresMainApp:15432/postgres",
            f"postgresql+asyncpg://{settings.database_user}:{settings.database_pwd}@{settings.database_host}/{settings.database_name}",
            echo=False)
        log.info(self.engine)
        self.AsyncSession = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def health_check(self):
        async with self.AsyncSession.begin() as session:
            try:
                select_count_result = await session.execute('SELECT 1')
                select_count_result.first()
                log.info("Database connection is set")
            except Exception as e:
                log.info(f"{type(e)}")
                log.info(f"database connection error - {e}")

    def get_session(self) -> AsyncSession:
        log.debug("Create session")
        session = self.AsyncSession  # возвращаем объект sessionmaker
        try:
            log.debug("Return session")
            yield session
        except Exception as e:
            log.debug(f"UNHANDLED {e}")

    async def close_db(self):
        await self.AsyncSession.close_all()


controller = DatabaseController()
