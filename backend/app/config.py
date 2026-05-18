from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database — must use asyncpg driver prefix for SQLAlchemy async
    DATABASE_URL: str = "postgresql+asyncpg://threatshield:ThreatShield2024!@postgres:5432/threatshield_db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # CORS — comma-separated list of allowed origins
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # GeoIP database path (MaxMind GeoLite2-City.mmdb)
    GEOIP_DB_PATH: str = "/app/geoip/GeoLite2-City.mmdb"

    # Log file paths (mounted from shared Docker volume)
    COWRIE_LOG_PATH: str = "/cowrie-logs/cowrie.json"
    WEB_LOGIN_LOG_PATH: str = "/cowrie-logs/web-login.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
