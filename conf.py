from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini/gemini-2.0-flash"
    SERPER_API_KEY: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    MONGO_URI: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
