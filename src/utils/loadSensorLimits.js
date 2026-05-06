/**
 * Carga límites de sensores desde localStorage
 * Devuelve los límites o null si no hay guardados
 */
export const loadSensorLimitsFromStorage = () => {
  try {
    const saved = localStorage.getItem('sensorLimits')
    if (saved) {
      const parsed = JSON.parse(saved)
      console.log('[LoadLimits] Límites cargados desde localStorage:', parsed)
      return parsed
    }
  } catch (e) {
    console.error('[LoadLimits] Error al cargar desde localStorage:', e)
  }
  return null
}

/**
 * Fuerza sincronización desde localStorage
 */
export const syncSensorLimitsFromStorage = (SENSOR_LIMITS) => {
  const limits = loadSensorLimitsFromStorage()
  if (limits) {
    SENSOR_LIMITS.value = JSON.parse(JSON.stringify(limits))
    console.log('[Sync] SENSOR_LIMITS actualizado desde localStorage:', SENSOR_LIMITS.value)
    return true
  }
  return false
}
