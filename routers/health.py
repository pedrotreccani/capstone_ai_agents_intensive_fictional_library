from fastapi import APIRouter
from schemas.book import HealthResponse
from services.health_service import HealthService

router = APIRouter(tags=["Health"])
health_service = HealthService()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with system information"""
    return health_service.get_health_status()

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Library Book Curation API",
        "version": health_service.VERSION,
        "docs": "/docs"
    }