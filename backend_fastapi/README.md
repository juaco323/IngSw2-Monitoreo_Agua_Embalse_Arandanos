# Backend FastAPI - Embalse Arandanos

## 1. Instalar dependencias

```bash
pip install -r backend_fastapi/requirements.txt
```

## 2. Ejecutar servidor

```bash
uvicorn backend_fastapi.main:app --reload --port 8000
```

## 3. Swagger y ReDoc

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Endpoints principales

- `GET /health`
- `GET /api/dashboard`
- `GET /api/alerts`
- `POST /api/alerts`
- `GET /api/alerts/{alert_id}`
