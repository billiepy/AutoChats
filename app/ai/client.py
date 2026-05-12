import openai
import asyncio
from typing import Optional, Dict, Any
from loguru import logger
from app.config import settings
from app.utils.logger import logger

class AIClient:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = settings.ai_model
        self.temperature = settings.ai_temperature
        self.max_tokens = settings.max_tokens
    
    async def generate_response(
        self, 
        messages: list[Dict[str, str]], 
        timeout: float = 30.0
    ) -> Optional[str]:
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=0.9,
                ),
                timeout=timeout
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"AI generated {len(content)} chars (model: {self.model})")
            return content
            
        except asyncio.TimeoutError:
            logger.error("AI generation timeout")
            return None
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return None
