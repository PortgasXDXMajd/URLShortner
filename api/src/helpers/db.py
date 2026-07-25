
import random
from config import get_setting
from psycopg_pool import AsyncConnectionPool

settings = get_setting()

# one write pool for the leader
write_pool = AsyncConnectionPool(
    settings.pg_primary_connection_string,
    min_size=settings.pool_min,
    max_size=settings.pool_max,
    open=False
)

# a read pool for each replica
read_pools = [ 
    AsyncConnectionPool(
        pg_read_replica_connection_string,
        min_size=settings.pool_min,
        max_size=settings.pool_max,
        open=False
    ) for pg_read_replica_connection_string in settings.pg_read_replicas_connection_string 
]

async def open_connections_async():
    await write_pool.open()
    for rp in read_pools: 
        await rp.open()

def _get_read_pool() -> tuple[AsyncConnectionPool, str]:
    if not read_pools: return (write_pool, "primary")
    return (random.choice(read_pools), "replica")


async def get_writer_async():
    async with write_pool.connection() as c:
        yield c

async def get_reader_async():
    pool, name = _get_read_pool()
    async with pool.connection() as c:
        yield c, name
