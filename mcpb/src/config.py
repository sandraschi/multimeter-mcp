from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BackendPreference = Literal["auto", "simulator", "scpi_serial"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MULTIMETER_MCP_", extra="ignore")

    backend: BackendPreference = "auto"
    port: int = 11005
    webapp_port: int = 11006
    work_dir: Path = Path("./data")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
