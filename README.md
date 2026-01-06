# ImageSync - Scalable Image Import System

## 📋 Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Prerequisites](#prerequisites)
5. [Quick Start](#quick-start)
6. [Project Structure](#project-structure)
7. [API Documentation](#api-documentation)
8. [Configuration](#configuration)
9. [Deployment](#deployment)
10. [Performance & Scalability](#performance--scalability)

---

## ✨ Features

### Core Features
- ✅ **Batch Image Import** - Import thousands of images from Google Drive & Dropbox
- ✅ **Real-time Progress Tracking** - Live progress bar with download/upload status
- ✅ **Parallel Processing** - Handle 10,000+ images concurrently with worker pool
- ✅ **Cloud Storage** - AWS S3 compatible (MinIO for local dev)
- ✅ **Metadata Management** - PostgreSQL for persistent image metadata
- ✅ **Responsive Gallery** - Browse, search, and paginate imported images
- ✅ **Fault Tolerance** - Automatic retries and error recovery
- ✅ **Async Processing** - Non-blocking imports with background workers

### Technical Features
- 🐳 **Docker Containerization** - All services Dockerized
- 🔄 **Microservices Architecture** - Loosely coupled, independently scalable
- 📊 **Observability** - Structured logging and monitoring ready
- 🔐 **Security** - Secure credential handling, CORS protection
- 📈 **Horizontal Scaling** - Worker pool auto-scales with demand
- 💪 **Production Ready** - Error handling, validation, health checks

---

## 🏗️ Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                            │
│              (React Frontend - Port 5173)                   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  API GATEWAY                                │
│            (FastAPI Backend - Port 8000)                    │
│  - Validate requests                                        │
│  - Create import jobs                                       │
│  - Queue tasks to Redis                                     │
│  - Return job status                                        │
└────────────────────┬────────────────────────────────────────┘
                     │ Queue
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              MESSAGE QUEUE (Redis)                          │
│                Port 6379                                    │
│  - FIFO task queue                                          │
│  - Job results backend                                      │
│  - Celery broker                                            │
└────────────────────┬────────────────────────────────────────┘
                     │ Pull Tasks
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         WORKER POOL (Celery - Scalable)                     │
│  - Download from Google Drive/Dropbox                       │
│  - Parallel image processing (5 concurrent)                 │
│  - Upload to cloud storage (S3/MinIO)                       │
│  - Save metadata to database                                │
│  - Update job progress in real-time                         │
└────────────────────┬────────────────────────────────────────┘
                     │ Store
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
┌──────────────────┐    ┌──────────────────┐
│   PostgreSQL     │    │  Cloud Storage   │
│   Port 5432      │    │  (MinIO/S3)      │
│  - Jobs table    │    │  Port 9000       │
│  - Images table  │    │  - Image files   │
│  - Metadata      │    │  - Metadata URLs │
└──────────────────┘    └──────────────────┘
```

### Service Breakdown
The system is composed of the following independent services:

Frontend
Provides the user interface for submitting import jobs and browsing the image gallery.
Built with React + Vite and runs on port 5173.

Backend
Exposes REST APIs, coordinates import jobs, and manages application logic.
Built with Python FastAPI and runs on port 8000.

Worker
Executes high-concurrency image processing tasks such as downloading and uploading.
Built with Python Celery and runs as a background service.

Redis
Acts as the message queue, task broker, and result backend for the worker system.
Runs on port 6379.

PostgreSQL
Stores persistent metadata for all imported images and jobs.
Runs on port 5432.

MinIO
Provides S3-compatible object storage for images.
Runs on ports 9000 (API) and 9001 (console).

---

## 💻 Tech Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Fast build tool
- **Inline CSS** - Responsive styling

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - ORM for database
- **Pydantic** - Data validation

### Worker
- **Celery** - Distributed task queue
- **Redis** - Message broker
- **ThreadPoolExecutor** - Parallel processing
- **google-api-python-client** - Google Drive API
- **boto3** - AWS S3 integration

### Database & Storage
- **PostgreSQL 15** - Relational database
- **MinIO** - S3-compatible object storage
- **Redis 7** - In-memory cache & queue

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **Python venv** - Virtual environments

---

## 📋 Prerequisites

### System Requirements
- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **8GB RAM** minimum (4GB for basic testing)
- **10GB disk space** (for images)

### Optional (Local Development)
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15** (if running locally without Docker)
- **Redis 7** (if running locally without Docker)

### Credentials
- **Google Cloud Service Account** (for real Google Drive API)
  - Create at: https://console.cloud.google.com/
  - Download JSON credentials
  - Share Google Drive folder with service account email

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/imageimporter.git
cd imageimporter
```

### 2. Create Environment Files

**backend/.env:**
```env
DATABASE_URL=postgresql://postgres:gil123@postgres:5432/imagedb
RABBITMQ_URL=redis://redis:6379/0
ENV=production
DEBUG=False
```

**workers/.env:**
```env
DATABASE_URL=postgresql://postgres:gil123@postgres:5432/imagedb
RABBITMQ_URL=redis://redis:6379/0
```

### 3. (Optional) Add Google Credentials

Place `google-credentials.json` in `workers/` directory for real Google Drive integration.

### 4. Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# Watch logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 5. Access Services

| Service | URL |
|---------|-----|
| Frontend |        http://localhost:5173 |
| Backend API |     http://localhost:8000 |
| API Docs |        http://localhost:8000/docs |
| MinIO Console |   http://localhost:9001 |

### 6. Test Import

1. Open http://localhost:5173
2. Click **Import** tab
3. Paste any Google Drive folder URL
4. Click **Start Import**
5. Watch progress in **Progress** tab
6. View images in **Gallery** tab

---

## 📁 Project Structure

```
imageimporter/
├── frontend/                          # React app
│   ├── src/
│   │   ├── App.jsx                   # Main component
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── backend/                           # FastAPI service
│   ├── main.py                       # API endpoints
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── workers/                           # Celery workers
│   ├── tasks.py                      # Background tasks
│   ├── google-credentials.json       # Google API credentials
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── docker-compose.yml                # Service orchestration
├── README.md                         # This file
└── .gitignore
```

---

## 🔌 API Documentation

### Authentication
Currently, no authentication required. For production, add JWT tokens.

### Endpoints

#### 1. Start Import Job
```http
POST /api/import/google-drive
Content-Type: application/json

{
  "folder_url": "https://drive.google.com/drive/folders/1ABC2DEF3GHI..."
}
```

**Response (200):**
```json
{
  "job_id": "abc-123-xyz-789",
  "status": "PENDING",
  "message": "Import job queued. Job ID: abc-123-xyz-789"
}
```

**Status Codes:**
- `200` - Job successfully queued
- `400` - Invalid Google Drive URL
- `500` - Server error

---

#### 2. Get Import Status
```http
GET /api/import-status/{job_id}
```

**Response (200):**
```json
{
  "job_id": "abc-123-xyz-789",
  "status": "PROCESSING",
  "total_images": 100,
  "processed_images": 45,
  "failed_images": 2,
  "progress": 45.0,
  "error_message": null,
  "created_at": "2026-01-04T10:30:00",
  "updated_at": "2026-01-04T10:35:00",
  "completed_at": null
}
```

**Job Status Values:**
- `PENDING` - Waiting to process
- `PROCESSING` - Currently downloading/uploading
- `COMPLETED` - All images imported successfully
- `FAILED` - Job failed with error

---

#### 3. Get Images List
```http
GET /api/images?page=1&size=20&search=photo&source=GOOGLE_DRIVE
```

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `size` (int, default: 20, max: 100) - Items per page
- `search` (string, optional) - Search by filename
- `source` (string, optional) - Filter by GOOGLE_DRIVE or DROPBOX

**Response (200):**
```json
{
  "items": [
    {
      "id": "img-123",
      "name": "photo.jpg",
      "size_bytes": 2048576,
      "mime_type": "image/jpeg",
      "storage_path": "s3://bucket/imports/job-id/photo.jpg",
      "source_type": "GOOGLE_DRIVE",
      "created_at": "2026-01-04T10:35:00"
    }
  ],
  "page": 1,
  "size": 20,
  "total_count": 100,
  "total_pages": 5
}
```

---

#### 4. Get Single Image
```http
GET /api/images/{image_id}
```

**Response (200):**
```json
{
  "id": "img-123",
  "name": "photo.jpg",
  "size_bytes": 2048576,
  "mime_type": "image/jpeg",
  "storage_path": "s3://bucket/imports/job-id/photo.jpg",
  "source_type": "GOOGLE_DRIVE",
  "created_at": "2026-01-04T10:35:00"
}
```

---

#### 5. Health Check
```http
GET /health
```

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T10:30:00"
}
```

---

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://postgres:gil123@localhost:5432/imagedb

# Message Queue
RABBITMQ_URL=redis://localhost:6379/0

# Environment
ENV=production              # development or production
DEBUG=False                 # True for development

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Google Drive API (optional)
GOOGLE_API_KEY=your_api_key_here
```

#### Worker (.env)
```env
# Database
DATABASE_URL=postgresql://postgres:gil123@localhost:5432/imagedb

# Message Queue
RABBITMQ_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=your_bucket
```

### Database Connection

PostgreSQL credentials are configured in docker-compose.yml:
- **User:** 
- **Password:** 
- **Database:** 
- **Port:** 5432

### Google Drive Setup (Production)

1. **Create Service Account:**
   - Go to https://console.cloud.google.com/
   - Create new project
   - Enable Google Drive API
   - Create service account
   - Download JSON credentials

2. **Share Folder with Service Account:**
   - Copy service account email from JSON
   - Open Google Drive folder
   - Right-click → Share
   - Paste email and give "Viewer" access

3. **Place Credentials:**
   - Save JSON as `workers/google-credentials.json`
   - Worker will use it automatically

---

## 🌐 Deployment

### Docker Compose (Local/On-Premise)

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.yml up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f worker

# Stop all services
docker-compose down

# Clean everything (remove volumes)
docker-compose down -v
```

## 📊 Performance & Scalability
### Scaling Strategy

1. **Vertical Scaling** - Increase worker resources (CPU/RAM)
2. **Horizontal Scaling** - Add more worker instances
3. **Database Scaling** - Add read replicas, optimize indexes
4. **Caching** - Use Redis for frequently accessed data
5. **CDN** - Serve images from CloudFront/CloudFlare

---
