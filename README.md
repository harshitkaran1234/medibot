# medibot

FastAPI service managed with Poetry.

## Setup

```bash
poetry install
```

## Run

```bash
poetry run uvicorn medibot.main:app --reload
```

Health check: http://localhost:8000/health · API docs: http://localhost:8000/docs

Env vars are loaded from `.env` (optional).

## Adding an API

Follow the `routes/v1/<feature>/` pattern:

```
medibot/routes/v1/<feature>/
├── __init__.py     # exports router
├── route.py        # APIRouter(prefix="/<feature>", tags=[...]) + endpoints
├── controller.py   # request handling logic
└── schema.py       # pydantic request/response models
```

Then register it in `medibot/routes/v1/__init__.py`. Shared business logic goes in `medibot/core/`.

## Test

```bash
poetry run pytest
```
