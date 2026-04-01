# Deploy del sistema (Docker + Vercel)

## Importante
Vercel **no soporta desplegar docker-compose** para correr frontend + backend + MongoDB en el mismo proyecto.

Estrategia recomendada:
- Frontend Vue/Vite en Vercel.
- Backend FastAPI en Render, Railway, Fly.io, VPS o similar.
- MongoDB en Atlas (o en un servidor propio).

## 1) Levantar todo localmente con Docker
Desde la raíz del proyecto:

```bash
docker compose up -d --build frontend backend mongodb
```

Servicios:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- MongoDB: mongodb://localhost:27017

## 2) Deploy del backend (fuera de Vercel)
Puedes usar el Dockerfile en backend_fastapi/Dockerfile.

Variables mínimas:
- MONGODB_URL
- MONGODB_DB
- SIMULATED_DATA_ENABLED=false

## 3) Deploy del frontend en Vercel
En Vercel configura:
- Framework Preset: Vite
- Build Command: npm run build
- Output Directory: dist

Variable de entorno requerida:
- VITE_API_URL=https://TU_BACKEND_PUBLICO

Ejemplo:
- VITE_API_URL=https://api-tu-proyecto.onrender.com

## 4) CORS
El backend ya tiene CORS abierto para todos los orígenes. Si luego quieres cerrar seguridad, limita orígenes al dominio de Vercel.

## 5) Flujo final en producción
ESP8266 -> Backend FastAPI -> MongoDB
Frontend Vercel -> Backend FastAPI
