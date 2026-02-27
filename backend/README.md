# Backend (FastAPI) — AGE-FIVE

## Requisitos
- Python 3.10+
- MongoDB local (recomendado: `docker-compose up -d` en la raíz del repo)

## Setup
```bash
cd backend
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

## Ejecutar
```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints
- `GET /health`
- `GET /api/players/search`
- `GET /api/player?name=...&squad=...`
- `GET /api/filters/squads`
- `GET /api/filters/comps`
- `GET /api/filters/pos`
- `GET /api/filters/rangos`
- `GET /api/filters/temporadas`
