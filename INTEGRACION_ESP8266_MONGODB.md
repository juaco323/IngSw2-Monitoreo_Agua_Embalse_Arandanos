# Guía de Integración: ESP8266 → MongoDB → Frontend

## 🎯 Resumen de la Integración

Este proyecto conecta un **ESP8266 con sensores de agua** que envía datos a una **API FastAPI** que los guarda en **MongoDB** y los muestra en un **Frontend Vue.js**.

```
ESP8266 (sensores)
    ↓ HTTP PUT
API FastAPI (puerto 8000)
    ↓ INSERT
MongoDB (base de datos)
    ↓ READ
Frontend Vue.js
```

---

## 📱 1. CONFIGURACIÓN DEL ESP8266

### Archivos modificados:
- **arduino-code.ino** - Código actualizado para ESP8266 con WiFi

### Requisitos:
1. **Hardware**: ESP8266 (NodeMCU o similar)
2. **Librerías Arduino**:
   - `ESP8266WiFi` (incluida)
   - `ESP8266HTTPClient` (incluida)
   - `ArduinoJson` (descargar)
   - `OneWire` (descargar)
   - `DallasTemperature` (descargar)

### Configuración:

Abre `arduino-code.ino` y modifica estas líneas:

```cpp
// Líneas 37-39 - Reemplazar con tu red WiFi
const char *ssid = "TU_SSID";           // tu red WiFi
const char *password = "TU_PASSWORD";   // tu contraseña
const char *api_url = "http://192.168.1.100:8000"; // IP de tu API
```

### Pasos para cargar:

1. Arduino IDE → Herramientas → Board → Selecciona "NodeMCU 1.0"
2. Herramientas → Puerto → Selecciona puerto COM
3. Sketch → Cargar
4. Abre Monitor Serial (115200 baud) para ver logs

### Logs esperados:
```
[WiFi] Conectado exitosamente
[WiFi] IP: 192.168.1.150
[HTTP] Enviando datos:
{"ph":7.2,"temperature":22.5,"conductivity":650,"timestamp":123456}
[HTTP] Respuesta: 200
[HTTP] Datos guardados exitosamente en MongoDB
```

---

## 🖥️ 2. CONFIGURACIÓN DEL BACKEND (FastAPI)

### Archivos modificados:
- **backend_fastapi/main.py** - Código actualizado con MongoDB
- **backend_fastapi/requirements.txt** - Nuevas dependencias agregadas
- **backend_fastapi/.env.example** - Variables de entorno

### Requisitos:
1. **MongoDB instalado localmente** o **MongoDB Atlas (nube)**
2. **Python 3.9+**

### Instalación:

#### Local (Windows):

1. Descarga MongoDB desde: https://www.mongodb.com/try/download/community
2. Instala en C:\Program Files\MongoDB\Server\6.0
3. El servicio se inicia automáticamente

Verifica que esté corriendo:
```powershell
# En PowerShell
Get-Service MongoDB | Start-Service
```

#### MongoDB Atlas (Nube):

1. Crea cuenta en https://www.mongodb.com/cloud/atlas
2. Crea un cluster (M0 es gratis)
3. Copia la cadena de conexión

### Configurar variables de entorno:

```bash
# Copia el archivo ejemplo
cp backend_fastapi/.env.example backend_fastapi/.env

# Edita backend_fastapi/.env con tus valores:
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=embalse_arandanos
MAILERSEND_API_TOKEN=tu_token (opcional)
...
```

### Instalar dependencias:

```bash
cd backend_fastapi
pip install -r requirements.txt
```

### Ejecutar API:

```bash
uvicorn main:app --reload --port 8000
```

Verifica en: http://localhost:8000/docs

---

## 🎨 3. CONFIGURACIÓN DEL FRONTEND (Vue.js)

### Archivos modificados:
- **src/services/ArduinoConfig.js** - Funciones para conectar a FastAPI

### Configuración:

Asegúrate que `vite.config.js` tenga la configuración correcta:

```javascript
// vite.config.js
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000' // Proxy a FastAPI
    }
  }
})
```

### Usar en App.vue:

