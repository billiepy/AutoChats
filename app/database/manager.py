import motor.motor_asyncio
from typing import List, Optional, Dict
from loguru import logger
from app.config import settings
from app.database.models import (
    Message, GroupProfile, Cooldown, Memory
)

class DatabaseManager:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
        self.db = self.client[settings.db_name]
        
        # Collections
        self.messages = self.db.messages
        self.groups = self.db.groups
        self.cooldowns = self.db.cooldowns
        self.memories = self.db.memories
        self.analytics = self.db.analytics
        
        self._create_indexes()
    
    async def _create_indexes(self):
        # Messages
        await self.messages.create_index("chat_id")
        await self.messages.create_index([("chat_id", 1), ("timestamp", -1)])
        
        # Cooldowns TTL (24h)
        await self.cooldowns.create_index("expires_at", expireAfterSeconds=0)
        
        # Groups
        await self.groups.create_index("chat_id", unique=True)
    
    async def save_message(self, message: Message):
        await self.messages.insert_one(message.dict())
    
    async def get_recent_messages(self, chat_id: int, limit: int = 20) -> List[Dict]:
        cursor = self.messages.find(
            {"chat_id": chat_id}
        ).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_group_profile(self, chat_id: int) -> Optional[GroupProfile]:
        group = await self.groups.find_one({"chat_id": chat_id})
        return GroupProfile(**group) if group else None
    
    async def update_group_profile(self, profile: GroupProfile):
        await self.groups.replace_one(
            {"chat_id": profile.chat_id},
            profile.dict(),
            upsert=True
        )
    
    async def set_cooldown(self, chat_id: int, duration_secs: int, reason: str):
        cooldown = Cooldown(
            chat_id=chat_id,
            expires_at=datetime.utcnow().timestamp() + duration_secs,
            reason=reason
        )
        await self.cooldowns.insert_one(cooldown.dict())
    
    async def is_on_cooldown(self, chat_id: int) -> bool:
        cooldown = await self.cooldowns.find_one({"chat_id": chat_id})
        if cooldown and cooldown["expires_at"] > datetime.utcnow().timestamp():
            return True
        return False
