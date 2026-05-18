# Diagrama de Integración - Indicador de Batería

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ARDUINO / ESP8266                           │
│                    (Lectura de Batería)                             │
│                           ↓                                         │
│                    "bateria": 85                                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND FASTAPI (main.py)                        │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  POST /api/sensors/readings                                  │   │
│  │  ├─ Recibe: bateria (0-100)                                 │   │
│  │  ├─ Guarda en MongoDB                                        │   │
│  │  └─ Actualiza dashboard_state                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────┴───────────────────────────────────┐   │
│  │  GET /api/dashboard (response_model=DashboardResponse)       │   │
│  │  ├─ Incluye: battery field (int)                             │   │
│  │  ├─ Valor: reading.get("bateria", 100)                       │   │
│  │  └─ Retorna JSON con battery                                 │   │
│  └────────────────────────┬──────────────────────────────────────┘   │
└────────────────────────────┼──────────────────────────────────────────┘
                             │
                             ↓ JSON Response
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND VUE.JS                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  ArduinoConfig.js - fetchDashboardData()                    │   │
│  │  ├─ GET /api/dashboard                                       │   │
│  │  ├─ Recibe: { battery: 85, ... }                            │   │
│  │  └─ Retorna: dashboard object                                │   │
│  └────────────────────────┬──────────────────────────────────────┘   │
│                           │                                         │
│  ┌────────────────────────┴───────────────────────────────────┐     │
│  │  DeviceDashboard.vue - loadDashboardFromApi()             │     │
│  │  ├─ Recibe dashboard con battery                           │     │
│  │  ├─ Actualiza: devices[0].battery = 85                     │     │
│  │  └─ Propaga a componentes hijos                            │     │
│  └────────────────────────┬───────────────────────────────────┘     │
│                           │                                         │
│         ┌─────────────────┼──────────────────┐                      │
│         │                 │                  │                      │
│         ↓                 ↓                  ↓                      │
│  ┌────────────────┐ ┌──────────────┐ ┌──────────────┐              │
│  │  DeviceCard    │ │    Dashboard │ │BatteryIndic  │              │
│  │   - Recibe     │ │   - Recibe   │ │   - Props:   │              │
│  │   battery: 85  │ │ batteryLevel │ │   level: 85  │              │
│  │   - Calcula    │ │   - Muestra  │ │   - Renderiza│              │
│  │   computed     │ │   en card    │ │   - Colores  │              │
│  │   - Renderiza  │ │   info       │ │   - SVG Icon │              │
│  │   BatteryInd   │ │   section    │ │              │              │
│  └────────────────┘ └──────────────┘ └──────────────┘              │
│         │                 │                  │                      │
│         ↓                 ↓                  ↓                      │
│    ┌─────────────────────────────────────────────┐                 │
│    │     UI VISUAL - BATTERY INDICATOR           │                 │
│    │                                             │                 │
│    │  Nivel 85%  → 🟢 [████████░░] 85%         │                 │
│    │  Nivel 50%  → 🟡 [█████░░░░░] 50%         │                 │
│    │  Nivel 25%  → 🟠 [██░░░░░░░░] 25%         │                 │
│    │  Nivel 5%   → 🔴 [░░░░░░░░░░] 5%          │                 │
│    └─────────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Estructura de Componentes

```
App.vue
│
├── DeviceDashboard.vue (Principal)
│   ├── Recibe: dashboard data (incluyendo battery)
│   ├── Computed: batteryLevel
│   ├── Renderiza: BatteryIndicator (en info-card)
│   │
│   └── DeviceList.vue (Sub-vista)
│       └── DeviceCard.vue (Tarjeta de dispositivo)
│           ├── Props: device (con battery)
│           ├── Computed: batteryLevel
│           └── Renderiza: BatteryIndicator (pequeño)
│
└── BatteryIndicator.vue (Componente Reutilizable)
    ├── Props:
    │   ├── level: 0-100
    │   ├── size: 'small'|'medium'|'large'
    │   └── showText: boolean
    ├── Computed:
    │   ├── batteryLevel (validado 0-100)
    │   ├── batteryFillWidth (ancho del SVG)
    │   └── batteryClass (color según nivel)
    └── Renderiza: SVG + Texto
```

## Estados de Color y Rango

