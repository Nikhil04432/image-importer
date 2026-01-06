from storage import init_bucket
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import uuid
from typing import List, Optional
from celery import Celery


REDIS_URL = os.getenv("CELERY_BROKER_URL")

if not REDIS_URL:
    raise RuntimeError("CELERY_BROKER_URL not set")

celery_app = Celery(
    "image_import_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)# backend/main.py
"""
Professional FastAPI Backend Service
Handles API requests, job queuing, and database operations
"""


# ============================================================================
# DATABASE SETUP
# ============================================================================

# Use environment variables for production, fallback to localhost for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:gil%40123@localhost:5432/imagedb"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True  # Checks connection health
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# DATABASE MODELS (SQLAlchemy ORM)
# ============================================================================

class ImportJob(Base):
    """Tracks import job status and metadata"""
    __tablename__ = "import_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_url = Column(String(2000), nullable=False, index=True)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, PROCESSING, COMPLETED, FAILED
    total_images = Column(Integer, default=0)
    processed_images = Column(Integer, default=0)
    failed_images = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)


class Image(Base):
    """Stores image metadata"""
    __tablename__ = "images"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    google_drive_id = Column(String(255), nullable=True, unique=True)
    size_bytes = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    storage_path = Column(String(2000), nullable=False)
    source_type = Column(String(50), default="GOOGLE_DRIVE")  # GOOGLE_DRIVE or DROPBOX
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# Create tables on startup
Base.metadata.create_all(bind=engine)

# ============================================================================
# PYDANTIC MODELS (Request/Response validation)
# ============================================================================

class ImportRequest(BaseModel):
    """Request body for import endpoint"""
    folder_url: str = Field(..., example="https://drive.google.com/drive/folders/...")
    
    class Config:
        json_schema_extra = {
            "example": {
                "folder_url": "https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J"
            }
        }


class ImportResponse(BaseModel):
    """Response for import request"""
    job_id: str
    status: str
    message: str


class ImageMetadata(BaseModel):
    """Single image metadata"""
    id: str
    name: str
    size_bytes: Optional[int]
    mime_type: Optional[str]
    storage_path: str
    source_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ImagesListResponse(BaseModel):
    """Paginated images response"""
    items: List[ImageMetadata]
    page: int
    size: int
    total_count: int
    total_pages: int


class JobStatus(BaseModel):
    """Job status response"""
    job_id: str
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED
    total_images: int
    processed_images: int
    failed_images: int
    progress: float  # 0-100
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="ImageSync API",
    description="Scalable image import system from Google Drive & Dropbox",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_bucket()
app.mount("/images", StaticFiles(directory="static/images"), name="images")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db():
    """Dependency: Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_progress(job: ImportJob) -> float:
    """Calculate progress percentage"""
    if job.total_images == 0:
        return 0.0
    return round((job.processed_images / job.total_images) * 100, 2)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.post("/api/import/google-drive", response_model=ImportResponse)
async def import_google_drive(request: ImportRequest, db: Session = Depends(get_db)):
    """
    Start an async import job for a Google Drive folder
    
    - Validates URL format
    - Creates job record in database
    - Queues job for async processing
    - Returns job_id immediately (no waiting)
    
    **Example:**
    ```
    POST /api/import/google-drive
    {
        "folder_url": "https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J"
    }
    ```
    """
    try:
        # Validate URL format
        if not request.folder_url or "drive.google.com" not in request.folder_url:
            raise HTTPException(
                status_code=400,
                detail="Invalid Google Drive URL. Must contain 'drive.google.com'"
            )
        
        # Create import job record
        job = ImportJob(
            id=str(uuid.uuid4()),
            source_url=request.folder_url,
            status="PENDING"
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # TODO: Queue job to RabbitMQ/Celery
        celery_app.send_task(
            'tasks.import_google_drive_folder',
            args=[job.id, request.folder_url],
            queue='celery'
        )

        
        return ImportResponse(
            job_id=job.id,
            status="PENDING",
            message=f"Import job queued. Job ID: {job.id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/import-status/{job_id}", response_model=JobStatus)
async def get_import_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get the status of an import job
    
    Returns current progress, total images, processed count, etc.
    
    **Response includes:**
    - `status`: PENDING, PROCESSING, COMPLETED, FAILED
    - `progress`: 0-100 percentage
    - `processed_images`: Number of successfully imported images
    - `failed_images`: Number of failed imports
    """
    try:
        job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Calculate progress percentage
        progress = calculate_progress(job)
        
        return JobStatus(
            job_id=job.id,
            status=job.status,
            total_images=job.total_images,
            processed_images=job.processed_images,
            failed_images=job.failed_images,
            progress=progress,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
            completed_at=job.completed_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/images", response_model=ImagesListResponse)
async def list_images(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by image name"),
    source: Optional[str] = Query(None, description="Filter by source (GOOGLE_DRIVE or DROPBOX)"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of imported images
    
    Supports:
    - **Pagination**: page and size parameters
    - **Search**: Filter by image name
    - **Source Filter**: Filter by GOOGLE_DRIVE or DROPBOX
    
    **Example:**
    ```
    GET /api/images?page=1&size=20&search=photo
    ```
    """
    try:
        query = db.query(Image)
        
        # Apply search filter
        if search:
            query = query.filter(Image.name.ilike(f"%{search}%"))
        
        # Apply source filter
        if source:
            query = query.filter(Image.source_type == source)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Calculate pagination
        skip = (page - 1) * size
        images = query.order_by(Image.created_at.desc()).offset(skip).limit(size).all()
        
        total_pages = (total_count + size - 1) // size
        
        return ImagesListResponse(
            items=images,
            page=page,
            size=size,
            total_count=total_count,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/images/{image_id}")
async def get_image(image_id: str, db: Session = Depends(get_db)):
    """Get single image details"""
    try:
        image = db.query(Image).filter(Image.id == image_id).first()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return image
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs")
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """List all import jobs with optional status filter"""
    try:
        query = db.query(ImportJob)
        
        if status:
            query = query.filter(ImportJob.status == status)
        
        total_count = query.count()
        skip = (page - 1) * size
        jobs = query.order_by(ImportJob.created_at.desc()).offset(skip).limit(size).all()
        
        return {
            "items": jobs,
            "total_count": total_count,
            "page": page,
            "total_pages": (total_count + size - 1) // size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow()
    }


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("✅ FastAPI Backend Started")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🗄️  Database: Connected")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("❌ FastAPI Backend Stopped")


# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000