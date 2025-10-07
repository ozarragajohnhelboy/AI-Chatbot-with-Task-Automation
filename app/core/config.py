from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "AI Chatbot with Task Automation"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    SECRET_KEY: str
    OPENAI_API_KEY: str = ""
    
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    LOG_LEVEL: str = "INFO"
    
    INTENT_MODEL_PATH: str = "models/saved_models/intent_classifier.keras"
    ENTITY_MODEL_PATH: str = "models/saved_models/entity_extractor.keras"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    MAX_CONVERSATION_HISTORY: int = 50
    CONVERSATION_MEMORY_WINDOW: int = 10
    
    TASK_TIMEOUT: int = 300
    MAX_CONCURRENT_TASKS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

