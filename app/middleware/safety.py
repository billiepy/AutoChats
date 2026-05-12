import time
from typing import Dict, Optional
from dataclasses import dataclass
from loguru import logger

@dataclass
class SafetyCheckResult:
    allowed: bool
    reason: str
    cooldown_until: Optional[float] = None

class SafetyMiddleware:
    def __init__(self):
        self.last_replies: Dict[int, list[float]] = {}  # chat_id -> timestamps
        self.last_reply_time: Dict[int, float] = {}     # chat_id -> last reply
        self.daily_replies: Dict[int, int] = {}         # chat_id -> daily count
        
    def check(self, chat_id: int, message: str) -> SafetyCheckResult:
        now = time.time()
        
        # Rate limiting (max 3/hour per group)
        recent_replies = self.last_replies.get(chat_id, [])
        recent_replies = [t for t in recent_replies if now - t < 3600]
        
        if len(recent_replies) >= 3:
            logger.debug(f"Rate limit hit for chat {chat_id}")
            return SafetyCheckResult(False, "rate_limited")
        
        # Daily cap
        daily_count = self.daily_replies.get(chat_id, 0)
        if daily_count >= 25:
            return SafetyCheckResult(False, "daily_cap")
        
        # Message length
        if len(message) > 250 or len(message.split()) > 40:
            return SafetyCheckResult(False, "too_long")
        
        # Cooldown between replies (min 8 mins)
        last_time = self.last_reply_time.get(chat_id, 0)
        if now - last_time < 480:  # 8 minutes
            return SafetyCheckResult(False, "cooldown")
        
        return SafetyCheckResult(True, "allowed")
    
    def record_reply(self, chat_id: int):
        now = time.time()
        if chat_id not in self.last_replies:
            self.last_replies[chat_id] = []
        self.last_replies[chat_id].append(now)
        self.last_reply_time[chat_id] = now
        self.daily_replies[chat_id] = self.daily_replies.get(chat_id, 0) + 1
        
        # Cleanup old timestamps
        self.last_replies[chat_id] = [
            t for t in self.last_replies[chat_id] 
            if now - t < 86400  # 24 hours
        ]
