# Guía de Pruebas - Indicador de Batería

## Pruebas Unitarias Recomendadas

### 1. Prueba de Renderización del Componente BatteryIndicator

```javascript
// test-battery-indicator.spec.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BatteryIndicator from './BatteryIndicator.vue'

describe('BatteryIndicator Component', () => {
  
  it('debe renderizar el indicador de batería', () => {
    const wrapper = mount(BatteryIndicator, {
      props: {
        level: 85
      }
    })
    expect(wrapper.find('.battery-indicator').exists()).toBe(true)
  })

  it('debe mostrar el porcentaje correcto', () => {
    const wrapper = mount(BatteryIndicator, {
      props: {
        level: 75
      }
    })
    expect(wrapper.find('.battery-text').text()).toBe('75%')
  })

  it('debe tener clase battery-full para nivel > 60%', () => {
    const wrapper = mount(BatteryIndicator, {
      props: {
        level: 80
      }
    })
    expect(wrapper.find('svg').classes()).toContain('battery-full')
  })

  it('debe tener clase battery-medium para nivel 31-60%', () => {
    const wrapper = mount(BatteryIndicator, {
      props: {
        level: 45
      }
    })
    expect(wrapper.find('svg').classes()).toContain('battery-medium')
  })

  it('debe tener clase battery-low para nivel 11-30%', () => {
    const wrapper = mount(BatteryIndicator, {
      props: {
        level: 20
      }
    })
    expect(wrapper.find('svg').classes()).toContain('battery-low')
  })

  it('debe tener clase battery-critical para nivel <= 10%', () => {
    const wrapper = mount(BatteryIndicator, {
      props: {
        level: 5
      }
    })
    expect(wrapper.find('svg').classes()).toContain('battery-critical')
  })

  it('debe limitar nivel a 0-100', () => {
    const wrapper = mount(BatteryIndicator, {
      props: {
        level: 150
      }
    })
    expect(wrapper.find('.battery-text').text()).toBe('100%')
  })
})
```

## Pruebas de Integración Manual

### Test 1: Visualización en Tarjetas de Dispositivos

**Pasos:**
1. Inicia la aplicación: `npm run dev`
2. Navega a la vista de dispositivos
3. Cada tarjeta debe mostrar un indicador de batería pequeño
4. El ícono debe cambiar de color según el nivel

**Resultado esperado:**
- ✅ Indicador visible en cada tarjeta
- ✅ Color correcto según nivel (verde/amarillo/naranja/rojo)
- ✅ Porcentaje visible

---

### Test 2: Visualización en Dashboard

**Pasos:**
1. Haz clic en un dispositivo para abrir el dashboard
2. Observa la sección "Información del Sistema"
3. Debe haber una fila "Estado de Batería"
4. El indicador debe ser más grande que en las tarjetas

**Resultado esperado:**
- ✅ Fila de batería visible
- ✅ Ícono grande con porcentaje
- ✅ Color apropiado

---

### Test 3: Actualización en Tiempo Real

**Pasos:**
1. Abre el dashboard de un dispositivo
2. Observa la batería durante 30 segundos
3. Los valores deben cambiar cada 2 segundos
4. Los colores deben cambiar dinámicamente

**Resultado esperado:**
- ✅ Valores cambian regularmente
- ✅ Transición suave de colores
- ✅ Sin parpadeos ni saltos abruptos

---

### Test 4: Modo Oscuro

**Pasos:**
1. Abre el indicador de tema (ThemeToggleButton)
2. Cambia a modo oscuro
3. Verifica que los colores son visibles
4. Vuelve a modo claro

**Resultado esperado:**
- ✅ Colores visibles en ambos modos
- ✅ Contraste adecuado
- ✅ Transición suave

---

### Test 5: Datos del Arduino Real

**Pasos:**
1. Configura Arduino para enviar batería
2. POST a `/api/sensors/readings`:
   ```json
   {
     "ph": 7.2,
     "temperature": 22.5,
     "conductivity": 650,
     "bateria": 65
   }
   ```
3. Observa el indicador en dashboard
4. Verifica que muestra 65%

**Resultado esperado:**
- ✅ Batería muestra valor enviado (65%)
- ✅ Color amarillo (nivel medio)
- ✅ Se actualiza correctamente

---

### Test 6: Fallback a 100%

**Pasos:**
1. POST sin campo `bateria`:
   ```json
   {
     "ph": 7.2,
     "temperature": 22.5,
     "conductivity": 650
   }
   ```
2. Verifica el indicador

**Resultado esperado:**
- ✅ Muestra 100% por defecto
- ✅ Color verde
- ✅ Sin errores en consola

---

### Test 7: Valores Extremos

**Pasos:**
1. Test con bateria: 0
   - Debe mostrar 🔴 Rojo
2. Test con bateria: 100
   - Debe mostrar 🟢 Verde
3. Test con bateria: -50 (inválido)
   - Debe limitarse a 0 (🔴 Rojo)
4. Test con bateria: 150 (inválido)
   - Debe limitarse a 100 (🟢 Verde)

