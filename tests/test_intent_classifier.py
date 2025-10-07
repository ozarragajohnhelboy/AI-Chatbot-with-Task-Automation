import pytest
import asyncio
from ml.inference.intent_predictor import IntentPredictor
from app.models.schemas import IntentType


@pytest.fixture
def predictor():
    return IntentPredictor()


@pytest.mark.asyncio
async def test_file_operation_intent(predictor):
    result = await predictor.predict("open file document.txt")
    assert result["intent"] == IntentType.FILE_OPERATION
    assert result["confidence"] > 0.5


@pytest.mark.asyncio
async def test_reminder_intent(predictor):
    result = await predictor.predict("remind me tomorrow at 9am")
    assert result["intent"] == IntentType.SCHEDULE_REMINDER
    assert result["confidence"] > 0.5


@pytest.mark.asyncio
async def test_script_intent(predictor):
    result = await predictor.predict("run script.py")
    assert result["intent"] == IntentType.RUN_SCRIPT
    assert result["confidence"] > 0.5


@pytest.mark.asyncio
async def test_chat_intent(predictor):
    result = await predictor.predict("hello how are you")
    assert result["intent"] == IntentType.CHAT
    assert result["confidence"] > 0.5

