# Backend FastAPI - Embalse Arandanos

## 1. Instalar dependencias

```bash
pip install -r backend_fastapi/requirements.txt
```

## 2. Configurar MongoDB

Define la variable de entorno para conectar a MongoDB:

```bash
# Local
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=embalse_arandanos

# O MongoDB Atlas
MONGODB_URL=mongodb+srv://usuario:contraseña@cluster.mongodb.net/
MONGODB_DB=embalse_arandanos
```

**Instalación local (Windows):**
- Descarga desde https://www.mongodb.com/try/download/community
- Instala y ejecuta el servicio de MongoDB

**MongoDB Atlas (Nube):**
- Crea una cuenta en https://www.mongodb.com/cloud/atlas
- Crea un cluster
- Obtén la cadena de conexión

## 3. Configurar MailerSend (notificaciones por correo)

Define estas variables de entorno:

```bash
MAILERSEND_API_TOKEN=tu_api_token
MAILERSEND_FROM_EMAIL=alertas@tudominio.com
MAILERSEND_FROM_NAME=Monitoreo Embalse Arandanos
MAILERSEND_TO_EMAILS=destino1@correo.com,destino2@correo.com
```

## 4. Ejecutar servidor

```bash
uvicorn backend_fastapi.main:app --reload --port 8000
```

## 5. Swagger y ReDoc

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Endpoints principales

### Dashboard
- `GET /api/dashboard` - Obtener estado actual de sensores desde MongoDB

### Sensores (datos del ESP8266)
- `PUT /api/sensors/ph` - Recibir datos de sensores del ESP8266 (HTTP PUT)
- `POST /api/sensors/readings` - Recibir datos de sensores (HTTP POST)
- `GET /api/sensors/latest` - Obtener última lectura de MongoDB
- `GET /api/sensors/history?limit=100` - Obtener historial (últimas N lecturas)

### Alertas
- `GET /api/alerts` - Listar alertas
- `POST /api/alerts` - Crear nueva alerta
- `GET /api/alerts/{alert_id}` - Obtener alerta específica

## Flujo de datos ESP8266 → MongoDB → Frontend

1. **ESP8266 (arduino-code.ino)**
   - Lee sensores cada 1 segundo
   - Envía datos cada 10 segundos vía HTTP PUT a `/api/sensors/ph`
   - Formato JSON: `{"ph": 7.2, "temperature": 22.5, "conductivity": 650, "timestamp": 1234567890}`

2. **Backend FastAPI (main.py)**
   - Recibe datos en endpoint PUT `/api/sensors/ph`
   - Guarda en colección `sensor_readings` de MongoDB
   - Mantiene estado en memoria para dashboard rápido

3. **Frontend (Vue.js)**
   - Solicita dados con `GET /api/dashboard`
   - Obtiene estado actualizado desde MongoDB
   - Muestra gráficos y gauges en tiempo real

## Configuración del archivo .env

Copia `.env.example` a `.env` y completa los valores:

```bash
cp backend_fastapi/.env.example backend_fastapi/.env
```

## Ejemplo de solicitud desde ESP8266

```cpp
// Arduino/ESP8266 code
DynamicJsonDocument doc(256);
doc["ph"] = 7.2;
doc["temperature"] = 22.5;
doc["conductivity"] = 650;
doc["timestamp"] = millis() / 1000;

String jsonData;
serializeJson(doc, jsonData);

http.begin(client, "http://192.168.1.100:8000/api/sensors/ph");
http.addHeader("Content-Type", "application/json");
int httpCode = http.PUT(jsonData);
```

## Ejemplo `POST /api/alerts`

```json
{
	"embalse": "Embalse Norte",
	"nombreDispositivo": "Arduino Embalse A",
	"sensor": "Conductividad",
	"medicion": "2100 uS/cm",
	"valor": 2100,
	"minimo": 100,
	"maximo": 2000
}
```

El mensaje de correo incluye:

- Nombre dispositivo
- Dia
- Fecha
- Hora
- Sensor
- Medicion
