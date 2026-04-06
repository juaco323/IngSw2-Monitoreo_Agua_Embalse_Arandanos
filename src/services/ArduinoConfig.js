/**
 * Configuración de conexión con Arduino/ESP8266
 * Este archivo contiene funciones para conectar el dashboard con la API FastAPI/MongoDB
 * 
 * Flujo: ESP8266 → API FastAPI → MongoDB → Frontend Vue.js
 */

// ============================================================================
// CONFIGURACIÓN
// ============================================================================

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
const RAW_DATA_MODE = String(import.meta.env.VITE_DATA_MODE ?? 'real').trim().toLowerCase()
export const DATA_MODE = RAW_DATA_MODE === 'simulated' ? 'simulated' : 'real'
export const IS_SIMULATED_MODE = DATA_MODE === 'simulated'
export const IS_REAL_MODE = !IS_SIMULATED_MODE
const POLL_INTERVAL = 2000 // Polling cada 2 segundos

const SIM_LIMITS = {
  ph: { min: 6.0, max: 8.5, safeMax: 8.0 },
  temperature: { min: 5, max: 35, safeMax: 28 },
  conductivity: { min: 100, max: 2000, safeMax: 1500 }
}

const SIMULATION_START_TIME = Date.now()

const clamp = (value, min, max) => Math.max(min, Math.min(max, value))

const getWave = (timestampMs, periodSeconds, phase = 0) => {
  return Math.sin((timestampMs / 1000) * (2 * Math.PI / periodSeconds) + phase)
}

const withNoise = (value, amount) => value + (Math.random() - 0.5) * 2 * amount

const getSensorStatus = (value, min, max) => {
  if (value < min || value > max) return 'critical'
  const margin = (max - min) * 0.15
  if (value < min + margin || value > max - margin) return 'warning'
  return 'stable'
}

const generateSyntheticReading = (timestampMs = Date.now()) => {
  const phBase = 7.1 + getWave(timestampMs, 180, 0.3) * 0.45 + getWave(timestampMs, 47, 1.1) * 0.08
  const tempBase = 22 + getWave(timestampMs, 240, 1.6) * 3.2 + getWave(timestampMs, 31, 0.4) * 0.25
  const conductivityBase = 900 + getWave(timestampMs, 210, 2.2) * 230 + getWave(timestampMs, 29, 0.9) * 22

  return {
    ph: Number(clamp(withNoise(phBase, 0.03), 5.8, 8.7).toFixed(2)),
    temperature: Number(clamp(withNoise(tempBase, 0.12), 4, 36).toFixed(2)),
    conductivity: Number(clamp(withNoise(conductivityBase, 8), 100, 2000).toFixed(2)),
    timestamp: timestampMs
  }
}

const buildSimulatedDashboard = () => {
  const reading = generateSyntheticReading(Date.now())
  const nowIso = new Date(reading.timestamp).toISOString()

  return {
    ph: {
      value: reading.ph,
      min: SIM_LIMITS.ph.min,
      max: SIM_LIMITS.ph.max,
      safeMax: SIM_LIMITS.ph.safeMax,
      lastUpdated: nowIso,
      status: getSensorStatus(reading.ph, SIM_LIMITS.ph.min, SIM_LIMITS.ph.max)
    },
    temperature: {
      value: reading.temperature,
      min: SIM_LIMITS.temperature.min,
      max: SIM_LIMITS.temperature.max,
      safeMax: SIM_LIMITS.temperature.safeMax,
      lastUpdated: nowIso,
      status: getSensorStatus(reading.temperature, SIM_LIMITS.temperature.min, SIM_LIMITS.temperature.max)
    },
    conductivity: {
      value: reading.conductivity,
      min: SIM_LIMITS.conductivity.min,
      max: SIM_LIMITS.conductivity.max,
      safeMax: SIM_LIMITS.conductivity.safeMax,
      lastUpdated: nowIso,
      status: getSensorStatus(reading.conductivity, SIM_LIMITS.conductivity.min, SIM_LIMITS.conductivity.max)
    },
    metadata: {
      systemStatus: 'operational',
      arduinoConnected: true,
      lastSync: nowIso,
      uptime: Math.floor((Date.now() - SIMULATION_START_TIME) / 1000),
      activeSensors: 3
    }
  }
}

