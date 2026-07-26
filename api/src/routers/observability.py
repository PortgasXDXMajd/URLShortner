
from fastapi import APIRouter, Depends
from helpers.db import get_writer_async
from config import get_setting

settings = get_setting()
router = APIRouter(prefix="/api/observability", tags=["observability"])

@router.get("/health")
async def health():
    return {"healthy": True, "instance_id": settings.instance_id}


@router.get("/whoami")
async def whoami(c=Depends(get_writer_async)):
    res = await c.execute("SELECT inet_server_addr()::text, pg_is_in_recovery()")
    r = await res.fetchone()

    return {
        "api": settings.instance_id,
        "db_host": r[0],
        "db_in_recovery": r[1]
    }

