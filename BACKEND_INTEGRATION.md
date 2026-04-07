# 🔗 Integración Backend - Ejemplos

## Integrar Supabase con FastAPI

Este archivo contiene ejemplos de cómo integrar Supabase con tu backend FastAPI.

---

## 1. Instalar Cliente Supabase para Python

```bash
pip install supabase
```

---

## 2. Configurar Cliente Supabase en FastAPI

Crear archivo `supabase_client.py` en backend:

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Cliente con Service Role Key (acceso completo, solo en backend)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
```

---

## 3. Ejemplos de Endpoints

### Obtener Límites de Alerta del Usuario

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi_jwt_bearer import JWTBearer

app = FastAPI()
security = JWTBearer()

@app.get("/api/alert-limits")
async def get_alert_limits(token: str = Depends(security)):
    """Obtener límites de alerta del usuario autenticado"""
    try:
        # Obtener ID del usuario del token
        user_id = token  # (deberías extraer del JWT)
        
        # Consultar Supabase
        response = supabase.table("alert_limits").select("*").eq(
            "user_id", user_id
        ).execute()
        
        if response.data:
            return response.data[0]
        else:
            # Retornar límites por defecto
            return {
                "ph_min": 6.5,
                "ph_max": 8.5,
                "temp_min": 15,
                "temp_max": 30,
                "turbidity_max": 5
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Registrar Lectura de Sensor

```python
from datetime import datetime

