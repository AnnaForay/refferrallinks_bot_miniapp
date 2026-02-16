import asyncpg
import logging
from config import DATABASE_DSN

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                dsn=DATABASE_DSN,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("✅ Подключение к PostgreSQL успешно установлено")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к БД: {e}")
            raise

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("✅ Подключение к PostgreSQL закрыто")

# Глобальный экземпляр
db = Database()

__all__ = ['db']
