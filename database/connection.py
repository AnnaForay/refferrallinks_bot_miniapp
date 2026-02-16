import asyncpg
import os

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            dsn=os.environ.get('DATABASE_URL'),
            min_size=1,
            max_size=10
        )
    
    async def fetch(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchval(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def close(self):
        await self.pool.close()

db = Database()
