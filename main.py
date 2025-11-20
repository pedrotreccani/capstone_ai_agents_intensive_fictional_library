from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Import configuration
from config.database import engine
from config.telemetry import logger

# Import models to create tables
from models.database import Base

# Import routers
from routers import books, health

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Library Book Curation API",
    version="1.0.0",
    description="A library management system with book CRUD and voting capabilities"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine)

# Include routers
app.include_router(health.router)
app.include_router(books.router)

logger.info("Library API started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)