from helpers import db
from fastapi import FastAPI
from routers import observability, link
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.open_connections_async()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(observability.router)
app.include_router(link.router)