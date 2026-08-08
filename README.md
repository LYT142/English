# AI Academic English Training Platform

A deployable FastAPI web app for academic English practice. It provides guided exercises for abstract rewriting, vocabulary precision, translation, and formal revision, then returns instant AI-style feedback from a deterministic rubric.

## Features

- Chinese/English landing page for academic English training.
- REST API for listing exercises and evaluating submissions.
- Docker Compose stack with FastAPI, PostgreSQL, Redis, and Milvus dependencies.
- GitHub Actions workflow for Python syntax and API smoke checks.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload
```

Open <http://localhost:8000>.

## Docker deployment

```bash
docker compose up --build
```

The web app is available at <http://localhost:8000> and the API health endpoint is <http://localhost:8000/health>.
