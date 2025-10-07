from typing import Optional, Dict, Any
from datetime import datetime

from app.models.schemas import ChatResponse, Intent, Message, MessageRole
from automation.handlers.command_handler import CommandHandler
from automation.handlers.adaptive_processor import AdaptiveProcessor
from app.core.logging_config import get_logger


logger = get_logger(__name__)


class ChatService:
    def __init__(
        self,
        intent_predictor,
        entity_extractor,
        conversation_manager,
        vector_store,
    ):
        self.intent_predictor = intent_predictor
        self.entity_extractor = entity_extractor
        self.conversation_manager = conversation_manager
        self.vector_store = vector_store
        self.command_handler = CommandHandler()
        self.adaptive_processor = AdaptiveProcessor()
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        logger.info(f"Processing message for session {session_id}")
        
        user_message = Message(
            role=MessageRole.USER,
            content=message,
        )
        self.conversation_manager.add_message(session_id, user_message)
        
        conversation_history = self.conversation_manager.get_recent_messages(
            session_id, limit=5
        )
        
        intent = await self._classify_intent(message, conversation_history)
        
        response_text, task_id = await self.command_handler.handle(
            intent=intent,
            message=message,
            context=context or {},
            history=conversation_history,
        )
        
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=response_text,
        )
        self.conversation_manager.add_message(session_id, assistant_message)
        
        await self.vector_store.add_interaction(
            session_id=session_id,
            user_message=message,
            assistant_response=response_text,
            intent=intent.type.value,
        )
        
        return ChatResponse(
            response=response_text,
            intent=intent,
            session_id=session_id,
            task_id=task_id,
        )
    
    async def _classify_intent(self, message: str, history: list = None) -> Intent:
        intent_result = await self.intent_predictor.predict(message)
        entities = await self.entity_extractor.extract(message)
        
        if history:
            entities = self.adaptive_processor.enhance_understanding(
                message, entities, history
            )
        
        return Intent(
            type=intent_result["intent"],
            confidence=intent_result["confidence"],
            entities=entities,
        )

