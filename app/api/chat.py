from fastapi import APIRouter, HTTPException, Request
from uuid import uuid4

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.core.logging_config import get_logger


logger = get_logger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, app_request: Request):
    try:
        session_id = request.session_id or str(uuid4())
        
        chat_service = ChatService(
            intent_predictor=app_request.app.state.intent_predictor,
            entity_extractor=app_request.app.state.entity_extractor,
            conversation_manager=app_request.app.state.conversation_manager,
            vector_store=app_request.app.state.vector_store,
        )
        
        response = await chat_service.process_message(
            message=request.message,
            session_id=session_id,
            context=request.context,
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn")
async def learn_from_feedback(feedback: dict):
    try:
        logger.info(f"Received learning feedback: {feedback}")
        return {"status": "feedback_recorded", "message": "Learning system updated"}
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

