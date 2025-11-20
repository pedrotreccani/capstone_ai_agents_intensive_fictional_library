# Project Setup Guide

## Complete File Structure

Create this exact directory structure:

```
library-api/
├── main.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── run_local.sh
├── cloudbuild.yaml
├── setup.sh
├── README.md
├── ARCHITECTURE.md
│
├── models/
│   ├── __init__.py
│   └── database.py
│
├── schemas/
│   ├── __init__.py
│   └── book.py
│
├── repositories/
│   ├── __init__.py
│   └── book_repository.py
│
├── services/
│   ├── __init__.py
│   ├── book_service.py
│   └── health_service.py
│
├── routers/
│   ├── __init__.py
│   ├── books.py
│   └── health.py
│
├── config/
│   ├── __init__.py
│   ├── database.py
│   └── telemetry.py
│
└── kubernetes/
    └── deployment.yaml
```

## Quick Start Options

### Option 1: Quick Local Development (Recommended)

Use SQLite - no PostgreSQL required!

```bash
# Make the script executable
chmod +x run_local.sh

# Run the application
./run_local.sh
```

This will:
- Create a virtual environment
- Install dependencies
- Use SQLite (no database setup needed)
- Start the API at http://localhost:8080

### Option 2: Docker with SQLite

```bash
# Run API with SQLite (no PostgreSQL)
docker build -t library-api .
docker run -p 8080:8080 -e USE_SQLITE=true library-api
```

### Option 3: Docker Compose with PostgreSQL

```bash
# Start both PostgreSQL and API
docker-compose up

# Or just the API with SQLite
docker-compose --profile sqlite up api-sqlite
```

### Option 4: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with SQLite
export USE_SQLITE=true
uvicorn main:app --reload --port 8080
```

## Environment Configuration

### Development (SQLite)
```bash
# Create .env file
cp .env.example .env

# Edit .env - set USE_SQLITE=true
USE_SQLITE=true
```

### Production (PostgreSQL)
```bash
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/library
GCP_PROJECT_ID=your-project-id
```

## Step-by-Step Setup

### 1. Create Directory Structure

```bash
mkdir -p library-api/{models,schemas,repositories,services,routers,config,kubernetes}
cd library-api
```

### 2. Create __init__.py Files

Create empty `__init__.py` in each package directory:

```bash
touch models/__init__.py
touch schemas/__init__.py
touch repositories/__init__.py
touch services/__init__.py
touch routers/__init__.py
touch config/__init__.py
```

### 3. Copy All Python Files

Copy each file to its respective directory:
- `models/database.py`
- `schemas/book.py`
- `config/database.py`
- `config/telemetry.py`
- `repositories/book_repository.py`
- `services/book_service.py`
- `services/health_service.py`
- `routers/books.py`
- `routers/health.py`
- `main.py` (in root)

### 4. Create Configuration Files

- `requirements.txt`
- `Dockerfile`
- `.dockerignore`
- `cloudbuild.yaml`
- `setup.sh`

### 5. Populate __init__.py Files

#### models/__init__.py
```python
from .database import Base, Book
__all__ = ["Base", "Book"]
```

#### schemas/__init__.py
```python
from .book import (
    BookBase,
    BookCreate,
    BookUpdate,
    BookResponse,
    VoteRequest,
    HealthResponse
)
__all__ = [
    "BookBase",
    "BookCreate",
    "BookUpdate",
    "BookResponse",
    "VoteRequest",
    "HealthResponse"
]
```

#### config/__init__.py
```python
from .database import engine, SessionLocal, get_db
from .telemetry import logger, tracer
__all__ = ["engine", "SessionLocal", "get_db", "logger", "tracer"]
```

#### repositories/__init__.py
```python
from .book_repository import BookRepository
__all__ = ["BookRepository"]
```

#### services/__init__.py
```python
from .book_service import BookService
from .health_service import HealthService
__all__ = ["BookService", "HealthService"]
```

#### routers/__init__.py
```python
# Can be empty
__all__ = []
```

## Verification

### Check Directory Structure
```bash
tree -I '__pycache__|*.pyc'
```

### Verify Python Can Import
```bash
python3 -c "from config import database; print('✓ Imports work')"
```

### Test Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/library"
```

3. Run the app:
```bash
uvicorn main:app --reload --port 8080
```

4. Test endpoint:
```bash
curl http://localhost:8080/health
```

## Docker Build & Run

### Build Docker Image
```bash
docker build -t library-api:latest .
```

### Run Locally with Docker
```bash
docker run -p 8080:8080 \
  -e DATABASE_URL="postgresql://user:password@host.docker.internal:5432/library" \
  -e GCP_PROJECT_ID="your-project-id" \
  library-api:latest
```

### Test Docker Container
```bash
curl http://localhost:8080/health
```

## Common Issues & Solutions

### Issue: ModuleNotFoundError: No module named 'config'

**Solutions:**
1. Ensure all `__init__.py` files exist
2. Check Dockerfile copies all directories:
   ```dockerfile
   COPY models/ ./models/
   COPY schemas/ ./schemas/
   COPY config/ ./config/
   # ... etc
   ```
3. Verify directory structure matches exactly

### Issue: ImportError: attempted relative import with no known parent package

**Solution:** Make sure you're running from the project root:
```bash
cd library-api
uvicorn main:app --reload
```

### Issue: Can't connect to database

**Solution:** 
- For local development, use `localhost` or `127.0.0.1`
- For Docker, use `host.docker.internal` (Mac/Windows) or Docker network
- For GKE, ensure Cloud SQL proxy is configured

### Issue: OpenTelemetry errors in local dev

**Solution:** Set a dummy project ID or handle gracefully:
```bash
export GCP_PROJECT_ID="local-dev"
```

The code already handles missing GCP credentials gracefully with try/catch blocks.

## Quick Start Script

Create a `setup_project.sh` file:

```bash
#!/bin/bash
set -e

echo "Setting up project structure..."

# Create directories
mkdir -p models schemas repositories services routers config kubernetes

# Create __init__.py files
touch models/__init__.py
touch schemas/__init__.py
touch repositories/__init__.py
touch services/__init__.py
touch routers/__init__.py
touch config/__init__.py

echo "✓ Directory structure created"
echo "✓ __init__.py files created"
echo ""
echo "Next steps:"
echo "1. Copy all Python files to their respective directories"
echo "2. Copy configuration files (requirements.txt, Dockerfile, etc.)"
echo "3. Run: pip install -r requirements.txt"
echo "4. Run: uvicorn main:app --reload"
```

Make it executable and run:
```bash
chmod +x setup_project.sh
./setup_project.sh
```

## Deployment Checklist

- [ ] All directories created
- [ ] All `__init__.py` files present
- [ ] All Python files in correct locations
- [ ] `requirements.txt` exists
- [ ] `Dockerfile` copies all directories
- [ ] `.dockerignore` created
- [ ] Local test passes
- [ ] Docker build succeeds
- [ ] Docker run succeeds
- [ ] GCP project configured
- [ ] `setup.sh` updated with project ID
- [ ] Infrastructure created (`./setup.sh`)
- [ ] Image pushed to GCR
- [ ] Kubernetes deployment applied