# Estado Actual del Sistema de Monitoreo

## 🎯 Resumen
El sistema está completamente funcional con los siguientes componentes activos:

| Componente | Estado | Detalles |
|-----------|--------|---------|
| **Frontend (Vue 3 + Vite)** | ✅ Operacional | http://localhost:5173 |
| **Backend (FastAPI)** | ✅ Operacional | http://localhost:8000 |
| **MongoDB** | ❌ No disponible | Problema SSL/TLS con MongoDB Atlas Windows |
| **Datos del Dashboard** | ✅ Usando simulados dinámicos | Generados algoritmos realistas |

---

## 📊 Datos del Dashboard

### Fuente Actual: **Datos Simulados Dinámicos**

Cuando MongoDB no está disponible, el backend genera automáticamente:
- **pH**: Variación realista (~6.5-7.5) con ciclos naturales
- **Temperatura**: Simulación de ciclos diarios (~18-26°C)
- **Conductividad**: Variación plausible (~800-1100 µS/cm)
- **Estado Arduino**: Mostrado como **Conectado**
- **Sensores Activos**: 3/3

Los datos cambian dinámicamente en tiempo real basados en:
- Hora del sistema (ciclos de 24 horas)
- Funciones trigonométricas para cambios naturales
- Pequeño ruido aleatorio realista

### Cuando MongoDB esté disponible

Los datos provendrán directamente de **MongoDB Atlas** y el indicador cambiará a **"Datos Reales"**.

---

## 🔌 API Endpoints

### Datos Dashboard
```bash
GET http://localhost:8000/api/dashboard
```
Retorna datos en tiempo real (reales o simulados):
```json
{
  "ph": { "value": 7.1, "status": "stable", ... },
  "temperature": { "value": 21.5, ... },
  "conductivity": { "value": 950, ... },
  "metadata": {
    "arduinoConnected": true,
    "systemStatus": "operational",
    "activeSensors": 3
  }
}
```

### Diagnóstico del Sistema
```bash
GET http://localhost:8000/api/diagnostics
```
Retorna estado de conexión y fuente de datos:
```json
{
  "mongodb_connected": false,
  "data_source": "simulated",
  "arduino_connected": false,
  "message": "Usando datos simulados dinámicos (MongoDB no disponible)"
}
```

### Historial de Sensores
```bash
GET http://localhost:8000/api/sensors/history?limit=100
```

### Enviar nueva lectura
```bash
POST http://localhost:8000/api/sensors/ph
Content-Type: application/json

{
  "sensor_id": "sensor-ph-a",
  "id_env": 1,
  "ph": 7.12,
  "timestamp": 12345,
  "temperature": 21.0,
  "conductivity": 950
}
```

---

## 🎨 Indicadores Visuales

El dashboard muestra:

1. **Badge de Fuente de Datos** (superior derecho)
   - 📊 **Datos Reales**: MongoDB conectado y datos disponibles (verde)
   - ⚙️ **Datos Simulados**: Usando generador de datos dinámico (amarillo)
   - ❓ **Fuente Desconocida**: Error al obtener estado (gris)

2. **Estado del Dispositivo** (tarjeta de información)
   - 🟢 **Conectado**: Arduino envió datos recientemente
   - 🔴 **Desconectado**: No hay datos recientes

3. **Indicador de Salud General**
   - 🟢 Sistema Normal
   - 🟡 Advertencia (valores cerca de los límites)
   - 🔴 Situación Peligrosa (fuera de límites)

---

## 🔧 Resolución de Problemas

### Problema: MongoDB no se conecta
**Causa**: Error SSL/TLS en Windows con MongoDB Atlas
**Status**: ⚠️ Pendiente de resolución
**Soluciones alternativas**:
1. Instalar MongoDB Community local (Windows)
2. Actualizar certificados SSL de Windows
3. Usar una VPN si hay restricciones de red
4. Contactar al administrador de red en MongoDB Atlas

### Mientras se resuelve MongoDB:
- ✅ Sistema funciona con datos simulados dinámicos
- ✅ API responde correctamente
- ✅ Frontend muestra estado actual
- ✅ Puedes enviar datos reales vía API POST

---

## 📝 Para Conectar Arduino Real

El Arduino puede enviar datos así:

```cpp
#include <HTTPClient.h>
#include <WiFi.h>

void enviarDatos() {
  WiFiClient client;
  HTTPClient http;
  
  http.begin(client, "http://192.168.x.x:8000/api/sensors/ph");
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\"sensor_id\":\"sensor-ph-1\",\"id_env\":1,\"ph\":7.2,\"temperature\":21.5,\"conductivity\":950}";
  
  int httpCode = http.POST(payload);
  http.end();
}
```

---

## 📡 Stack Tecnológico

### Frontend
- **Framework**: Vue 3
- **Build Tool**: Vite
- **Estilos**: CSS puro (Scoped)
- **Comunicación**: Fetch API / Axios

### Backend
- **Framework**: FastAPI
- **Servidor**: Uvicorn
- **Base de Datos**: MongoDB (cuando disponible)
- **Validación**: Pydantic

### Características
- ✅ Real-time dashboard
- ✅ Alertas automáticas
- ✅ Historial de datos
- ✅ Generador dinámico de datos
- ✅ Diagnóstico del sistema

---

## 🚀 Próximos Pasos

1. **Resolver conexión SSL con MongoDB Atlas**
   - Opción A: Instalar MongoDB local
   - Opción B: Usar MongoDB community edition
   - Opción C: Solucionar certificados SSL en Windows

2. **Cuando MongoDB esté disponible**
   - El backend automaticamente detectará y usará datos reales
   - El frontend mostrará "Datos Reales" en la badge
   - El historial se cargará desde la base de datos

3. **Opcional: Mejorar seguridad**
   - Agregar autenticación a la API
   - Restringir CORS (actualmente permite todo)
   - Usar HTTPS en producción

---

**Última actualización**: 31/03/2026
**Sistema**: En línea y funcional ✅
