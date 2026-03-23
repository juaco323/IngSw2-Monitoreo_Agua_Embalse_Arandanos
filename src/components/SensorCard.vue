<template>
  <div class="sensor-card">
    <div class="sensor-header">
      <h3 class="sensor-title">{{ sensorName }}</h3>
      <span class="sensor-status" :class="`status-${statusClass}`">
        {{ statusText }}
      </span>
    </div>
    
    <div class="gauge-wrapper">
      <LinearGauge
        :sensor-name="sensorName"
        :value="value"
        :min-value="min"
        :max-value="max"
        :unit="unit"
        :width="450"
        :height="150"
        :major-ticks="majorTicks"
        :minor-ticks="5"
        :highlights="gaugeHighlights"
      />
    </div>

    <div class="sensor-info">
      <div class="info-row">
        <span class="info-label">Rango seguro:</span>
        <span class="info-value">{{ min.toFixed(1) }} - {{ safeMax.toFixed(1) }} {{ unit }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Última actualización:</span>
        <span class="info-value">{{ lastUpdated }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LinearGauge from './LinearGauge.vue'

const props = defineProps({
  sensorName: {
    type: String,
    required: true
  },
  sensorType: {
    type: String,
    default: 'temperature',
    validator: (value) => ['temperature', 'ph', 'conductivity'].includes(value)
  },
  value: {
    type: Number,
    required: true
  },
  min: {
    type: Number,
    required: true
  },
  max: {
    type: Number,
    required: true
  },
  safeMax: {
    type: Number,
    required: true
  },
  unit: {
    type: String,
    required: true
  },
  lastUpdated: {
    type: String,
    default: 'ahora'
  }
})

const percentage = computed(() => {
  const clipped = Math.max(props.min, Math.min(props.max, props.value))
  return ((clipped - props.min) / (props.max - props.min)) * 100
})

const statusClass = computed(() => {
  const pct = percentage.value
  if (pct < 15 || pct > 85) return 'danger'
  if (pct < 35 || pct > 65) return 'warning'
  return 'safe'
})

const statusText = computed(() => {
  const pct = percentage.value
  if (pct < 15 || pct > 85) return 'Peligroso'
  if (pct < 35 || pct > 65) return 'Advertencia'
  return 'Estable'
})

const majorTicks = computed(() => {
  const range = props.max - props.min
  const step = range / 10
  const ticks = []
  for (let i = 0; i <= 10; i++) {
    ticks.push(parseFloat((props.min + i * step).toFixed(2)))
  }
  return ticks
})

const gaugeHighlights = computed(() => {
  // Para temperatura: azul en extremo frío, para pH y conductividad: rojo en ambos extremos
  if (props.sensorType === 'temperature') {
    // Temperatura: Azul (crítico bajo) | Amarillo (advertencia) | Verde (SAFE) | Amarillo (advertencia) | Rojo (crítico alto)
    const seg1 = props.min + (props.safeMax - props.min) * 0.15        // Límite azul-amarillo
    const seg2 = props.min + (props.safeMax - props.min) * 0.35        // Límite amarillo-verde
    const safeEnd = props.safeMax                                      // Fin de la zona segura
    const seg3 = props.safeMax + (props.max - props.safeMax) * 0.5     // Límite amarillo-rojo

    return [
      { from: props.min, to: seg1, color: 'rgba(0, 0, 255, 0.25)' },          // Azul (Frío - crítico)
      { from: seg1, to: seg2, color: 'rgba(255, 193, 7, 0.25)' },             // Amarillo (Advertencia baja)
      { from: seg2, to: safeEnd, color: 'rgba(76, 175, 80, 0.25)' },          // Verde (SAFE - rango seguro)
      { from: safeEnd, to: seg3, color: 'rgba(255, 193, 7, 0.25)' },          // Amarillo (Advertencia alta)
      { from: seg3, to: props.max, color: 'rgba(255, 0, 0, 0.25)' }           // Rojo (Calor - crítico)
    ]
  } else {
    // pH y Conductividad: Rojo (crítico bajo) | Amarillo (advertencia) | Verde (SAFE) | Amarillo (advertencia) | Rojo (crítico alto)
    const seg1 = props.min + (props.safeMax - props.min) * 0.15        // Límite rojo-amarillo
    const seg2 = props.min + (props.safeMax - props.min) * 0.35        // Límite amarillo-verde
    const safeEnd = props.safeMax                                      // Fin de la zona segura
    const seg3 = props.safeMax + (props.max - props.safeMax) * 0.5     // Límite amarillo-rojo

    return [
      { from: props.min, to: seg1, color: 'rgba(255, 0, 0, 0.25)' },          // Rojo (Bajo - crítico)
      { from: seg1, to: seg2, color: 'rgba(255, 193, 7, 0.25)' },             // Amarillo (Advertencia baja)
      { from: seg2, to: safeEnd, color: 'rgba(76, 175, 80, 0.25)' },          // Verde (SAFE - rango seguro)
      { from: safeEnd, to: seg3, color: 'rgba(255, 193, 7, 0.25)' },          // Amarillo (Advertencia alta)
      { from: seg3, to: props.max, color: 'rgba(255, 0, 0, 0.25)' }           // Rojo (Alto - crítico)
    ]
  }
})
</script>

<style scoped>
.sensor-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
}

.sensor-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #d0d0d0;
}

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.sensor-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  letter-spacing: 0.3px;
}

.sensor-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.status-safe {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-warning {
  background-color: #fff3e0;
  color: #e65100;
}

.status-danger {
  background-color: #ffebee;
  color: #c62828;
}

.gauge-wrapper {
  display: flex;
  justify-content: center;
  margin: 24px 0;
}

.sensor-info {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #888;
  font-weight: 500;
}

.info-value {
  color: #444;
  font-weight: 600;
}

@media (max-width: 768px) {
  .sensor-card {
    padding: 16px;
  }

  .sensor-title {
    font-size: 16px;
  }

  .sensor-header {
    margin-bottom: 16px;
  }
}
</style>
