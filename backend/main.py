import os
import logging
from dotenv import load_dotenv

# Load .env variables first
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.database_utils import init_db
from api.auth import router as auth_router
from api.upload import router as upload_router
from api.process import router as process_router
from api.chat import router as chat_router
from api.report import router as report_router
from api.history import router as history_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-Powered Video Summarization System API",
    description="Backend API services for speech transcribing, CV frame extracting, and AI summarizing of videos.",
    version="1.0.0"
)

# Configure CORS for local frontend communication (React dev server defaults to port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount frames and uploads folder statically to serve assets to UI
frames_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frames")
os.makedirs(frames_path, exist_ok=True)
app.mount("/frames", StaticFiles(directory=frames_path), name="frames")

uploads_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    logger.info("Initializing database schema...")
    try:
        init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}", exc_info=True)

# Register API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(process_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(history_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "AI-Powered Video Summarization System API is active.",
        "docs": "/docs"
    }
