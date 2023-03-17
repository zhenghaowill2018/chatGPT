import asyncio
from aiomysql import create_pool, Pool,Connection, DictCursor, Cursor

from typing import Dict,Tuple

class MysqlDB:

    """
    aiomysql封装
    loop = asyncio.get_running_loop()
    mysql = MysqlDB(mysql_info, loop=loop)
    await mysql.setup()
    await mysql.pool
    res = await mysql.find_one('SELECT NOW();')
    """

    def __init__(self, mysql_url:Dict[str,str],loop:asyncio.AbstractEventLoop=None):
        self.mysql_url = mysql_url
        self.loop = loop if loop else asyncio.get_running_loop()
        self._pool:Pool

    async def setup(self)->None:
        self._pool = await create_pool(**self.mysql_url)


    @property
    async def pool(self)->Pool:
        for _ in range(180):
            if self._pool:
                return self._pool
            await asyncio.sleep(1)

        raise ValueError('始终无法链接pg数据库: %s'%self.mysql_url)


    async def close(self)->None:
        self._pool.close()
        await self._pool.wait_closed()


    async def find_one(self, sql:str, args:Tuple[str]=None)->None:
        conn:Connection
        cursor:Cursor
        async with self._pool.acquire() as conn:
            await conn.ping()
            async with conn.cursor(DictCursor) as cursor:
                await cursor.execute(sql, args)
                return await cursor.fetchone()


    async def find(self, sql:str, args:Tuple[str]=None)->None:
        conn:Connection
        cursor:Cursor
        async with self._pool.acquire() as conn:
            await conn.ping()
            async with conn.cursor(DictCursor) as cursor:
                await cursor.execute(sql, args)
                return await cursor.fetchall()


    async def execute(self, query:str, args:Tuple[str]=None)->None:
        conn:Connection
        cursor:Cursor
        async with self._pool.acquire() as conn:
            await conn.ping()
            async with conn.cursor(DictCursor) as cursor:
                count = await cursor.execute(query, args)
                await conn.commit()
                return count


    async def execute_many(self, query:str, args:Tuple[str]=None)->None:
        conn:Connection
        cursor:Cursor
        async with self._pool.acquire() as conn:
            await conn.ping()
            async with conn.cursor(DictCursor) as cursor:
                count = await cursor.executemany(query, args)
                await conn.commit()
                return count
