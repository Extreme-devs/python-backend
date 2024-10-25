from pydantic_settings import BaseSettings
import requests_cache

requests_cache.install_cache("demo_cache")


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    OPENAI_API_KEY: str
    QDRANT_API_KEY: str
    QDRANT_HOST: str
    JWT_SECRET_KEY: str
    GOOGLE_CSE_ID: str
    GOOGLE_API_KEY: str
    SERPER_API_KEY: str

    TRIPADVISER_API_KEY: str
    GOOGLEMAPS_API_KEY: str
    WEATHER_API_KEY: str
    
    SUPABASE_PROJECT_URL: str
    SUPABASE_ANON_KEY: str
    
    class Config:
        env_file = ".env"


settings = Settings()
