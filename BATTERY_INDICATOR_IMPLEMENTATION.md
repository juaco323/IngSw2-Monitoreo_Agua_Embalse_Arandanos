# Implementación de Indicador de Batería

## Descripción General

Se ha implementado un **indicador visual de batería** para los dispositivos de monitoreo que muestra el estado actual de la carga mediante:
- **Ícono de batería dinámico** que cambia de apariencia según el nivel
- **Códigos de color característicos**:
  - 🟢 **Verde** (>60%): Batería con carga completa
  - 🟡 **Amarillo** (31-60%): Batería con carga media
  - 🟠 **Naranja** (11-30%): Batería baja
  - 🔴 **Rojo** (≤10%): Batería crítica
- **Texto numérico** mostrando el porcentaje exacto

## Cambios Implementados

### 1. Frontend - Nuevo Componente Vue

#### Archivo: `src/components/BatteryIndicator.vue`
- Nuevo componente reutilizable que muestra el indicador de batería
- Props configurables:
  - `level`: Nivel de batería (0-100)
  - `size`: Tamaño del indicador (small, medium, large)
  - `showText`: Mostrar u ocultar el porcentaje
- Incluye ícono SVG animado que se llena según el nivel
- Soporte para modo oscuro automático
- Transiciones suaves al cambiar el nivel

### 2. Frontend - Componente DeviceCard.vue (Tarjeta de Dispositivo)

**Cambios:**
- Importación de `BatteryIndicator.vue`
- Nuevo computed `batteryLevel` que obtiene el nivel del dispositivo
- Nuevo elemento HTML en el header con el indicador de batería
- Estilos CSS para alinear el indicador con el estado de conexión
- Responsive design que se adapta a diferentes tamaños de pantalla

**Ubicación en la UI:**
- Se muestra en la sección del encabezado de cada tarjeta de dispositivo
- Junto al indicador de estado de conexión

### 3. Frontend - Componente DeviceDashboard.vue (Panel Principal)

**Cambios:**
- Importación de `BatteryIndicator.vue`
- Nuevo computed `batteryLevel` que obtiene la batería del dispositivo seleccionado
- Nueva tarjeta de información "Estado de Batería" en la sección de información del sistema
- Actualización de los datos del dispositivo cuando se reciben del API
- Estilos CSS para la sección de batería (light y dark mode)

**Ubicación en la UI:**
- Se muestra en la sección "Información del Sistema" del dashboard
- Entre la información de "Conexión Arduino" y "Rol de Usuario"

### 4. Backend - FastAPI (`backend_fastapi/main.py`)

**Cambios:**

#### Modelo actualizado:
- `class DashboardResponse`: Nuevo campo `battery` (int, 0-100)

#### Endpoints:
- Actualización de `/api/dashboard` para incluir `battery` en la respuesta
- Se incluye en dos casos:
  1. **Datos reales desde MongoDB**: `battery=reading.get("bateria", 100)`
  2. **Datos simulados (fallback)**: `battery=simulated_payload.bateria`

### 5. Frontend - Servicio ArduinoConfig.js

**Cambios:**
- Actualización de `buildSimulatedDashboard()` para generar datos de batería simulada
- Valores de prueba: 20-95% (con variación aleatoria)
- Se incluye en la respuesta del dashboard simulado

### 6. Frontend - Actualización de DeviceDashboard.vue (Data Loading)

**Cambios:**
- Función `loadDashboardFromApi()` actualizada para asignar la batería recibida:
  - `battery: dashboard.battery || 100`
  - `bateria: dashboard.battery || 100` (respaldo de compatibilidad)
- Los datos se actualizan cada 2 segundos

## Características

✅ **Indicador Visual Dinámico**
- Ícono que se llena progresivamente según el nivel de carga
- Cambio de color automático según el rango

✅ **Información Detallada**
- Muestra el porcentaje exacto junto al ícono
- Tooltip al pasar el cursor mostrando "Batería: XX%"

✅ **Soporte Multi-tema**
- Colores optimizados para modo claro y oscuro
- Transiciones suaves

✅ **Información en Dos Lugares**
1. **Tarjeta de Dispositivo**: Indicador pequeño y compacto
2. **Dashboard Principal**: Indicador con más detalle en la sección de información

✅ **Compatibilidad Backward**
- Si no hay datos de batería, usa 100% como default
- Soporta tanto `battery` como `bateria` (compatibilidad con backend Python)

## Archivos Modificados

```
✨ NUEVOS:
- src/components/BatteryIndicator.vue

📝 MODIFICADOS:
- src/components/DeviceCard.vue
- src/components/DeviceDashboard.vue
- src/services/ArduinoConfig.js
- backend_fastapi/main.py
```

## Pruebas Recomendadas

1. **Visualización en Tarjetas**
   - Verificar que el indicador aparece en cada tarjeta de dispositivo
   - Comprobar cambios de color según el nivel simulado

2. **Visualización en Dashboard**
   - Abrir el dashboard de un dispositivo
   - Verificar que la batería se muestra en la sección de información

3. **Actualización en Tiempo Real**
   - Monitorear cambios de batería cada 2 segundos
   - Verificar transiciones suaves de color

4. **Modo Oscuro/Claro**
   - Cambiar entre temas
   - Verificar que los colores son visibles en ambos modos

5. **Datos del Arduino Real** (si está disponible)
   - Verificar que se reciben valores reales de batería
   - Comprobar que el indicador responde correctamente

## Integración con Arduino

El Arduino ya envía datos de batería en la estructura:
```json
{
  "arduino_id": "esp8266_1",
  "timestamp": 1234567890,
  "mediciones": {
    "ph": 7.2,
    "temperatura": 22.5,
    "conductividad": 650
  },
  "bateria": 85
}
```

El backend captura este valor `bateria` y lo expone a través del API como `battery` en el campo de DashboardResponse.

## Notas de Desarrollo

- El componente BatteryIndicator es totalmente reutilizable y puede usarse en otros lugares del dashboard
- Los valores de batería simulados varían entre 20% y 95% para una presentación más realista
- El indicador se actualiza reactivamente cuando cambian los datos del servidor
- Los estilos utilizan variables CSS para facilitar cambios futuros

## Próximas Mejoras Sugeridas

1. Agregar alertas cuando la batería esté por debajo de un umbral crítico (ej: 20%)
2. Mostrar tendencia de descarga en un gráfico
3. Estimar tiempo de vida útil restante basado en el consumo
4. Incluir historial de batería en la sección de datos históricos
