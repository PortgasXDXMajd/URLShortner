from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    instance_id: str = "api-?"
    pg_primary_connection_string: str = ""
    pg_read_replicas_connection_string: list[str] = []
    pool_min : int = 2
    pool_max : int = 20          
    pool_timeout : float = 2.0   
    pool_max_waiting : int = 100 

    @field_validator("pg_read_replicas_connection_string", mode="before")
    @classmethod
    def split_csv(cls, v):
        if isinstance(v, str):
            return [ cs.strip() for cs in v.split(",") if cs.strip() != None or "" ]
        return v

@lru_cache
def get_setting() -> Settings:
    return Settings()
