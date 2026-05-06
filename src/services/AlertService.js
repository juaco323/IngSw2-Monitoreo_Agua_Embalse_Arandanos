/**
 * Servicio para enviar alertas al backend cuando sensores estén fuera de rango
 */

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
const DATA_MODE = String(import.meta.env.VITE_DATA_MODE ?? 'real').trim().toLowerCase()
const IS_SIMULATED_MODE = DATA_MODE === 'simulated'
const API_URL = `${API_BASE_URL}/api/alerts`

export const sendAlertToBackend = async (deviceName, sensor, value, measurement, min, max) => {
  if (IS_SIMULATED_MODE) {
    return null
  }

  try {
    const payload = {
      embalse: deviceName,
      nombreDispositivo: deviceName,
      sensor: sensor,
      medicion: measurement,
      valor: value,
      minimo: min,
      maximo: max
    }

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      console.error(`Error enviando alerta: ${response.status}`)
      return null
    }

    const data = await response.json()
    console.log('Alerta enviada al backend:', data)
    return data
  } catch (error) {
    console.error('Error en sendAlertToBackend:', error)
    return null
  }
}

export const checkAndSendAlerts = async (device, sensorLimits) => {
  if (IS_SIMULATED_MODE) {
    return
  }

  const ph = device.sensors.ph
  const temperature = device.sensors.temperature
  const conductivity = device.sensors.conductivity

  // Función auxiliar para determinar el nivel de riesgo
  const getAlertLevel = (value, limits) => {
    // Nueva estructura soportada: { base_min, base_max, safe_min, safe_max, danger_ranges: [{min,max}], warning_ranges: [{min,max}] }
    if (!limits) return 'danger'

    // Safe direct check
    if (typeof limits.safe_min === 'number' && typeof limits.safe_max === 'number') {
      if (value >= limits.safe_min && value <= limits.safe_max) return 'safe'
    }

    // Warnings (array of ranges)
    if (Array.isArray(limits.warning_ranges)) {
      for (const r of limits.warning_ranges) {
        if (typeof r.min === 'number' && typeof r.max === 'number' && value >= r.min && value <= r.max) return 'warning'
      }
    }

    // Dangers (array of ranges)
    if (Array.isArray(limits.danger_ranges)) {
      for (const r of limits.danger_ranges) {
        if (typeof r.min === 'number' && typeof r.max === 'number' && value >= r.min && value <= r.max) return 'danger'
      }
    }

    // Backwards compatibility: single-range fields
    const { danger_min, danger_max, warning_min, warning_max } = limits
    if (typeof warning_min === 'number' && typeof warning_max === 'number') {
      if (value >= warning_min && value <= warning_max) return 'warning'
    }
    if (typeof danger_min === 'number' && typeof danger_max === 'number') {
      if (value >= danger_min && value <= danger_max) return 'danger'
    }

    // Fallback: outside base bounds => danger, otherwise warning
    if (typeof limits.base_min === 'number' && value < limits.base_min) return 'danger'
    if (typeof limits.base_max === 'number' && value > limits.base_max) return 'danger'

    return 'warning'
  }

  // Verificar pH
  const phLevel = getAlertLevel(ph, sensorLimits.ph)
  if (phLevel !== 'safe') {
    await sendAlertToBackend(
      device.name,
      'pH',
      ph,
      `${ph.toFixed(2)} pH (${phLevel})`,
      sensorLimits.ph.safe_min,
      sensorLimits.ph.safe_max
    )
  }

  // Verificar Temperatura
  const tempLevel = getAlertLevel(temperature, sensorLimits.temperature)
  if (tempLevel !== 'safe') {
    await sendAlertToBackend(
      device.name,
      'Temperatura',
      temperature,
      `${temperature.toFixed(2)} °C (${tempLevel})`,
      sensorLimits.temperature.safe_min,
      sensorLimits.temperature.safe_max
    )
  }

  // Verificar Conductividad
  const condLevel = getAlertLevel(conductivity, sensorLimits.conductivity)
  if (condLevel !== 'safe') {
    await sendAlertToBackend(
      device.name,
      'Conductividad Eléctrica',
      conductivity,
      `${conductivity.toFixed(0)} µS/cm (${condLevel})`,
      sensorLimits.conductivity.safe_min,
      sensorLimits.conductivity.safe_max
    )
  }
}

export default {
  sendAlertToBackend,
  checkAndSendAlerts
}
