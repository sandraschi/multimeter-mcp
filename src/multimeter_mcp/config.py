from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MULTIMETER_MCP_", extra="ignore")
    backend: str = "simulator"
    port: int = 11005
    webapp_port: int = 11006
    work_dir: Path = Path("./data")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
