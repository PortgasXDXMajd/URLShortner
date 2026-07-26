from functools import cached_property, lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    instance_id: str = "api-?"
    pg_primary_connection_string: str = ""
    pg_read_replicas_connection_string: str = ""
    pool_min : int = 2
    pool_max : int = 20
    pool_timeout : float = 2.0
    pool_max_waiting : int = 100

    redis_connection_string : str = ""
    link_cache_ttl : int = 86400
    click_flush_interval : float = 1.0
    click_flush_batch : int = 5000

    @cached_property
    def replica_dsns(self) -> list[str]:
        raw = self.pg_read_replicas_connection_string
        return [cs.strip() for cs in raw.split(",") if cs.strip()]

@lru_cache
def get_setting() -> Settings:
    return Settings()
