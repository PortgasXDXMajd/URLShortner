
import asyncio
import logging
from datetime import datetime, timezone

from redis.asyncio import Redis
from config import get_setting

settings = get_setting()
log = logging.getLogger("cache")

LINK_KEY = "link:{}"
CLICKS_BUFFER = "clicks_buffer"

# short socket timeouts so a dead redis costs ~200ms once, not a hung hot path
redis: Redis | None = (
    Redis.from_url(
        settings.redis_connection_string,
        decode_responses=True,
        socket_connect_timeout=0.2,
        socket_timeout=0.5,
    ) if settings.redis_connection_string else None
)

async def get_link(token: str) -> str | None:
    if redis is None: return None
    try:
        return await redis.get(LINK_KEY.format(token))
    except Exception:
        return None

async def set_link(token: str, target_url: str):
    if redis is None: return
    try:
        await redis.set(LINK_KEY.format(token), target_url, ex=settings.link_cache_ttl)
    except Exception:
        pass

async def push_click(token: str) -> bool:
    """True if buffered; on False the caller must write the click itself."""
    if redis is None: return False
    try:
        now = datetime.now(timezone.utc).isoformat()
        await redis.rpush(CLICKS_BUFFER, f"{token}|{now}")
        return True
    except Exception:
        return False

async def _flush_clicks_once() -> int:
    if redis is None: return 0
    entries = await redis.lpop(CLICKS_BUFFER, settings.click_flush_batch)
    if not entries: return 0

    rows = [(token, ts) for token, _, ts in (e.partition("|") for e in entries)]
    from helpers import db
    try:
        async with db.write_connection() as c:
            await c.cursor().executemany(
                "INSERT INTO clicks (url_token, clicked_at) VALUES (%s, %s::timestamptz)",
                rows)
    except Exception:
        # postgres refused the batch: put it back so it is retried next tick
        await redis.rpush(CLICKS_BUFFER, *entries)
        raise
    return len(entries)

async def click_flusher():
    """Per-worker background task: drain the click buffer into postgres."""
    if redis is None: return
    while True:
        await asyncio.sleep(settings.click_flush_interval)
        try:
            # keep draining while full batches come back
            while await _flush_clicks_once() == settings.click_flush_batch:
                pass
        except Exception as e:
            log.warning("click flush failed, will retry: %s", e)
