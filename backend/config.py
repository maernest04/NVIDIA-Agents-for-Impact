from pathlib import Path

from pydantic_settings import BaseSettings

# .env lives at the repo root, one level above this file
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "SJSU Safeline"
    debug: bool = False
    nemotron_api_key: str = ""
    nemotron_base_url: str = "https://integrate.api.nvidia.com/v1"

    model_config = {"env_file": str(_ENV_FILE)}


settings = Settings()
