# Guía Rápida - Indicador de Batería

## ¿Dónde Ver el Indicador de Batería?

### 1. **En las Tarjetas de Dispositivos** (Vista de Dispositivos)
- Cuando ves la lista de todos los dispositivos
- El indicador aparece en la esquina superior derecha de cada tarjeta
- Junto a "Conectado" o "Desconectado"
- Muestra un ícono de batería pequeño con el porcentaje

### 2. **En el Dashboard Principal** (Información del Sistema)
- Cuando abres un dispositivo para verlo en detalle
- En la sección "Información del Sistema" (arriba del dashboard)
- Se muestra como "Estado de Batería"
- Incluye un ícono más grande con el porcentaje

## Interpretación de Colores

| Color | Rango | Estado |
|-------|-------|--------|
| 🟢 Verde | > 60% | Batería en buen estado |
| 🟡 Amarillo | 31-60% | Batería media |
| 🟠 Naranja | 11-30% | Batería baja |
| 🔴 Rojo | ≤ 10% | Batería crítica |

## Cómo Funciona

- **Actualización**: El indicador se actualiza automáticamente cada 2 segundos desde el servidor
- **Datos**: Los valores vienen del dispositivo Arduino en tiempo real
- **Simulación**: En modo de prueba, los valores varían entre 20% y 95%
- **Almacenamiento**: Cada lectura de batería se guarda en la base de datos

## Información Técnica

### Datos que Llegan del Arduino

```json
{
  "bateria": 85  // Valor entre 0-100
}
```

### API Endpoint

**GET `/api/dashboard`**

Respuesta incluye:
```json
{
  "ph": { ... },
  "temperature": { ... },
  "conductivity": { ... },
  "metadata": { ... },
  "battery": 85
}
```

## Características Avanzadas

✅ **Responsive**: Se adapta a diferentes tamaños de pantalla
✅ **Modo Oscuro**: Los colores se ajustan automáticamente
✅ **Tooltip**: Pasa el cursor sobre el icono para ver "Batería: XX%"
✅ **Reutilizable**: El componente se puede usar en otras partes de la aplicación

## Próximas Funcionalidades Sugeridas

1. **Alertas de Batería Baja**
   - Notificación cuando la batería está por debajo de 20%
   - Mensaje en Telegram

2. **Gráfico de Descarga**
   - Ver tendencia de consumo de batería
   - Estimar tiempo de duración

3. **Historial de Batería**
   - Datos históricos en la sección de reportes
   - Gráfico de evolución

## Solución de Problemas

### No veo el indicador de batería

1. Verifica que el dispositivo está conectado y enviando datos
2. Recarga la página (F5)
3. Asegúrate que el backend FastAPI está corriendo

### El indicador siempre muestra 100%

1. El Arduino no está enviando datos de batería
2. O los datos llegando no incluyen el campo `bateria`
3. Revisa los logs del backend: `backend_fastapi/app.log`

### Los colores no cambian

1. Verifica que los valores de batería varían (espera a que se actualicen)
2. Comprueba que JavaScript está habilitado
3. Limpia el cache del navegador

## Referencias

- Documentación completa: `BATTERY_INDICATOR_IMPLEMENTATION.md`
- Componente: `src/components/BatteryIndicator.vue`
- Backend: `backend_fastapi/main.py` (línea 289)
