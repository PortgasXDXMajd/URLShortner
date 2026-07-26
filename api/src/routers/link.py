
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse

from config import get_setting
from helpers.url_token_generator import get_url_token
from helpers import cache
from helpers.db import get_reader_async, get_writer_async, read_connection, write_connection

settings = get_setting()

router = APIRouter(tags=["links"])

class NewLink(BaseModel):
    url: str

@router.post(path="/links", status_code=201)
async def create(body: NewLink,resp: Response, c=Depends(get_writer_async)):
    url_token = get_url_token()

    await c.execute("INSERT INTO links (url_token, target_url) VALUES (%s, %s)",(url_token, body.url))
    row = await (await c.execute("SELECT pg_current_wal_lsn()::text")).fetchone()

    resp.headers['X-Served-By'] = settings.instance_id
    resp.headers['X-DB-Role'] = "primary"
    resp.headers['X-WRITE-LSN'] = row[0]

    return {"url_token": url_token, "target_url": body.url}


@router.get(path="/{s}", status_code=302, response_class=RedirectResponse)
async def get(s: str):
    if not s:
        raise HTTPException(400, "url_token is empty")

    target, role = await cache.get_link(s), "cache"
    if target is None:
        async with read_connection() as (c, role):
            row = await (await c.execute("SELECT target_url from links WHERE url_token=%s", (s,))).fetchone()
        if row is not None and row[0]:
            target = row[0]
            await cache.set_link(s, target)

    if not target:
        raise HTTPException(404, "url_token was not found")

    # buffer the click in redis; fall back to a direct insert if redis is down
    if not await cache.push_click(s):
        async with write_connection() as w:
            await w.execute("INSERT INTO clicks (url_token) VALUES (%s)", (s,))

    return RedirectResponse(target, status_code=302, headers={
        'X-Served-By': settings.instance_id,
        'X-DB-Role': role,
    })

@router.get("/links/{s}/stats")
async def stats(s: str, resp: Response, r=Depends(get_reader_async)):
    row = await (await r[0].execute("SELECT count(*) FROM clicks WHERE url_token=%s", (s,))).fetchone()

    resp.headers["X-Served-By"] = settings.instance_id
    resp.headers["X-DB-Role"] = r[1]

    return {
        "url_token": s,
        "clicks": row[0]
    }