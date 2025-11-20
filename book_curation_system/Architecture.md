# Layered Architecture Documentation

## Project Structure

```
library-api/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container definition
├── cloudbuild.yaml                 # CI/CD configuration
├── setup.sh                        # Infrastructure setup
│
├── models/                         # Data Models Layer
│   ├── __init__.py
│   └── database.py                 # SQLAlchemy ORM models
│
├── schemas/                        # Schema/DTO Layer
│   ├── __init__.py
│   └── book.py                     # Pydantic schemas for validation
│
├── repositories/                   # Repository Layer
│   ├── __init__.py
│   └── book_repository.py          # Database access logic
│
├── services/                       # Service/Business Logic Layer
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

## Architecture Layers

### 1. **Models Layer** (`models/`)
**Purpose**: Define database schema and ORM models

- **database.py**: SQLAlchemy models representing database tables
- Contains the `Book` model with all database columns
- Declarative base for table creation

**Dependencies**: SQLAlchemy only

### 2. **Schemas Layer** (`schemas/`)
**Purpose**: Data validation and serialization

- **book.py**: Pydantic models for request/response validation
  - `BookBase`: Common fields
  - `BookCreate`: Creation payload
  - `BookUpdate`: Update payload (partial)
  - `BookResponse`: API response format
  - `VoteRequest`: Vote validation
  - `HealthResponse`: Health check response

**Dependencies**: Pydantic

### 3. **Configuration Layer** (`config/`)
**Purpose**: Application configuration and setup

- **database.py**: Database engine, session management, and dependency injection
- **telemetry.py**: OpenTelemetry and Google Cloud Logging setup

**Dependencies**: SQLAlchemy, OpenTelemetry, Google Cloud SDK

### 4. **Repository Layer** (`repositories/`)
**Purpose**: Database access abstraction (Data Access Layer)

- **book_repository.py**: All database operations for books
  - `create()`: Insert new book
  - `get_by_id()`: Retrieve by ID
  - `get_by_isbn()`: Retrieve by ISBN
  - `get_all()`: List with pagination
  - `update()`: Update existing book
  - `delete()`: Remove book
  - `add_vote()`: Add vote and recalculate rating

**Key Principles**:
- Pure database operations
- No business logic
- Returns ORM models
- Session management via dependency injection

**Dependencies**: SQLAlchemy, Models

### 5. **Service Layer** (`services/`)
**Purpose**: Business logic and orchestration

- **book_service.py**: Book business operations
  - Validates business rules (e.g., ISBN uniqueness)
  - Coordinates repository calls
  - Handles exceptions and error responses
  - Converts ORM models to Pydantic schemas
  - Implements tracing and logging

- **health_service.py**: Health check operations
  - Fetches GCP metadata
  - Formats health response

**Key Principles**:
- Business logic lives here
- Orchestrates multiple repositories if needed
- Handles transactions
- Returns Pydantic schemas (not ORM models)
- Implements observability (traces, logs)

**Dependencies**: Repository, Schemas, Config

### 6. **Router Layer** (`routers/`)
**Purpose**: HTTP endpoint definitions (Controller/Presentation Layer)

- **books.py**: Book CRUD and voting endpoints
  - Defines routes and HTTP methods
  - Request/response models
  - Dependency injection for database sessions
  - Delegates to service layer

- **health.py**: Health and root endpoints

**Key Principles**:
- Thin layer - just routing
- HTTP concerns only (status codes, headers)
- No business logic
- Dependency injection
- API documentation via docstrings

**Dependencies**: Services, Schemas, FastAPI

### 7. **Application Layer** (`main.py`)
**Purpose**: Application initialization and configuration

- Creates FastAPI app
- Configures middleware (CORS)
- Instruments OpenTelemetry
- Includes routers
- Creates database tables

**Dependencies**: All layers

## Data Flow

### Request Flow (Example: Create Book)
```
1. HTTP Request
   ↓
2. Router Layer (routers/books.py)
   - Validates request via Pydantic schema
   - Injects database session
   ↓
