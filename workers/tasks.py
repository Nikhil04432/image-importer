# workers/tasks.py
"""
Celery Worker Tasks - Image Import from Google Drive
Handles background job processing for image imports
"""
from storage import upload_image
from google.oauth2 import service_account
from googleapiclient.discovery import build
from minio import Minio

import os
import uuid
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from urllib.parse import urlparse, parse_qs

from celery import Celery
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
PUBLIC_MINIO_URL = os.getenv("PUBLIC_MINIO_URL", "http://localhost:9000")

minio_client = Minio(
    MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Ensure bucket exists
if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:gil%40123@localhost:5432/imagedb"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class ImportJob(Base):
    """Tracks import job status and metadata"""
    __tablename__ = "import_jobs"
    
    id = Column(String(36), primary_key=True)
    source_url = Column(String(2000), nullable=False, index=True)
    status = Column(String(50), default="PENDING", index=True)
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
    
    id = Column(String(36), primary_key=True)
    job_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    google_drive_id = Column(String(255), nullable=True, unique=True)
    size_bytes = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    storage_path = Column(String(2000), nullable=False)
    source_type = Column(String(50), default="GOOGLE_DRIVE")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ============================================================================
# CELERY SETUP
# ============================================================================

BROKER_URL = os.getenv("RABBITMQ_URL", "redis://localhost:6379/0")

celery_app = Celery(
    'tasks',
    broker=BROKER_URL,
    backend=BROKER_URL,
    include=['tasks']
)

celery_app.conf.task_default_queue = 'celery'

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_pool='solo',
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise


def extract_folder_id(folder_url: str) -> str:
    """
    Extract Google Drive folder ID from sharing URL
    
    Example:
    Input:  https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J?usp=sharing
    Output: 1A2B3C4D5E6F7G8H9I0J
    """
    try:
        if '/folders/' in folder_url:
            folder_id = folder_url.split('/folders/')[1].split('?')[0].split('#')[0]
            return folder_id
        
        parsed = urlparse(folder_url)
        params = parse_qs(parsed.query)
        if 'id' in params:
            return params['id'][0]
        
        return None
    except Exception as e:
        print(f"❌ Error extracting folder ID: {e}")
        return None


def fetch_images_from_google_drive(folder_id: str) -> list:
    print("\n🌐 Connecting to Google Drive API...")

    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    SERVICE_ACCOUNT_FILE = 'google-credentials.json'

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=creds, cache_discovery=False)

    print(f"📂 Fetching files from folder: {folder_id}")

    query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"

    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, size)"
    ).execute()

    files = results.get('files', [])

    images = []
    for f in files:
        images.append({
            'id': f['id'],
            'name': f['name'],
            'mime_type': f['mimeType'],
            'size': int(f.get('size', 0)),
            'url': f"https://drive.google.com/uc?id={f['id']}"
        })

    print(f"✅ Found {len(images)} real images from Drive\n")
    return images