// ============================================================================
// OPCIÓN 1: Fetch API (Polling) - Obtener datos del dashboard desde MongoDB
// ============================================================================

/**
 * Obtener datos del dashboard desde la API FastAPI
 * Estos datos son actualizados por el ESP8266 en tiempo real
 */
export const fetchDashboardData = async (apiUrl = `${API_BASE_URL}/api/dashboard`) => {
  if (IS_SIMULATED_MODE) {
    return buildSimulatedDashboard()
  }

  try {
    console.log('[API] Obteniendo datos del dashboard desde:', apiUrl)
    const response = await fetch(apiUrl)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    console.log('[API] Datos recibidos:', data)
    return data
  } catch (error) {
    console.error('[API] Error obteniendo datos del dashboard:', error)
    return null
  }
}

/**
 * Obtener la última lectura de sensores desde MongoDB
 */
export const fetchLatestSensorReading = async (apiUrl = `${API_BASE_URL}/api/sensors/latest`) => {
  if (IS_SIMULATED_MODE) {
    return generateSyntheticReading(Date.now())
  }

  try {
    const response = await fetch(apiUrl)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    return data
  } catch (error) {
    console.error('[API] Error obteniendo última lectura:', error)
    return null
  }
}

/**
 * Obtener historial de lecturas de sensores desde MongoDB
 */
export const fetchSensorHistory = async (limit = 100) => {
  if (IS_SIMULATED_MODE) {
    const maxRows = Math.max(1, Number(limit) || 100)
    const now = Date.now()

    return Array.from({ length: maxRows }, (_, index) => {
      const timestamp = now - index * 60 * 1000
      return generateSyntheticReading(timestamp)
    })
  }

  try {
    const apiUrl = `${API_BASE_URL}/api/sensors/history?limit=${limit}`
    const response = await fetch(apiUrl)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    return data
  } catch (error) {
    console.error('[API] Error obteniendo historial:', error)
    return []
  }
}

/**
 * Iniciar polling automático de datos del dashboard
 * Usa callback para actualizar datos en tiempo real
 */
export const startDashboardPolling = (callback, interval = POLL_INTERVAL) => {
  console.log('[API] Iniciando polling cada', interval, 'ms')
  
  // Primera lectura inmediata
  fetchDashboardData().then(data => {
    if (data) callback(data)
  })
  
  // Polling periódico
  const intervalId = setInterval(() => {
    fetchDashboardData().then(data => {
      if (data) callback(data)
    })
  }, interval)
  
  // Retornar ID para detener el polling
  return intervalId
}

/**
 * Detener polling automático
 */
export const stopDashboardPolling = (intervalId) => {
  if (intervalId) {
    clearInterval(intervalId)
    console.log('[API] Polling detenido')
  }
}

// Uso en App.vue:
// import { startDashboardPolling, stopDashboardPolling, fetchDashboardData } from '@/services/ArduinoConfig'
//
// const updateSensorData = (dashboardData) => {
//   sensors.value = {
//     ph: dashboardData.ph,
//     temperature: dashboardData.temperature,
//     conductivity: dashboardData.conductivity
//   }
//   lastSync.value = dashboardData.metadata.lastSync
// }
//
// let pollingId
// 
// onMounted(() => {
//   pollingId = startDashboardPolling(updateSensorData)
// })
//
// onUnmounted(() => {
//   stopDashboardPolling(pollingId)
// })

export default {
  DATA_MODE,
  IS_SIMULATED_MODE,
  IS_REAL_MODE,
  fetchDashboardData,
  fetchLatestSensorReading,
  fetchSensorHistory,
  startDashboardPolling,
  stopDashboardPolling
}

