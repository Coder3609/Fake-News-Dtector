from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    PORT: int = 8010
    LOG_LEVEL: str = "info"
    
    # Supabase Credentials
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE: str = ""
    
    # Redis Configuration
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""
    
    # AI API Keys
    GEMINI_API_KEY: str = "mock-gemini-api-key"
    TAVILY_API_KEY: str = "mock-tavily-api-key"
    
    model_config = ConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding='utf-8',
        extra="ignore"
    )

settings = Settings()
