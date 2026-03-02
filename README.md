# SupportLens

Lightweight observability platform for a support chatbot.

## Run with Docker Compose

1. Create `.env` with at least:

```env
OPENAI_API_KEY=your_key_here
LLM_MODEL=gpt-4o-mini
```

2. Start stack:

```bash
docker compose up --build
```

3. Open dashboard at `http://localhost:5000`.

## Services

- `frontend`: Nginx serving static production assets and reverse-proxying API requests.
- `backend`: Flask + Gunicorn API.
- `db`: PostgreSQL with persistent volume `db_data`.

## API Endpoints

- `GET /health`
- `POST /api/chat`
- `POST /api/traces`
- `GET /api/traces`
- `GET /api/analytics`
- `GET /api/analytics/trends`