def download_image(image_url: str, image_name: str, timeout: int = 30) -> tuple:
    """
    Download single image from URL
    
    Returns: (image_bytes, mime_type) or (None, None) on failure
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"      📥 Downloading: {image_name}...", end=" ")
        
        response = requests.get(image_url, timeout=timeout, headers=headers, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        # Check if it's actually an image
        content_type = response.headers.get('content-type', '')
        
        if 'image' not in content_type.lower():
            print(f"❌ (Not an image: {content_type})")
            return None, None
        
        # Read image bytes
        image_bytes = response.content
        
        # Check size
        size_mb = len(image_bytes) / 1024 / 1024
        if size_mb > 50:
            print(f"❌ (Too large: {size_mb:.1f} MB)")
            return None, None
        
        print(f"✅ ({size_mb:.1f} MB)")
        
        return image_bytes, content_type
        
    except Exception as e:
        print(f"❌ (Error: {str(e)[:50]})")
        return None, None


def upload_to_s3(image_bytes: bytes, filename: str, job_id: str) -> str:
    object_name = f"{job_id}/{filename}"

    minio_client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        data=BytesIO(image_bytes),
        length=len(image_bytes),
        content_type="image/jpeg"
    )

    # 🔗 Public URL returned to frontend
    return f"{PUBLIC_MINIO_URL}/{MINIO_BUCKET}/{object_name}"




def save_image_metadata(db, job_id, filename, google_drive_id, size_bytes, mime_type, storage_path):

    # 🔒 Prevent duplicate inserts (important for parallel workers)
    existing = db.query(Image).filter(Image.google_drive_id == google_drive_id).first()
    if existing:
        return True

    image = Image(
        id=str(uuid.uuid4()),
        job_id=job_id,
        name=filename,
        google_drive_id=google_drive_id,
        size_bytes=size_bytes,
        mime_type=mime_type,
        storage_path=storage_path,
        source_type="GOOGLE_DRIVE",
        created_at=datetime.utcnow()
    )

    db.add(image)
    db.commit()
    return True

# ============================================================================
# CELERY TASKS
# ============================================================================

@celery_app.task(bind=True, max_retries=3, name='tasks.import_google_drive_folder')
def import_google_drive_folder(self, job_id: str, folder_url: str):
    """
    Main task: Import all images from Google Drive folder
    
    This runs in background with automatic retries
    """
    db = get_db()
    
    try:
        print(f"\n{'='*80}")
        print(f"🚀 Starting import job: {job_id}")
        print(f"📂 Folder URL: {folder_url}")
        print(f"{'='*80}\n")
        
        # Update job status
        job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        job.status = "PROCESSING"
        job.updated_at = datetime.utcnow()
        db.commit()
        
        print("✅ Job status: PROCESSING\n")
        
        # Extract folder ID
        folder_id = extract_folder_id(folder_url)
        if not folder_id:
            raise Exception("Could not extract folder ID from URL")
        
        print(f"✅ Extracted folder ID: {folder_id}\n")
        
        # Fetch image list from Google Drive
        print("📥 Fetching image list from Google Drive...")
        image_list = fetch_images_from_google_drive(folder_id)
        
        total_images = len(image_list)
        print(f"\n📊 Total images to process: {total_images}\n")
        
        # Update job with total count
        job.total_images = total_images
        db.commit()
        
        if total_images == 0:
            job.status = "COMPLETED"
            job.completed_at = datetime.utcnow()
            db.commit()
            print("⚠️  No images found in folder")
            return
        
        # Process images in parallel
        processed = 0
        failed = 0
        
        print(f"🔄 Processing {total_images} images in parallel...\n")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for idx, image_info in enumerate(image_list):
                future = executor.submit(
                    process_single_image,
                    job_id,
                    image_info
                )
                futures[future] = idx + 1
            
            # Process completed downloads
            for future in as_completed(futures):
                try:
                    success = future.result()
                    if success:
                        processed += 1
                    else:
                        failed += 1
                    
                    # Update progress
                    completed = processed + failed
                    progress = (completed / total_images) * 100
                    job.processed_images = processed
                    job.failed_images = failed
                    job.updated_at = datetime.utcnow()
                    db.commit()
                    
                    print(f"   📈 Progress: {processed + failed}/{total_images} ({progress:.1f}%)")
                    
                except Exception as e:
                    failed += 1
                    print(f"   ❌ Error processing image: {e}")
        
        # Mark job as completed
        job.status = "COMPLETED"
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        db.commit()
        
        print(f"\n{'='*80}")
        print(f"✅ Import job COMPLETED!")
        print(f"   Total: {total_images}")
        print(f"   Processed: {processed}")
        print(f"   Failed: {failed}")
        print(f"{'='*80}\n")
        
        return {
            "status": "COMPLETED",
            "total": total_images,
            "processed": processed,
            "failed": failed
        }
        
    except Exception as e:
        print(f"\n❌ Job failed: {e}\n")
        
        job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
        if job:
            job.status = "FAILED"
            job.error_message = str(e)
            job.updated_at = datetime.utcnow()
            db.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    
    finally:
        db.close()


def process_single_image(job_id: str, image_info: dict) -> bool:
    db = SessionLocal()

    try:
        drive_file_id = image_info.get('id')
        filename = image_info.get('name', 'unknown.jpg')

        # 🔐 1. Skip if already imported
        existing = db.query(Image).filter(Image.google_drive_id == drive_file_id).first()
        if existing:
            print(f"⏭️  Skipped duplicate: {filename}")
            return True

        # 2. Download
        image_bytes, mime_type = download_image(image_info['url'], filename)
        if not image_bytes:
            return False

        # 3. Upload
        s3_path = upload_image(image_bytes, filename, mime_type)

        # 4. Save metadata
        save_image_metadata(
            db,
            job_id=job_id,
            filename=filename,
            google_drive_id=drive_file_id,
            size_bytes=len(image_bytes),
            mime_type=mime_type,
            storage_path=s3_path
        )

        return True

    except IntegrityError:
        db.rollback()
        print(f"⚠️ Duplicate detected (race condition): {filename}")
        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Error processing {filename}: {e}")
        return False

    finally:
        db.close()


# ============================================================================
# WORKER STARTUP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🎯 Celery Worker Started")
    print("📌 Listening for tasks...")
    print("="*80 + "\n")
    
    celery_app.start()