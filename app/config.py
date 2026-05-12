from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    # Telegram
    api_id: int = Field(..., env="API_ID")
    api_hash: str = Field(..., env="API_HASH")
    session_name: str = Field("userbot_session", env="SESSION_NAME")
    
    # OpenRouter AI
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    ai_model: str = Field("anthropic/claude-3.5-sonnet", env="AI_MODEL")
    ai_temperature: float = Field(0.85, env="AI_TEMPERATURE")
    max_tokens: int = Field(120, env="MAX_TOKENS")
    
    # Database
    mongo_uri: str = Field("mongodb://mongodb:27017", env="MONGO_URI")
    db_name: str = Field("userbot", env="DB_NAME")
    
    # Behavior Engine
    reply_probability: float = Field(0.12, env="REPLY_PROBABILITY")
    min_reply_delay: int = Field(8, env="MIN_REPLY_DELAY")
    max_reply_delay: int = Field(45, env="MAX_REPLY_DELAY")
    typing_simulation: bool = Field(True, env="TYPING_SIMULATION")
    max_replies_per_hour: int = Field(3, env="MAX_REPLIES_PER_HOUR")
    
    # Safety Limits
    flood_wait_max: int = Field(3600, env="FLOOD_WAIT_MAX")
    engagement_cap_daily: int = Field(25, env="ENGAGEMENT_CAP_DAILY")
    message_max_length: int = Field(250, env="MESSAGE_MAX_LENGTH")
    
    class Config:
        env_file = ".env"

settings = Settings()
