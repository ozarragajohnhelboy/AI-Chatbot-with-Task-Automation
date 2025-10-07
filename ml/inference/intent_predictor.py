import tensorflow as tf
import numpy as np
from pathlib import Path
import json
import re

from app.models.schemas import IntentType
from app.core.logging_config import get_logger


logger = get_logger(__name__)


class IntentPredictor:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.intent_labels = [
            IntentType.CHAT,
            IntentType.FILE_OPERATION,
            IntentType.SCHEDULE_REMINDER,
            IntentType.RUN_SCRIPT,
            IntentType.SEARCH,
            IntentType.SYSTEM_INFO,
            IntentType.UNKNOWN,
        ]
        
        self._initialize_fallback()
    
    def _initialize_fallback(self):
        self.patterns = {
            IntentType.FILE_OPERATION: [
                r'\b(open|create|delete|move|copy|read|write|save)\b.*\b(file|folder|directory)\b',
                r'\b(file|folder|directory)\b',
            ],
            IntentType.SCHEDULE_REMINDER: [
                r'\b(remind|schedule|alarm|notify)\b',
                r'\b(tomorrow|today|later|at \d+)\b',
            ],
            IntentType.RUN_SCRIPT: [
                r'\b(run|execute|start|launch)\b.*\b(script|program|command)\b',
                r'\bpython\b.*\.py\b',
            ],
            IntentType.SEARCH: [
                r'\b(search|find|look for|query)\b',
                r'\bwhere is\b',
            ],
            IntentType.SYSTEM_INFO: [
                r'\b(system|cpu|memory|disk|process)\b.*\b(info|status|usage)\b',
                r'\bwhat.*\b(time|date|weather)\b',
            ],
        }
    
    async def predict(self, text: str) -> dict:
        try:
            if self.model is None:
                return self._fallback_predict(text)
            
            return self._model_predict(text)
            
        except Exception as e:
            logger.warning(f"Error in prediction, using fallback: {e}")
            return self._fallback_predict(text)
    
    def _fallback_predict(self, text: str) -> dict:
        text_lower = text.lower()
        
        scores = {intent: 0.0 for intent in IntentType}
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    scores[intent] += 0.3
        
        action_verbs = {
            IntentType.FILE_OPERATION: [
                'create', 'make', 'new', 'add', 'build', 'generate',
                'open', 'display', 'view', 'read',
                'delete', 'remove', 'erase', 'clear', 'trash',
                'move', 'transfer', 'relocate', 'shift',
                'copy', 'duplicate', 'clone',
                'write', 'save', 'store', 'put',
                'rename', 'change', 'modify', 'update',
            ],
            IntentType.SCHEDULE_REMINDER: [
                'remind', 'reminder', 'remember', 'notify', 'alert',
                'schedule', 'plan', 'set', 'arrange',
                'alarm', 'wake', 'ping', 'tell',
            ],
            IntentType.RUN_SCRIPT: [
                'run', 'execute', 'start', 'launch', 'fire',
                'perform', 'do', 'activate', 'trigger',
                'call', 'invoke', 'process',
            ],
            IntentType.SEARCH: [
                'search', 'find', 'look', 'locate', 'discover',
                'where', 'query', 'seek', 'hunt', 'browse', 'show',
            ],
            IntentType.SYSTEM_INFO: [
                'time', 'date', 'clock', 'calendar',
                'system', 'computer', 'machine', 'status',
                'info', 'information', 'details', 'stats',
            ],
        }
        
        search_phrases = ['find', 'look for', 'search for', 'where is', 'locate', 'show me']
        for phrase in search_phrases:
            if phrase in text_lower:
                scores[IntentType.SEARCH] += 0.6
        
        file_related = ['file', 'folder', 'directory', 'doc', 'document', 'text', 'data', 'path']
        
        for intent, verbs in action_verbs.items():
            for verb in verbs:
                if f' {verb} ' in f' {text_lower} ' or text_lower.startswith(verb):
                    scores[intent] += 0.4
                    
                    if intent == IntentType.FILE_OPERATION:
                        if any(f in text_lower for f in file_related):
                            scores[intent] += 0.3
        
        if any(word in text_lower for word in ['folder', 'directory']):
            if not any(search_word in text_lower for search_word in ['find', 'search', 'where', 'locate', 'look']):
                scores[IntentType.FILE_OPERATION] += 0.5
        
        if any(word in text_lower for word in ['tomorrow', 'later', 'at', 'pm', 'am', 'o\'clock']):
            scores[IntentType.SCHEDULE_REMINDER] += 0.3
        
        if '.py' in text_lower or '.sh' in text_lower or 'script' in text_lower:
            scores[IntentType.RUN_SCRIPT] += 0.4
        
        greeting_words = ['hello', 'hi', 'hey', 'greetings', 'sup', 'yo']
        if any(text_lower.startswith(g) for g in greeting_words):
            scores[IntentType.CHAT] += 0.8
        
        if max(scores.values()) > 0:
            predicted_intent = max(scores, key=scores.get)
            confidence = min(scores[predicted_intent], 0.95)
        else:
            predicted_intent = IntentType.CHAT
            confidence = 0.6
        
        return {
            "intent": predicted_intent,
            "confidence": confidence,
        }
    
    def _model_predict(self, text: str) -> dict:
        processed = self._preprocess(text)
        prediction = self.model.predict(processed, verbose=0)
        
        intent_idx = np.argmax(prediction[0])
        confidence = float(prediction[0][intent_idx])
        
        return {
            "intent": self.intent_labels[intent_idx],
            "confidence": confidence,
        }
    
    def _preprocess(self, text: str):
        return text

