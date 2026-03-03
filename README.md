# Learning Tracker API

A fully-featured REST API for tracking learning progress across 8 technology categories.

**Stack:** FastAPI · SQLAlchemy · SQLite in-memory · Pydantic v2 · pytest

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn app.main:app --reload --port 8000

# 3. Open Swagger UI
open http://localhost:8000/docs

# 4. Run tests
pytest tests/ -v
```

---

## 🐳 Docker Deployment

To run the application securely without baking your secrets into the image, use runtime environment injection.

### 1. Build the image
```bash
docker build -t synaptic-api .
```

### 2. Run with environment variables
Ensure you have your `.env` file ready with your `GDRIVE` credentials, then run:
```bash
docker run --env-file .env -p 8000:8000 synaptic-api
```
*Note: This injects your secrets at runtime, keeping them out of the image layers.*

---

## Architecture

```
Request → Router → Service → Repository → SQLAlchemy → SQLite in-memory
```

| Layer | Responsibility |
|-------|----------------|
| **Routers** | HTTP request parsing, response formatting via `APIResponse[T]` |
| **Services** | Business logic, validation, cascading updates |
| **Repositories** | Data access abstraction, query construction |
| **Models** | SQLAlchemy ORM table definitions |
| **Schemas** | Pydantic v2 input/output validation |

---

## API Endpoints

### Topics `/api/topics`
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/topics/create` | Create a new topic |
| `GET` | `/api/topics/{id}` | Get topic with subtopics, notes, resources |
| `POST` | `/api/topics/{id}/mark-completed` | Mark topic as completed |
| `POST` | `/api/topics/{id}/mark-in-progress` | Mark topic as in-progress |
| `POST` | `/api/topics/{id}/mark-to-learn` | Reset topic to to-learn |

### SubTopics
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/topics/{id}/subtopics/create` | Create a subtopic |
| `GET` | `/api/topics/{id}/subtopics` | List subtopics |
| `POST` | `/api/subtopics/{id}/mark-completed` | Complete subtopic + cascade progress |
| `POST` | `/api/subtopics/{id}/mark-in-progress` | Mark in-progress |
| `DELETE` | `/api/subtopics/{id}` | Delete subtopic + update progress |

### Users
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/users/{id}/topics` | Topics grouped by category |
| `GET` | `/api/users/{id}/progress` | Overall + per-category progress |
| `GET` | `/api/users/{id}/categories/{category}` | Single category stats |
| `GET` | `/api/users/{id}/projects` | All user projects |

### Search
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/search/global?user_id=1&q=algo` | Cross-entity search (min 2 chars) |

### Projects
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/projects/create` | Create project |
| `POST` | `/api/projects/{id}/mark-completed` | Mark completed |
| `POST` | `/api/projects/{id}/add-topics` | Link topics to project |

### Notes
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/notes/create` | Create note for a topic |
| `PUT` | `/api/notes/{id}` | Update note |
| `DELETE` | `/api/notes/{id}` | Delete note |
| `GET` | `/api/notes/topic/{topic_id}` | Notes for a topic |

### Health
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |

---

## Progress Calculation

- **Topic progress** = `(completed subtopics / total subtopics) × 100` — auto-updated on every subtopic status change
- **Category progress** = `(completed topics / total topics) × 100`
- **Overall progress** = average of all 8 category percentages

---

## Learning Categories

| Key | Display Name |
|-----|-------------|
| `backend` | Backend Development |
| `system_design` | System Design |
| `dsa` | Data Structures & Algorithms |
| `frontend` | Frontend Development |
| `devops` | DevOps & Infrastructure |
| `database_design` | Database Design |
| `projects_portfolio` | Projects & Portfolio |
| `other` | Other |

---

## Response Format

All endpoints return a consistent envelope:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "error": null
}
```

---

## Testing

```bash
pytest tests/ -v                    # run all tests
pytest tests/test_topics.py -v      # specific file
pytest tests/ --tb=short            # shorter tracebacks
```

Tests use a fresh in-memory SQLite database per test via `conftest.py` dependency overrides.
