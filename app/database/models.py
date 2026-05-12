from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Message(BaseModel):
    chat_id: int
    message_id: int
    sender_id: int
    sender_name: str
    text: str
    timestamp: datetime
    reply_to: Optional[int] = None

class GroupProfile(BaseModel):
    chat_id: int
    title: str
    member_count: int
    language: str = "mixed"
    emoji_density: str = "medium"
    tone: str = "casual"
    slang_level: str = "medium"
    avg_sentence_length: float = 12.0
    last_updated: datetime
    message_count: int = 0

class Cooldown(BaseModel):
    chat_id: int
    expires_at: datetime
    reason: str

class Memory(BaseModel):
    chat_id: int
    summary: str
    topics: List[str]
    created_at: datetime
