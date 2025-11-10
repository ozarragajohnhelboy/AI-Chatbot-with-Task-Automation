from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import get_settings
from app.core.logging_config import setup_logging, get_logger
from app.api import chat, tasks, conversations
from ml.inference.intent_predictor import IntentPredictor
from ml.inference.entity_extractor import EntityExtractorModel
from memory.conversation.manager import ConversationManager
from memory.vector_store.store import VectorStore


logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.LOG_LEVEL)
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    
    from automation.tasks.device_detector import DeviceDetector
    
    device_detector = DeviceDetector()
    device_info = device_detector.get_device_info()
    
    logger.info(f"Device: {device_info['os']} {device_info['machine']}")
    logger.info(f"Available apps: {[app['name'] for app in device_info['available_apps']]}")
    
    if device_info['preferred_reminder_app']:
        logger.info(f"Preferred reminder app: {device_info['preferred_reminder_app']['name']}")
    if device_info['preferred_calendar_app']:
        logger.info(f"Preferred calendar app: {device_info['preferred_calendar_app']['name']}")
    
    app.state.intent_predictor = IntentPredictor()
    app.state.entity_extractor = EntityExtractorModel()
    app.state.conversation_manager = ConversationManager()
    app.state.vector_store = VectorStore()
    app.state.device_info = device_info
    
    await app.state.vector_store.initialize()
    
    logger.info("All services initialized successfully")
    
    yield
    
    logger.info("Shutting down services")
    await app.state.vector_store.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(conversations.router, prefix="/api/v1", tags=["conversations"])

# Serve static files from frontend directory
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/")
async def root():
    """Serve the frontend index.html"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

