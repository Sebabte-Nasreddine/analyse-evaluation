"""
Configuration centralisée pour l'application
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Formation Evaluation Analysis"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/evaluation_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # NLP Models Configuration
    MODEL_CACHE_DIR: str = "./models_cache"
    
    # Modèles par langue
    FRENCH_SENTIMENT_MODEL: str = "cmarkea/distilcamembert-base-sentiment"
    ARABIC_SENTIMENT_MODEL: str = "CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment"
    DARIJA_MODEL: str = "SI2M-Lab/DarijaBERT"
    
    # Topic modeling
    USE_BERTOPIC: bool = True
    MIN_TOPIC_SIZE: int = 5
    
    # Clustering
    CLUSTERING_METHOD: str = "kmeans"  # kmeans, dbscan
    MIN_CLUSTER_SIZE: int = 5
    
    # Nombre de clusters
    MAX_CLUSTERS: int = 10  # Max testé par auto-détection
    DEFAULT_N_CLUSTERS: Optional[int] = 3  # Force 3 clusters au lieu d'auto-détection instead of auto-detection
    
    # File upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".pdf", ".xlsx"]
    
    # Processing
    BATCH_SIZE: int = 32
    MAX_WORKERS: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Retourne une instance singleton des settings"""
    return Settings()


# Instance globale
settings = get_settings()
