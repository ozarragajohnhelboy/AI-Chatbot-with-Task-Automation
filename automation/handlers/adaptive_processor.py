from typing import Dict, Any, Optional, List
from app.models.schemas import Message
from app.core.logging_config import get_logger


logger = get_logger(__name__)


class AdaptiveProcessor:
    def __init__(self):
        self.context_memory = {}
        self.common_patterns = {}
        
    def enhance_understanding(
        self, 
        message: str, 
        entities: Dict[str, Any],
        history: List[Message]
    ) -> Dict[str, Any]:
        enhanced = entities.copy()
        
        enhanced = self._infer_from_context(message, enhanced, history)
        enhanced = self._apply_common_sense(message, enhanced)
        enhanced = self._expand_abbreviations(message, enhanced)
        
        return enhanced
    
    def _infer_from_context(
        self, 
        message: str, 
        entities: Dict[str, Any],
        history: List[Message]
    ) -> Dict[str, Any]:
        
        if not entities.get("file_path") and history:
            for msg in reversed(history[-3:]):
                if msg.role.value == "user" and any(word in msg.content.lower() for word in ["file", "folder", "document"]):
                    words = msg.content.split()
                    for word in words:
                        if len(word) > 2 and word[0].isupper():
                            entities["inferred_filename"] = word
                            break
        
        return entities
    
    def _apply_common_sense(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        message_lower = message.lower()
        
        location_hints = {
            "desktop": "Desktop",
            "downloads": "Downloads",
            "documents": "Documents",
            "pictures": "Pictures",
            "home": "~",
        }
        
        for hint, path in location_hints.items():
            if hint in message_lower:
                entities["location_hint"] = path
                break
        
        if any(word in message_lower for word in ["urgent", "asap", "now", "quickly"]):
            entities["priority"] = "high"
        
        if any(word in message_lower for word in ["backup", "save", "important"]):
            entities["importance"] = "high"
        
        return entities
    
    def _expand_abbreviations(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        abbreviations = {
            "doc": "document",
            "docs": "documents",
            "pic": "picture",
            "pics": "pictures",
            "vid": "video",
            "vids": "videos",
            "temp": "temporary",
            "proj": "project",
            "config": "configuration",
            "pref": "preference",
        }
        
        message_lower = message.lower()
        for abbr, full in abbreviations.items():
            if abbr in message_lower:
                entities["expanded_term"] = full
                break
        
        return entities
    
    def learn_from_interaction(
        self,
        message: str,
        intent: str,
        success: bool
    ):
        
        key = f"{intent}:{message[:30]}"
        if key not in self.common_patterns:
            self.common_patterns[key] = {
                "count": 0,
                "success_rate": 0.0,
            }
        
        pattern = self.common_patterns[key]
        pattern["count"] += 1
        pattern["success_rate"] = (
            (pattern["success_rate"] * (pattern["count"] - 1) + (1 if success else 0))
            / pattern["count"]
        )
        
        logger.info(f"Learned pattern: {key[:50]} (success rate: {pattern['success_rate']:.2f})")

