import asyncio

from helpers import cache, db
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from psycopg_pool import PoolTimeout, TooManyRequests
from routers import observability, link
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.open_connections_async()
    flusher = asyncio.create_task(cache.click_flusher())
    yield
    flusher.cancel()

app = FastAPI(lifespan=lifespan)

# pool exhausted -> shed load with a 503 instead of queueing requests
@app.exception_handler(PoolTimeout)
@app.exception_handler(TooManyRequests)
async def pool_exhausted(request, exc):
    return JSONResponse(status_code=503, content={"detail": "database busy, try again"})

app.include_router(observability.router)
app.include_router(link.router)