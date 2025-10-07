from fastapi import APIRouter, HTTPException, Request
from typing import List

from app.models.schemas import Conversation
from app.core.logging_config import get_logger


logger = get_logger(__name__)
router = APIRouter()


@router.get("/conversations", response_model=List[Conversation])
async def get_conversations(app_request: Request, limit: int = 10):
    try:
        conversation_manager = app_request.app.state.conversation_manager
        conversations = conversation_manager.get_recent_conversations(limit=limit)
        return conversations
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{session_id}", response_model=Conversation)
async def get_conversation(session_id: str, app_request: Request):
    try:
        conversation_manager = app_request.app.state.conversation_manager
        conversation = conversation_manager.get_conversation(session_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

