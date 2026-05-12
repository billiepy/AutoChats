import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Message
from loguru import logger
from app.behavior.timing import HumanTiming
from app.middleware.safety import SafetyMiddleware
from app.services.context import ContextEngine
from app.ai.client import AIClient
from app.ai.prompts import PromptBuilder
from app.database.manager import DatabaseManager
from app.config import settings

class MessageHandler:
    def __init__(
        self,
        client: TelegramClient,
        db: DatabaseManager,
        ai_client: AIClient,
        safety: SafetyMiddleware
    ):
        self.client = client
        self.db = db
        self.ai = ai_client
        self.safety = safety
        self.context_engine = ContextEngine(db)
        
        self.register_handlers()
    
    def register_handlers(self):
        @self.client.on(events.NewMessage(chats=None))
        async def handle_message(event: events.NewMessage.Event):
            await self.process_message(event.message)
    
    async def process_message(self, message: Message):
        try:
            chat_id = message.chat_id
            if not isinstance(chat_id, int) or chat_id < 0:
                return
            
            # Save message to DB
            msg_data = {
                "chat_id": chat_id,
                "message_id": message.id,
                "sender_id": message.sender_id,
                "sender_name": (await message.get_sender()).username or "user",
                "text": message.text or "",
                "timestamp": message.date
            }
            await self.db.save_message(msg_data)
            
            # Ignore non-text, own messages, short messages
            if not message.text or len(message.text.strip()) < 3:
                return
            
            # Safety checks
            if await self.db.is_on_cooldown(chat_id):
                logger.debug(f"Chat {chat_id} on cooldown")
                return
            
            safety_result = self.safety.check(chat_id, message.text)
            if not safety_result.allowed:
                logger.debug(f"Safety blocked chat {chat_id}: {safety_result.reason}")
                return
            
            # Human-like reply decision
            if not HumanTiming.should_reply(settings.reply_probability):
                logger.trace(f"Skipped reply (probability) chat {chat_id}")
                return
            
            # Build context and generate response
            await self.generate_and_send_reply(chat_id, message)
            
        except Exception as e:
            logger.error(f"Message handler error: {e}")
    
    async def generate_and_send_reply(self, chat_id: int, trigger_message: Message):
        try:
            # Human reading delay
            reading_time = HumanTiming.reading_delay(trigger_message.text)
            await asyncio.sleep(reading_time)
            
            # Build context
            context = await self.context_engine.build_context(chat_id, {
                "text": trigger_message.text,
                "sender": (await trigger_message.get_sender()).username or "user"
            })
            
            # Generate AI response
            prompt = PromptBuilder.build_conversation_prompt(
                context["recent_messages"],
                context["group_style"],
                trigger_message.text
            )
            
            response_text = await self.ai.generate_response(prompt)
            if not response_text or len(response_text) > settings.message_max_length:
                return
            
            # Typing simulation
            if settings.typing_simulation:
                await asyncio.sleep(2)  # Start typing delay
            
            # Final human delay
            final_delay = HumanTiming.random_delay(
                settings.min_reply_delay, 
                settings.max_reply_delay
            )
            await asyncio.sleep(final_delay)
            
            # Send reply
            await self.client.send_message(
                chat_id,
                response_text,
                reply_to=trigger_message.id
            )
            
            logger.info(f"Replied in chat {chat_id}: {response_text[:50]}...")
            
            # Record for safety
            self.safety.record_reply(chat_id)
            
        except Exception as e:
            logger.error(f"Reply generation failed: {e}")
