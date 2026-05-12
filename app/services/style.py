from typing import Dict, Any, List
from collections import Counter
import re
from app.database.models import Message

class StyleAnalyzer:
    def __init__(self, messages: List[Dict]):
        self.messages = messages
    
    def analyze(self) -> Dict[str, Any]:
        if not self.messages:
            return {"language": "mixed", "emoji_density": "medium"}
        
        texts = [msg.get('text', '') for msg in self.messages]
        combined_text = " ".join(texts)
        
        return {
            "language": self._detect_language(combined_text),
            "emoji_density": self._emoji_density(combined_text),
            "tone": self._detect_tone(texts),
            "sentence_length": self._avg_sentence_length(texts),
            "grammar": self._grammar_quality(texts),
            "slang": self._slang_level(combined_text),
        }
    
    def _detect_language(self, text: str) -> str:
        hindi_chars = re.findall(r'[\u0900-\u097F]', text)
        eng_ratio = len(text.split()) / max(1, len(text))
        hindi_ratio = len(hindi_chars) / max(1, len(text))
        
        if hindi_ratio > 0.3:
            return "hinglish"
        elif hindi_ratio > 0.1:
            return "mixed"
        return "english"
    
    def _emoji_density(self, text: str) -> str:
        emojis = re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]', text)
        density = len(emojis) / max(1, len(re.findall(r'\w+', text)))
        if density > 0.15: return "high"
        elif density > 0.05: return "medium"
        return "low"
    
    def _avg_sentence_length(self, texts: List[str]) -> float:
        sentences = [t.split('.') for t in texts if t.strip()]
        words = sum(len(s.split()) for s in sentences)
        total_sentences = sum(len(s) for s in sentences)
        return words / max(1, total_sentences)
    
    def _grammar_quality(self, texts: List[str]) -> str:
        formal_markers = sum(1 for t in texts if any(marker in t.lower() for marker in ["please", "thank you", "regards"]))
        total = len([t for t in texts if t.strip()])
        formal_ratio = formal_markers / max(1, total)
        return "formal" if formal_ratio > 0.2 else "informal"
    
    def _slang_level(self, text: str) -> str:
        slang_words = re.findall(r'\b(br[ou]h?|lolz?|wtf|omg|btw|idk|tbh|imo|smh|fyi)\b', text.lower())
        total_words = len(re.findall(r'\w+', text))
        ratio = len(slang_words) / max(1, total_words)
        if ratio > 0.08: return "high"
        elif ratio > 0.02: return "medium"
        return "low"
