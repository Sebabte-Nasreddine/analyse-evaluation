"""
Application FastAPI principale
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import router

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    logger.info("Starting up...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Créer l'application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="Système d'analyse automatisée des évaluations de formation avec NLP multilingue"
)

# CORS - TEMPORARILY ALLOW ALL FOR DEBUGGING
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=False,  # Must be False when using wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(router)


@app.get("/")
def root():
    """Endpoint racine"""
    return {
        "message": "Formation Evaluation Analysis API",
        "version": settings.VERSION,
        "status": "online"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
