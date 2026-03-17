from pathlib import Path

from pydantic_settings import BaseSettings

# .env lives alongside this file in the backend/ directory
_ENV_FILE = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    app_name: str = "NVIDIA Agents for Impact"
    debug: bool = False
    nemotron_api_key: str = ""
    nemotron_base_url: str = "https://integrate.api.nvidia.com/v1"

    model_config = {"env_file": str(_ENV_FILE)}


settings = Settings()
