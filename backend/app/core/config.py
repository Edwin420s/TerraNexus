from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "TerraNexus API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    
    # Authoritative store: PostgreSQL with PostGIS in production, SQLite in memory or local file for test/fallback
    database_url: str = "sqlite:///./terranexus.db"
    
    # Redis for caching, pub/sub, rate limiting
    redis_url: str = "redis://localhost:6379/0"
    
    # Mosquitto MQTT Broker
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_keepalive: int = 60
    mqtt_username: str = ""
    mqtt_password: str = ""
    
    # Security & JWT Auth
    jwt_secret: str = "terranexus-insecure-secret-key-change-in-production-2026"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440 # 24 hours
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # QVAC Local AI endpoint
    qvac_endpoint: str = "http://localhost:8080/v1/qvac"

settings = Settings()
