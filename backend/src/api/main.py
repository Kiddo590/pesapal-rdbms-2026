"""
FastAPI backend for RDBMS web interface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .routes import database, query, tables, demo_app
from ..rdbms.core.database import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI"""
    # Startup
    print("Starting Pesapal RDBMS API...")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Create default database
    global default_db
    default_db = Database("default")
    
    yield
    
    # Shutdown
    print("Shutting down Pesapal RDBMS API...")


app = FastAPI(
    title="Pesapal RDBMS API",
    description="Custom relational database management system API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(tables.router, prefix="/api/tables", tags=["Tables"])
app.include_router(database.router, prefix="/api/database", tags=["Database"])
app.include_router(demo_app.router, prefix="/api/demo", tags=["Demo"])

# Global database instance
default_db = None


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Pesapal RDBMS API",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query",
            "tables": "/api/tables",
            "database": "/api/database",
            "demo": "/api/demo"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}