import asyncio
import uvloop
import signal
import sys
from pathlib import Path
from loguru import logger
from telethon import TelegramClient
from telethon.sessions import StringSession

from app.config import settings
from app.utils.logger import setup_logger
from app.database.manager import DatabaseManager
from app.ai.client import AIClient
from app.middleware.safety import SafetyMiddleware
from app.handlers.message import MessageHandler
from app.services.context import ContextEngine

async def main():
    # Setup
    logger.info("Starting AI Telegram Userbot...")
    Path("./sessions").mkdir(exist_ok=True)
    Path("./logs").mkdir(exist_ok=True)
    
    # Initialize components
    db = DatabaseManager()
    ai_client = AIClient()
    safety = SafetyMiddleware()
    
    # Telegram client
    client = TelegramClient(
        settings.session_name,
        settings.api_id,
        settings.api_hash,
        timeout=30
    )
    
    # Register handlers
    handler = MessageHandler(client, db, ai_client, safety)
    
    # Graceful shutdown
    def signal_handler():
        logger.info("Shutdown signal received")
        asyncio.create_task(client.disconnect())
    
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(shutdown()))
    signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(shutdown()))
    
    async def shutdown():
        logger.info("Shutting down...")
        await client.disconnect()
        sys.exit(0)
    
    # Connect and run
    await client.start()
    logger.info(f"Userbot connected as {await client.get_me()}")
    
    # Health check server
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "client": "connected"}
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="error")
    server = uvicorn.Server(config)
    
    await asyncio.gather(
        client.run_until_disconnected(),
        server.serve()
    )

if __name__ == "__main__":
    uvloop.install()
    asyncio.run(main())
