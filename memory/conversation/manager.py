from typing import Dict, List, Optional
from collections import defaultdict, deque
from datetime import datetime

from app.models.schemas import Message, Conversation
from app.core.config import get_settings
from app.core.logging_config import get_logger


logger = get_logger(__name__)
settings = get_settings()


class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=settings.MAX_CONVERSATION_HISTORY)
        )
        self.metadata: Dict[str, dict] = {}
    
    def add_message(self, session_id: str, message: Message):
        self.conversations[session_id].append(message)
        
        if session_id not in self.metadata:
            self.metadata[session_id] = {
                "created_at": datetime.utcnow(),
                "message_count": 0,
            }
        
        self.metadata[session_id]["updated_at"] = datetime.utcnow()
        self.metadata[session_id]["message_count"] += 1
        
        logger.debug(f"Added message to session {session_id}")
    
    def get_recent_messages(
        self, session_id: str, limit: int = 10
    ) -> List[Message]:
        if session_id not in self.conversations:
            return []
        
        messages = list(self.conversations[session_id])
        return messages[-limit:] if len(messages) > limit else messages
    
    def get_conversation(self, session_id: str) -> Optional[Conversation]:
        if session_id not in self.conversations:
            return None
        
        messages = list(self.conversations[session_id])
        meta = self.metadata.get(session_id, {})
        
        return Conversation(
            session_id=session_id,
            messages=messages,
            created_at=meta.get("created_at", datetime.utcnow()),
            updated_at=meta.get("updated_at", datetime.utcnow()),
        )
    
    def get_recent_conversations(self, limit: int = 10) -> List[Conversation]:
        sorted_sessions = sorted(
            self.metadata.items(),
            key=lambda x: x[1].get("updated_at", datetime.min),
            reverse=True,
        )
        
        conversations = []
        for session_id, _ in sorted_sessions[:limit]:
            conv = self.get_conversation(session_id)
            if conv:
                conversations.append(conv)
        
        return conversations
    
    def clear_conversation(self, session_id: str):
        if session_id in self.conversations:
            self.conversations[session_id].clear()
            logger.info(f"Cleared conversation {session_id}")

