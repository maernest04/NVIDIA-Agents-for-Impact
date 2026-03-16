from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "NVIDIA Agents for Impact"
    debug: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