```
┌─────────────────────────────────────────────────────────┐
│           BATTERY LEVEL INDICATORS                      │
├──────────────────┬──────────────┬──────────────────────┤
│ Rango            │ Color        │ Estado               │
├──────────────────┼──────────────┼──────────────────────┤
│ 61 - 100%        │ 🟢 Verde     │ Batería Normal       │
│ 31 - 60%         │ 🟡 Amarillo  │ Batería Media        │
│ 11 - 30%         │ 🟠 Naranja   │ Batería Baja         │
│ 0 - 10%          │ 🔴 Rojo      │ Batería Crítica      │
└──────────────────┴──────────────┴──────────────────────┘
```

## Ciclo de Actualización

```
┌─────────────────────────────────────────────────────┐
│ CICLO DE ACTUALIZACIÓN (cada 2 segundos)           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. startSensorUpdates() lanza setInterval(2000)   │
│     │                                              │
│     ├─→ updateSensorData()                         │
│         │                                          │
│         ├─→ loadDashboardFromApi()                 │
│             │                                      │
│             ├─→ fetchDashboardData()               │
│                 │                                  │
│                 ├─→ GET /api/dashboard             │
│                     │                              │
│                     └─→ { battery: 85, ... }       │
│                         │                          │
│             ├─→ devices.value[0] = {               │
│                 battery: 85,                       │
│                 bateria: 85,  // compatibility      │
│                 ...                                │
│             }                                      │
│             │                                      │
│  2. Vue Reactivity                                 │
│     │                                              │
│     ├─→ Computed: batteryLevel actualizado         │
│         │                                          │
│         └─→ BatteryIndicator renderiza con nuevo  │
│             nivel (smoothly con transición CSS)    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Base de Datos - Almacenamiento

```
MongoDB Collection: sensor_readings

{
  "_id": ObjectId(...),
  "arduino_id": "esp8266_1",
  "timestamp": 1234567890,
  "mediciones": {
    "ph": 7.2,
    "temperatura": 22.5,
    "conductividad": 650
  },
  "bateria": 85,              ← Campo de batería
  "created_at": ISODate(...),
  "updated_at": ISODate(...)
}
```

## API Request/Response

### Request
```bash
GET /api/dashboard
```

### Response (200 OK)
```json
{
  "ph": {
    "value": 7.2,
    "min": 6.0,
    "max": 8.5,
    "safeMax": 8.0,
    "lastUpdated": "2026-05-18T10:30:45Z",
    "status": "stable"
  },
  "temperature": { ... },
  "conductivity": { ... },
  "metadata": {
    "systemStatus": "operational",
    "arduinoConnected": true,
    "lastSync": "2026-05-18T10:30:45Z",
    "uptime": 3600,
    "activeSensors": 3
  },
  "battery": 85              ← NUEVO CAMPO
}
```

## Modo Oscuro (Dark Theme)

```
HTML THEME SELECTOR
│
├─ html[data-theme='light']
│  ├─ .battery-full { color: #4ade80 }    (Verde)
│  ├─ .battery-medium { color: #eab308 }  (Amarillo)
│  ├─ .battery-low { color: #f97316 }     (Naranja)
│  └─ .battery-critical { color: #ef4444 } (Rojo)
│
└─ html[data-theme='dark']
   ├─ .battery-full { color: #86efac }      (Verde claro)
   ├─ .battery-medium { color: #facc15 }    (Amarillo claro)
   ├─ .battery-low { color: #fb923c }       (Naranja claro)
   └─ .battery-critical { color: #fca5a5 }  (Rojo claro)
```

## Archivos Involucrados

```
Frontend:
├── src/components/
│   ├── BatteryIndicator.vue         (✨ NUEVO)
│   ├── DeviceCard.vue               (📝 MODIFICADO)
│   └── DeviceDashboard.vue          (📝 MODIFICADO)
│
├── src/services/
│   └── ArduinoConfig.js             (📝 MODIFICADO)
│
└── Documentation:
    ├── BATTERY_INDICATOR_IMPLEMENTATION.md  (📝 NUEVO)
    └── BATTERY_INDICATOR_QUICK_START.md     (📝 NUEVO)

Backend:
└── backend_fastapi/
    └── main.py                      (📝 MODIFICADO)
        ├── class DashboardResponse (línea 289)
        ├── /api/dashboard endpoint (línea 562, 977)
        └── battery field default=100
```
