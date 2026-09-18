\"\"\"Netrava Configuration & Settings.

Supports environment overrides for Hackathon, Demo, and Production environments.
\"\"\"

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = \"Netrava Video Intelligence Fabric\"
    VERSION: str = \"1.0.0\"
    API_V1_STR: str = \"/api/v1\"
    APP_MODE: str = Field(default=\"hackathon\", description=\"hackathon, demo, or production\")
    
    # Security & Auth
    SECRET_KEY: str = \"netrava_super_secret_jwt_key_gujarat_police_2026_change_in_prod\"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for control room operators
    ALGORITHM: str = \"HS256\"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        \"http://localhost:3000\",
        \"http://127.0.0.1:3000\",
        \"http://localhost:8000\",
        \"http://127.0.0.1:8000\",
    ]
    
    # Database
    # Defaults to SQLite for local zero-dependency run, or PostgreSQL+PostGIS when available
    DATABASE_URL: str = Field(
        default=\"sqlite+aiosqlite:///./netrava.db\",
        description=\"Async database connection string\"
    )
    
    # Redis Cache & PubSub
    REDIS_URL: str = \"redis://localhost:6379/0\"
    
    # Media Gateway (MediaMTX)
    MEDIAMTX_API_URL: str = \"http://localhost:9997\"
    MEDIAMTX_RTSP_HOST: str = \"localhost:8554\"
    MEDIAMTX_HLS_HOST: str = \"localhost:8888\"
    MEDIAMTX_WEBRTC_HOST: str = \"localhost:8889\"
    
    # Object Storage (MinIO / S3)
    MINIO_ENDPOINT: str = \"localhost:9000\"
    MINIO_ACCESS_KEY: str = \"netrava_admin\"
    MINIO_SECRET_KEY: str = \"netrava_secret_key_2026\"
    MINIO_BUCKET_EVIDENCE: str = \"netrava-evidence\"
    EVIDENCE_LOCAL_STORAGE_DIR: str = \"./data/evidence\"
    
    # Default Reference District
    DEFAULT_STATE: str = \"Gujarat\"
    DEFAULT_REFERENCE_DISTRICT: str = \"Ahmedabad\"

    class Config:
        case_sensitive = True
        env_file = \".env\"
        extra = \"allow\"


settings = Settings()