@app.post("/api/sensor-reading")
async def save_sensor_reading(reading: dict, token: str = Depends(security)):
    """Guardar lectura de sensor"""
    try:
        user_id = token  # Extraer del JWT
        
        data = {
            "user_id": user_id,
            "device_id": reading["device_id"],
            "sensor_name": reading["sensor_name"],
            "value": reading["value"],
            "unit": reading["unit"],
            "status": reading.get("status", "normal"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("sensor_readings").insert([data]).execute()
        
        return {"success": True, "id": response.data[0]["id"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Verificar Alertas Activas

```python
@app.get("/api/check-alerts")
async def check_alerts(reading: dict, token: str = Depends(security)):
    """Verificar si hay alertas basado en límites configurados"""
    try:
        user_id = token
        
        # Obtener límites del usuario
        limits_response = supabase.table("alert_limits").select("*").eq(
            "user_id", user_id
        ).execute()
        
        if not limits_response.data:
            return {"alert": False, "message": "Sin límites configurados"}
        
        limits = limits_response.data[0]
        
        # Verificar según sensor
        sensor_name = reading["sensor_name"]
        value = reading["value"]
        alerts = []
        
        if sensor_name == "pH":
            if value < limits["ph_min"] or value > limits["ph_max"]:
                alerts.append(f"pH fuera de rango ({value})")
        
        elif sensor_name == "Temperatura":
            if value < limits["temp_min"] or value > limits["temp_max"]:
                alerts.append(f"Temperatura fuera de rango ({value}°C)")
        
        elif sensor_name == "Turbidez":
            if value > limits["turbidity_max"]:
                alerts.append(f"Turbidez elevada ({value} NTU)")
        
        return {
            "alert": len(alerts) > 0,
            "messages": alerts,
            "severity": "critical" if alerts else "normal"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Obtener Todos los Usuarios (Admin)

```python
@app.get("/api/admin/users")
async def get_all_users(token: str = Depends(security)):
    """Obtener lista de todos los usuarios (solo admin)"""
    try:
        # Verificar que es admin
        admin_check = supabase.table("users_roles").select("role").eq(
            "id", token
        ).execute()
        
        if not admin_check.data or admin_check.data[0]["role"] != "admin":
            raise HTTPException(status_code=403, detail="No es administrador")
        
        # Obtener todos los usuarios
        response = supabase.table("users_roles").select("*").execute()
        
        return response.data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Crear Usuario (Admin)

```python
from supabase.lib.auth_admin import AdminAuthClient

@app.post("/api/admin/create-user")
async def create_user_admin(
    email: str,
    password: str,
    full_name: str,
    role: str = "user",
    token: str = Depends(security)
):
    """Crear usuario como administrador"""
    try:
        # Verificar admin
        admin_check = supabase.table("users_roles").select("role").eq(
            "id", token
        ).execute()
        
        if not admin_check.data or admin_check.data[0]["role"] != "admin":
            raise HTTPException(status_code=403, detail="No es administrador")
        
        # Crear usuario en auth
        user = supabase.auth.admin.create_user(
            email=email,
            password=password,
            user_metadata={"full_name": full_name}
        )
        
        # Crear entrada en users_roles
        supabase.table("users_roles").insert([{
            "id": user.user.id,
            "email": email,
            "full_name": full_name,
            "role": role
        }]).execute()
        
        # Crear límites por defecto
        supabase.table("alert_limits").insert([{
            "user_id": user.user.id,
            "ph_min": 6.5,
            "ph_max": 8.5,
            "temp_min": 15,
            "temp_max": 30,
            "turbidity_max": 5
        }]).execute()
        
        return {"success": True, "user_id": user.user.id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 4. Archivo requirements.txt

```txt
fastapi==0.104.1
uvicorn==0.24.0
supabase==2.4.0
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
```

---

## 5. Archivo .env Backend

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT
SECRET_KEY=tu-clave-secreta

# API
API_PORT=8000
```

---

## 6. Ejemplo Completo de main.py

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_bearer import JWTBearer
from supabase import create_client
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Crear app
app = FastAPI(title="Monitoreo Embalse API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT
security = JWTBearer()

# Rutas

@app.get("/")
async def root():
    return {"status": "ok", "service": "Monitoreo Embalse"}

@app.get("/api/health")
async def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/alert-limits")
async def get_alert_limits(token: str = Depends(security)):
    """Obtener límites de alerta del usuario"""
    try:
        response = supabase.table("alert_limits").select("*").eq(
            "user_id", token
        ).execute()
        
        return response.data[0] if response.data else {
            "ph_min": 6.5, "ph_max": 8.5,
            "temp_min": 15, "temp_max": 30,
            "turbidity_max": 5
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sensor-reading")
async def save_reading(
    device_id: str,
    sensor_name: str,
    value: float,
    unit: str,
    token: str = Depends(security)
):
    """Guardar lectura de sensor"""
    try:
        data = {
            "user_id": token,
            "device_id": device_id,
            "sensor_name": sensor_name,
            "value": value,
            "unit": unit,
            "status": "normal",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("sensor_readings").insert([data]).execute()
        return {"success": True, "id": response.data[0]["id"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sensor-history/{device_id}")
async def get_sensor_history(
    device_id: str,
    limit: int = 100,
    token: str = Depends(security)
):
    """Obtener historial de sensor"""
    try:
        response = supabase.table("sensor_readings").select("*").eq(
            "device_id", device_id
        ).eq(
            "user_id", token
        ).order("timestamp", desc=True).limit(limit).execute()
        
        return response.data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 7. Integrar en Componentes Vue

### Obtener Límites en Dashboard

```javascript
// En Dashboard.vue o un composable
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

export async function loadAlertLimits() {
  const authStore = useAuthStore()
  
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/alert-limits`,
      {
        headers: {
          'Authorization': `Bearer ${authStore.user?.id}`
        }
      }
    )
    return response.data
  } catch (error) {
    console.error('Error cargando límites:', error)
    return null
  }
}
```

### Enviar Lecturas de Sensores

```javascript
export async function sendSensorReading(deviceId, sensorName, value, unit) {
  const authStore = useAuthStore()
  
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/sensor-reading`,
      {
        device_id: deviceId,
        sensor_name: sensorName,
        value: value,
        unit: unit
      },
      {
        headers: {
          'Authorization': `Bearer ${authStore.user?.id}`
        }
      }
    )
    return response.data
  } catch (error) {
    console.error('Error enviando lectura:', error)
  }
}
```

---

## 8. Middleware de Autenticación

```python
from fastapi import Request
from fastapi.exceptions import HTTPException
import jwt

async def verify_token(request: Request):
    """Middleware para verificar JWT"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="No auth header")
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid scheme")
        
        # Verificar con Supabase
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## 9. Notas Importantes

1. **Service Role Key vs Anon Key:**
   - Service Role Key: Usar en backend (acceso completo)
   - Anon Key: Usar en frontend (acceso restringido por RLS)

2. **Seguridad:**
   - Nunca exponer Service Role Key
   - Usar HTTPS en producción
   - Validar tokens siempre

3. **Performance:**
   - Cachear límites de alerta
   - Usar índices en base de datos
   - Batching para múltiples lecturas

4. **Error Handling:**
   - Capturar excepciones de Supabase
   - Retornar errores descriptivos
   - Loguear todo

---

Esta integración te permitirá tener un backend completamente funcional con autenticación Supabase.
