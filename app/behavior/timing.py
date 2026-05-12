import random
import asyncio
import time
from typing import Optional
from loguru import logger

class HumanTiming:
    @staticmethod
    def random_delay(min_secs: int, max_secs: int) -> float:
        """Random delay with human-like distribution"""
        return random.uniform(min_secs, max_secs)
    
    @staticmethod
    def reading_delay(message_length: int) -> float:
        """Time to read message (human reading speed ~250 wpm)"""
        words = len(message_length.split()) if isinstance(message_length, str) else message_length // 5
        return random.uniform(words * 0.15, words * 0.35)
    
    @staticmethod
    async def simulate_typing(client, chat_id: int, message_length: int):
        """Simulate realistic typing"""
        typing_duration = max(1.5, message_length * 0.08)
        await client.send(ReadMessageCallback(chat_id))
        await asyncio.sleep(typing_duration)
    
    @staticmethod
    def should_reply(probability: float) -> bool:
        """Weighted random decision with human-like bias"""
        if random.random() > probability:
            return False
        
        # Additional human-like randomness
        if random.random() < 0.3:  # 30% chance to override and skip
            return False
            
        return True
