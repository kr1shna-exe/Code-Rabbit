from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    github_token: str
    github_webhook_secret: str
    github_bot_token: str
    github_app_id: int
    github_app_slug: str 
    github_app_private_key_path: str
    gemini_api_key: str
    groq_api_key: str
    zai_api_key: str = ""
    ai_provider: str = "groq"
    temp_repo_dir: str = "./temp_repos"
    port: int = 8000


settings = Settings()

