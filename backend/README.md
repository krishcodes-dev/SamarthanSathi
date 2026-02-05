# SamarthanSathi Backend

Crisis Need to Resource Matching Engine - FastAPI Backend

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Core configuration and database
│   │   ├── config.py        # Pydantic settings
│   │   └── database.py      # SQLAlchemy async setup
│   ├── models/              # SQLAlchemy models (Phase 2)
│   ├── schemas/             # Pydantic schemas (Phase 2)
│   ├── services/            # Business logic (Phase 3)
│   └── api/                 # API routes
│       └── health.py        # Health check endpoint
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+

### 2. Setup Virtual Environment

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download SpaCy Model

```bash
python -m spacy download en_core_web_md
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 6. Setup PostgreSQL Database

```bash
# Create database
createdb samarthansathi

# Or using psql:
psql -U postgres
CREATE DATABASE samarthansathi;
\q
```

### 7. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### Current Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API info |
| GET | `/health` | Health check + DB connectivity |

### Coming Soon (Phase 3-4)

- `POST /api/v1/request/submit` - Submit crisis request
- `GET /api/v1/request/{id}` - Get request details
- `GET /api/v1/matches/{request_id}` - Get resource matches
- `GET /api/v1/requests/queue` - Get urgency-sorted queue
- `POST /api/v1/dispatch/{request_id}/{resource_id}` - Dispatch resource

## 🧪 Testing

```bash
pytest
```

## 🔧 Development

### Database Migrations (Phase 2)

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Create initial tables"

# Apply migration
alembic upgrade head
```

### Code Quality

```bash
# Format code
black app/

# Lint
ruff check app/

# Type checking
mypy app/
```

## 🚢 Deployment

### Render.com

1. Create new Web Service
2. Connect GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_md`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`
5. Create PostgreSQL database and link

## 📚 Tech Stack

- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **NLP**: SpaCy 3.7 (en_core_web_md)
- **Geolocation**: geopy
- **Testing**: pytest + httpx

## 📖 Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [Pydantic V2 Docs](https://docs.pydantic.dev/latest/)

## 🎯 Development Phases

- [x] **Phase 1**: Project skeleton ✅
- [ ] **Phase 2**: Data contracts & models
- [ ] **Phase 3**: Business logic services
- [ ] **Phase 4**: API endpoints
- [ ] **Phase 5**: Frontend integration
- [ ] **Phase 6**: Testing & deployment

---

Built for the Crisis Response Hackathon 🚨
