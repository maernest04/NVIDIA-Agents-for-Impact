from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "NVIDIA Agents for Impact"
    debug: bool = False
    nvidia_api_key: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
