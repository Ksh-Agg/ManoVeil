from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    environment: str = "development"
    app_name: str = "ManoVeil"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://manoveil:manoveil@localhost:5432/manoveil"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    # AI/ML
    hf_model_id: str = "distilbert-base-uncased-finetuned-sst-2-english"
    openai_api_key: str = ""
    shap_enabled: bool = True

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Blockchain / FL
    fabric_peer_endpoint: str = "grpc://localhost:7051"
    fabric_orderer_endpoint: str = "grpc://localhost:7050"
    fabric_channel_name: str = "manoveil-channel"
    fabric_chaincode_name: str = "manoveil-gradient"
    fl_aggregator_url: str = "http://localhost:8081"
    dp_epsilon: float = 0.8
    he_key_bits: int = 2048
    ipfs_node_url: str = "http://localhost:5001"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