```javascript
import { startDashboardPolling, stopDashboardPolling } from '@/services/ArduinoConfig'
import { onMounted, onUnmounted, ref } from 'vue'

export default {
  setup() {
    const sensors = ref({
      ph: { value: 0 },
      temperature: { value: 0 },
      conductivity: { value: 0 }
    })
    let pollingId = null

    const updateSensorData = (dashboardData) => {
      sensors.value.ph = dashboardData.ph
      sensors.value.temperature = dashboardData.temperature
      sensors.value.conductivity = dashboardData.conductivity
    }

    onMounted(() => {
      // Inicia polling automático cada 10 segundos
      pollingId = startDashboardPolling(updateSensorData, 10000)
    })

    onUnmounted(() => {
      // Detén polling cuando se desmonta
      stopDashboardPolling(pollingId)
    })

    return { sensors }
  }
}
```

---

## 🚀 4. FLUJO COMPLETO

### 1️⃣ ESP8266 Lee Sensores
```cpp
// Cada 1 segundo
readAllSensors()  // pH, Temperatura, Conductividad

// Cada 10 segundos
sendSensorDataToAPI()  // HTTP PUT a /api/sensors/ph
```

### 2️⃣ API Recibe y Guarda
```
PUT /api/sensors/ph
├─ Recibe JSON con datos
├─ Valida datos
├─ Guarda en MongoDB (colección: sensor_readings)
└─ Retorna {"status": "success", "id": "..."}
```

### 3️⃣ Frontend Obtiene Datos
```
GET /api/dashboard (polling cada 10s)
├─ Lee última lectura de MongoDB
├─ Calcula estado (stable/warning/critical)
└─ Actualiza UI (gráficos, gauges, etc)
```

---

## 📊 5. MONGODB - ESTRUCTURA DE DATOS

### Colección: `sensor_readings`

```json
{
  "_id": ObjectId("..."),
  "ph": 7.2,
  "temperature": 22.5,
  "conductivity": 650,
  "timestamp": ISODate("2026-03-30T15:30:00Z"),
  "created_at": ISODate("2026-03-30T15:30:00Z")
}
```

### Ver datos en MongoDB:

```bash
# Abrir mongo client
mongosh

# Conectar a BD
use embalse_arandanos

# Ver colecciones
show collections

# Ver últimas lecturas
db.sensor_readings.find().sort({timestamp: -1}).limit(10)
```

---

## 🔍 6. TROUBLESHOOTING

### ❌ ESP8266 no conecta a WiFi
- Verifica SSID y contraseña
- El router debe estar en 2.4GHz (ESP8266 no soporta 5GHz)
- Verifica que el ESP8266 esté alimentado correctamente

### ❌ API no recibe datos
- Verifica IP en arduino-code.ino
- Comprueba que API esté corriendo: `http://<IP>:8000/docs`
- Revisa logs del ESP8266 (Monitor Serial a 115200 baud)

### ❌ MongoDB no guarda datos
- Verifica que MongoDB esté corriendo
- Verifica MONGODB_URL en .env
- Revisa logs de FastAPI

### ❌ Frontend no muestra datos
- Abre inspeccionar (F12) → Console
- Verifica que API_BASE_URL sea correcto
- Comprueba conexión en Network

---

## 📝 7. ENDPOINTS DISPONIBLES

### Dashboard
```
GET /api/dashboard
Respuesta:
{
  "ph": { "value": 7.2, "status": "stable", ... },
  "temperature": { "value": 22.5, ... },
  "conductivity": { "value": 650, ... },
  "metadata": { "systemStatus": "operational", ... }
}
```

### Sensores
```
PUT /api/sensors/ph
POST /api/sensors/readings
GET /api/sensors/latest
GET /api/sensors/history?limit=100
```

### Alertas
```
GET /api/alerts
POST /api/alerts
GET /api/alerts/{id}
```

---

## 🎓 8. PRÓXIMOS PASOS

1. ✅ Configura ESP8266
2. ✅ Instala MongoDB
3. ✅ Ejecuta FastAPI
4. ✅ Prueba Frontend
5. 📊 Agrega gráficos históricos
6. 📧 Configura alertas por email
7. 🔔 Implementa notificaciones en tiempo real

---

## 📞 SOPORTE

Para más ayuda:
- 📖 Documentación API: http://localhost:8000/docs
- 🔗 MongoDB Docs: https://docs.mongodb.com
- 🚀 FastAPI: https://fastapi.tiangolo.com
- 💬 Vue.js: https://vuejs.org