3. Service Layer (services/book_service.py)
   - Applies business rules (check ISBN uniqueness)
   - Starts tracing span
   - Logs operation
   ↓
4. Repository Layer (repositories/book_repository.py)
   - Executes SQL via SQLAlchemy
   - Returns ORM model
   ↓
5. Service Layer
   - Converts ORM model to Pydantic schema
   - Returns to router
   ↓
6. Router Layer
   - Returns HTTP response with status code
   ↓
7. HTTP Response
```

### Database Query Flow (Example: Get Book)
```
1. Router receives request with book_id
   ↓
2. Service validates request
   ↓
3. Repository queries database
   SELECT * FROM books WHERE id = ?
   ↓
4. Repository returns ORM model (or None)
   ↓
5. Service checks if book exists
   - If not: raises HTTPException(404)
   - If yes: converts to BookResponse schema
   ↓
6. Router returns JSON response
```

## Layer Responsibilities

| Layer | Responsibilities | Should NOT |
|-------|-----------------|------------|
| **Models** | Database schema definition | Contain business logic, validation |
| **Schemas** | Request/response validation | Access database, contain business logic |
| **Config** | Setup and configuration | Contain business logic |
| **Repository** | Database operations | Validate business rules, handle HTTP |
| **Service** | Business logic, orchestration | Handle HTTP directly, define schemas |
| **Router** | HTTP routing, endpoint definition | Contain business logic, access DB directly |
| **Main** | Application setup | Contain business logic |

## Benefits of This Architecture

### 1. **Separation of Concerns**
Each layer has a single, well-defined responsibility

### 2. **Testability**
- Mock repositories in service tests
- Mock services in router tests
- Test business logic independently

### 3. **Maintainability**
- Easy to locate code (clear structure)
- Changes isolated to specific layers
- Reduce coupling between components

### 4. **Reusability**
- Services can be used by multiple routers
- Repositories can be used by multiple services
- Easy to add new endpoints

### 5. **Scalability**
- Easy to add new features
- Clear patterns to follow
- Team members know where to add code

### 6. **Database Independence**
- Repository abstracts database operations
- Easy to switch databases
- Easy to add caching layer

## Example: Adding a New Feature

**Task**: Add author search functionality

### 1. Repository Layer
```python
# repositories/book_repository.py
@staticmethod
def search_by_author(db: Session, author: str) -> List[Book]:
    return db.query(Book).filter(Book.author.ilike(f"%{author}%")).all()
```

### 2. Service Layer
```python
# services/book_service.py
def search_books_by_author(self, db: Session, author: str) -> List[BookResponse]:
    with tracer.start_as_current_span("service_search_author"):
        books = self.repository.search_by_author(db, author)
        logger.info(f"Found {len(books)} books by author: {author}")
        return [BookResponse.model_validate(book) for book in books]
```

### 3. Router Layer
```python
# routers/books.py
@router.get("/search", response_model=List[BookResponse])
async def search_books(author: str, db: Session = Depends(get_db)):
    """Search books by author name"""
    return book_service.search_books_by_author(db, author)
```

## Testing Strategy

### Unit Tests
- **Repository**: Test with in-memory SQLite
- **Service**: Mock repository, test business logic
- **Router**: Mock service, test HTTP handling

### Integration Tests
- Test full request flow
- Use test database
- Verify end-to-end functionality

### Example Test Structure
```
tests/
├── unit/
│   ├── test_repositories.py
│   ├── test_services.py
│   └── test_routers.py
├── integration/
│   └── test_api.py
└── conftest.py  # Pytest fixtures
```

## Best Practices

1. **Never skip layers** - Always go through the proper layer hierarchy
2. **Keep services thin but smart** - Complex logic goes here, not routers
3. **Repositories are dumb** - Just CRUD operations, no business rules
4. **Use dependency injection** - Makes testing easier
5. **Return appropriate types** - Repositories return ORM, Services return Pydantic
6. **Handle errors at service layer** - Services raise HTTPExceptions
7. **Log at service layer** - Centralized logging
8. **Trace at service layer** - OpenTelemetry spans in services