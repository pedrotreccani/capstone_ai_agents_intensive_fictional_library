# This is a fictional project created exclusively for analysis as part of my AI capstone project - Library Book Curation API

A FastAPI-based library management system deployed on Google Cloud Platform (GCP) with Kubernetes (GKE), Cloud SQL, and OpenTelemetry integration. Built with a clean layered architecture for maintainability and scalability.

## Features

- **Complete CRUD operations** for book management
- **Rating system**: Vote on books with 0-5 stars
- **Health check endpoint** with version, region, and zone information
- **OpenTelemetry integration** exporting to GCP Cloud Trace and Cloud Logging
- **PostgreSQL database** using Google Cloud SQL
- **Kubernetes deployment** on GKE with autoscaling
- **Workload Identity** for secure GCP service authentication
- **Layered architecture** for clean separation of concerns

## Architecture

- **API**: FastAPI with Python 3.11
- **Database**: Google Cloud SQL (PostgreSQL 15)
- **Container Orchestration**: Google Kubernetes Engine (GKE)
- **Observability**: OpenTelemetry → Cloud Trace & Cloud Logging
- **CI/CD**: Cloud Build
- **Container Registry**: Google Container Registry (GCR)
- **Architecture Pattern**: Layered/Clean Architecture

## Project Structure

```
library-api/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container definition
├── cloudbuild.yaml                 # CI/CD configuration
├── setup.sh                        # Infrastructure setup
├── README.md                       # This file
├── ARCHITECTURE.md                 # Detailed architecture documentation
│
├── models/                         # Database Models Layer
│   ├── __init__.py
│   └── database.py                 # SQLAlchemy ORM models
│
├── schemas/                        # Validation/DTO Layer
│   ├── __init__.py
│   └── book.py                     # Pydantic schemas
│
├── repositories/                   # Data Access Layer
│   ├── __init__.py
│   └── book_repository.py          # Database operations
│
├── services/                       # Business Logic Layer
│   ├── __init__.py
│   ├── book_service.py             # Book business logic
│   └── health_service.py           # Health check logic
│
├── routers/                        # API Router Layer
│   ├── __init__.py
│   ├── books.py                    # Book endpoints
│   └── health.py                   # Health endpoints
│
├── config/                         # Configuration Layer
│   ├── __init__.py
│   ├── database.py                 # Database configuration
│   └── telemetry.py                # OpenTelemetry setup
│
└── kubernetes/                     # Kubernetes configurations
    └── deployment.yaml
```

### Architecture Layers

The application follows a **layered architecture** pattern with clear separation of concerns:

1. **Models Layer**: Database schema definitions (SQLAlchemy ORM)
2. **Schemas Layer**: Request/response validation (Pydantic)
3. **Config Layer**: Application configuration and setup
4. **Repository Layer**: Database access abstraction (Data Access Layer)
5. **Service Layer**: Business logic and orchestration
6. **Router Layer**: HTTP endpoint definitions (Controllers)
7. **Application Layer**: FastAPI initialization

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## API Endpoints

### Health & Info
- `GET /` - Root endpoint with API information
- `GET /health` - Health check with version, region, and zone

### Books CRUD
- `POST /books` - Create a new book
- `GET /books` - List all books (with pagination)
- `GET /books/{book_id}` - Get a specific book
- `PUT /books/{book_id}` - Update a book
- `DELETE /books/{book_id}` - Delete a book

### Voting
- `POST /books/{book_id}/vote` - Vote on a book (0-5 stars)

## Setup Instructions

### Prerequisites

1. Google Cloud SDK installed and configured
2. Docker installed
3. kubectl installed
4. A GCP project with billing enabled

### 1. Initial Setup

Edit `setup.sh` and update the configuration variables:

```bash
PROJECT_ID="your-project-id"
REGION="us-central1"
ZONE="us-central1-a"
```

Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Enable required GCP APIs
- Create a GKE cluster
- Create a Cloud SQL PostgreSQL instance
- Set up service accounts and IAM permissions
- Configure Workload Identity
- Create Kubernetes secrets and configmaps

### 2. Build and Deploy

#### Option A: Using Cloud Build (Recommended)

```bash
# Update cloudbuild.yaml with your cluster name and region if different
gcloud builds submit --config=cloudbuild.yaml
```

#### Option B: Manual Docker Build