**Resultado esperado:**
- ✅ Todos los valores se manejan correctamente
- ✅ Se limitan a rango 0-100
- ✅ Colores apropiados

---

### Test 8: Responsividad

**Pasos:**
1. Abre en desktop (1920x1080)
   - Verifica tamaño y visibilidad
2. Abre en tablet (768x1024)
   - Verifica escala y alineación
3. Abre en móvil (375x667)
   - Verifica que cabe en la tarjeta

**Resultado esperado:**
- ✅ Se ajusta correctamente en todos los tamaños
- ✅ Legible en dispositivos móviles
- ✅ No rompe el layout

---

## Pruebas de API

### Test API del Backend

```bash
# Test 1: Obtener dashboard con batería
curl -X GET http://localhost:8000/api/dashboard \
  -H "Content-Type: application/json"

# Respuesta esperada:
# {
#   "ph": {...},
#   "temperature": {...},
#   "conductivity": {...},
#   "metadata": {...},
#   "battery": 85
# }

# Test 2: Enviar lectura con batería
curl -X POST http://localhost:8000/api/sensors/readings \
  -H "Content-Type: application/json" \
  -d '{
    "ph": 7.2,
    "temperature": 22.5,
    "conductivity": 650,
    "bateria": 78
  }'

# Test 3: Verificar en MongoDB
# En MongoDB Compass:
# db.sensor_readings.findOne()
# {
#   "_id": ObjectId(...),
#   "bateria": 78,
#   ...
# }
```

---

## Pruebas de Consola JavaScript

```javascript
// Test 1: Verificar que BatteryIndicator se importó
console.log('BatteryIndicator imported:', typeof BatteryIndicator !== 'undefined')
// Resultado esperado: true

// Test 2: Verificar que el device tiene battery
console.log('Device battery:', selectedDevice.value.battery)
// Resultado esperado: número entre 0-100

// Test 3: Verificar computed batteryLevel
console.log('Battery Level computed:', batteryLevel.value)
// Resultado esperado: número entre 0-100

// Test 4: Simular cambio de batería
devices.value[0].battery = 50
// Verifica que el indicador cambia a amarillo en tiempo real

// Test 5: Verificar datos del API
fetch('/api/dashboard')
  .then(r => r.json())
  .then(d => console.log('Dashboard battery:', d.battery))
// Resultado esperado: número entre 0-100
```

---

## Pruebas de Performance

### Test: Renderización con Múltiples Indicadores

```javascript
// En DeviceList.vue cuando hay muchos dispositivos
// Medir tiempo de renderización

console.time('render-device-list')
// ... renderizar lista de 50 dispositivos
console.timeEnd('render-device-list')

// Resultado esperado: < 200ms
```

---

## Checklist de Validación

- [ ] BatteryIndicator.vue creado correctamente
- [ ] DeviceCard.vue importa y usa BatteryIndicator
- [ ] DeviceDashboard.vue importa y usa BatteryIndicator
- [ ] Backend retorna `battery` en `/api/dashboard`
- [ ] Indicador visible en tarjetas
- [ ] Indicador visible en dashboard
- [ ] Colores cambian según nivel
- [ ] Actualización cada 2 segundos funciona
- [ ] Modo oscuro funciona
- [ ] Responsive en móvil/tablet/desktop
- [ ] No hay errores en consola
- [ ] Datos de Arduino real se reciben
- [ ] Fallback a 100% cuando no hay datos
- [ ] Performance es bueno (sin lag)

---

## Logs Esperados

### Console Log (cuando inicia):
```
✓ BatteryIndicator component loaded
✓ DeviceDashboard mounted
✓ Starting sensor updates every 2000ms
✓ [DEBUG] Respuesta de /api/dashboard: {...battery: 85...}
```

### Backend Logs:
```
INFO - Dashboard actualizado desde MongoDB. Arduino conectado: True
INFO - Battery level: 85% from sensor reading
```

---

## Troubleshooting

### Problema: Indicador no aparece
- [ ] Verificar que BatteryIndicator.vue está en `src/components/`
- [ ] Verificar import en DeviceCard.vue
- [ ] Verificar que device tiene propiedad `battery` o `bateria`
- [ ] Abrir DevTools > Console (F12) y buscar errores

### Problema: Color equivocado
- [ ] Verificar que el nivel está en rango 0-100
- [ ] Verificar que el batteryClass computed es correcto
- [ ] Limpiar cache del navegador (Ctrl+Shift+Del)
- [ ] Verificar tema (light/dark)

### Problema: No se actualiza
- [ ] Verificar que `updateInterval` está corriendo
- [ ] Verificar que `/api/dashboard` retorna `battery`
- [ ] Verificar que `devices.value[0].battery` se actualiza
- [ ] Abrir Network tab (F12) y verificar requests

---

## Scripts de Prueba

```bash
# Correr pruebas unitarias (si está configurado)
npm run test

# Correr linter para verificar sintaxis
npm run lint

# Build para verificar que compila
npm run build

# Dev server para pruebas manuales
npm run dev
```

---

## Conclusión

Si todas las pruebas pasan, el indicador de batería está funcionando correctamente y listo para producción.