```bash
# Build the image
docker build -t gcr.io/YOUR_PROJECT_ID/library-api:latest .

# Push to GCR
docker push gcr.io/YOUR_PROJECT_ID/library-api:latest

# Update kubernetes/deployment.yaml with YOUR_PROJECT_ID
# Then deploy
kubectl apply -f kubernetes/deployment.yaml
```

### 3. Access the API

Get the external IP:

```bash
kubectl get service library-api-service
```

Wait for the external IP to be assigned, then access the API:

```bash
curl http://EXTERNAL_IP/health
```

Access the interactive API documentation at:
```
http://EXTERNAL_IP/docs
```

## API Usage Examples

### Create a Book

```bash
curl -X POST "http://EXTERNAL_IP/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "978-0743273565",
    "description": "A classic American novel",
    "published_year": 1925
  }'
```

### List Books

```bash
curl "http://EXTERNAL_IP/books?skip=0&limit=10"
```

### Get a Book

```bash
curl "http://EXTERNAL_IP/books/1"
```

### Update a Book

```bash
curl -X PUT "http://EXTERNAL_IP/books/1" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "An updated description"
  }'
```

### Vote on a Book

```bash
curl -X POST "http://EXTERNAL_IP/books/1/vote" \
  -H "Content-Type: application/json" \
  -d '{
    "stars": 5
  }'
```

### Delete a Book

```bash
curl -X DELETE "http://EXTERNAL_IP/books/1"
```

### Check Health

```bash
curl "http://EXTERNAL_IP/health"
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "region": "us-central1",
  "zone": "us-central1-a",
  "timestamp": "2025-11-19T12:00:00.000000"
}
```

## Environment Variables

The application uses the following environment variables:

- `DATABASE_URL` - PostgreSQL connection string (from Kubernetes secret)
- `GCP_PROJECT_ID` - GCP project ID for OpenTelemetry (from ConfigMap)

## Monitoring and Observability

### Cloud Trace
View distributed traces in the GCP Console:
```
https://console.cloud.google.com/traces
```

### Cloud Logging
View application logs:
```
https://console.cloud.google.com/logs
```

Filter logs by service:
```
resource.type="k8s_container"
resource.labels.container_name="library-api"
```

## Database Schema

### Books Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| title | String | Book title |
| author | String | Book author |
| isbn | String | Unique ISBN |
| description | String | Book description |
| published_year | Integer | Year published |
| rating | Float | Average rating (0-5) |
| vote_count | Integer | Number of votes |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

## Scaling

The deployment is configured with:
- **Horizontal Pod Autoscaling**: 1-5 replicas based on CPU/memory
- **Resource requests**: 256Mi memory, 250m CPU
- **Resource limits**: 512Mi memory, 500m CPU

To manually scale:

```bash
kubectl scale deployment library-api --replicas=5
```

## Development

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up local PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/library"
```

3. Run the application:
```bash
uvicorn main:app --reload --port 8080
```

4. Access the API at `http://localhost:8080/docs`

### Project Organization

The project follows a layered architecture pattern. Each layer has specific responsibilities:

- **Models**: Define database tables
- **Schemas**: Validate and serialize data
- **Repositories**: Handle database operations
- **Services**: Implement business logic
- **Routers**: Define HTTP endpoints
- **Config**: Manage application configuration

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed information about the architecture, data flow, and best practices.

### Adding New Features

Follow the layered architecture pattern:

1. **Define model** in `models/` if needed
2. **Create schema** in `schemas/` for validation
3. **Add repository method** in `repositories/` for database access
4. **Implement service** in `services/` for business logic
5. **Create router endpoint** in `routers/` for HTTP handling

Example in [ARCHITECTURE.md](ARCHITECTURE.md).

### Testing

```
tests/
├── unit/
│   ├── test_repositories.py
│   ├── test_services.py
│   └── test_routers.py
└── integration/
    └── test_api.py
```

Run tests:
```bash
pytest tests/
```

## Cleanup

To delete all resources:

```bash
# Delete Kubernetes resources
kubectl delete -f kubernetes/deployment.yaml

# Delete GKE cluster
gcloud container clusters delete library-cluster --region=us-central1

# Delete Cloud SQL instance
gcloud sql instances delete library-db

# Delete service account
gcloud iam service-accounts delete library-api@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## Documentation

- **README.md** (this file): Quick start and API usage
- **ARCHITECTURE.md**: Detailed architecture documentation, layer responsibilities, data flow, and best practices

## License

This project is provided as-is for educational and commercial use.
