<template>
  <div class="sensor-card">
    <div class="sensor-header">
      <h3 class="sensor-title">{{ sensorName }}</h3>
      <span class="sensor-status" :class="`status-${statusClass}`">
        {{ statusText }}
      </span>
    </div>
    
    <div class="sensor-display" :class="`status-bg-${statusClass}`">
      <div class="sensor-value">
        <span class="value-number">{{ value.toFixed(1) }}</span>
        <span class="value-unit">{{ unit }}</span>
      </div>
    </div>

    <div class="sensor-info">
      <div class="info-row">
        <span class="info-label">Rango verde:</span>
        <span class="info-value">{{ normalizedThresholds.warningLow.toFixed(1) }} - {{ normalizedThresholds.warningHigh.toFixed(1) }} {{ unit }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Zona amarilla:</span>
        <span class="info-value">
          {{ normalizedThresholds.dangerLow.toFixed(1) }} - {{ normalizedThresholds.warningLow.toFixed(1) }}
          / {{ normalizedThresholds.warningHigh.toFixed(1) }} - {{ normalizedThresholds.dangerHigh.toFixed(1) }} {{ unit }}
        </span>
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
  thresholds: {
    type: Object,
    default: null
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

const clamp = (value, min, max) => Math.min(max, Math.max(min, value))

const buildFallbackThresholds = () => {
  const range = props.max - props.min
  return {
    dangerLow: props.min + range * 0.15,
    warningLow: props.min + range * 0.35,
    warningHigh: props.min + range * 0.65,
    dangerHigh: props.min + range * 0.85
  }
}

const normalizedThresholds = computed(() => {
  const fallback = buildFallbackThresholds()

  const values = [
    Number(props.thresholds?.dangerLow ?? fallback.dangerLow),
    Number(props.thresholds?.warningLow ?? fallback.warningLow),
    Number(props.thresholds?.warningHigh ?? fallback.warningHigh),
    Number(props.thresholds?.dangerHigh ?? fallback.dangerHigh)
  ]
    .map((value) => Number.isFinite(value) ? clamp(value, props.min, props.max) : props.min)
    .sort((first, second) => first - second)

  return {
    dangerLow: values[0],
    warningLow: values[1],
    warningHigh: values[2],
    dangerHigh: values[3]
  }
})

const statusClass = computed(() => {
  const currentValue = clamp(props.value, props.min, props.max)
  if (currentValue <= normalizedThresholds.value.dangerLow || currentValue >= normalizedThresholds.value.dangerHigh) return 'danger'
  if (currentValue <= normalizedThresholds.value.warningLow || currentValue >= normalizedThresholds.value.warningHigh) return 'warning'
  return 'safe'
})

const statusText = computed(() => {
  const currentValue = clamp(props.value, props.min, props.max)
  if (currentValue <= normalizedThresholds.value.dangerLow || currentValue >= normalizedThresholds.value.dangerHigh) return 'Peligroso'
  if (currentValue <= normalizedThresholds.value.warningLow || currentValue >= normalizedThresholds.value.warningHigh) return 'Advertencia'
  return 'Estable'
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
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sensor-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #d0d0d0;
}

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
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

/* Sensor Display with Number and Background Color */
.sensor-display {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 140px;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.status-bg-safe {
  background-color: #4caf50;
  background-color: rgba(76, 175, 80, 0.9);
}

.status-bg-warning {
  background-color: #ffc107;
  background-color: rgba(255, 193, 7, 0.9);
}

.status-bg-danger {
  background-color: #f44336;
  background-color: rgba(244, 67, 54, 0.9);
}

.sensor-value {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
}

.value-number {
  font-size: 56px;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.value-unit {
  font-size: 18px;
  font-weight: 500;
  color: #ffffff;
  opacity: 0.95;
}

.sensor-info {
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
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

  .value-number {
    font-size: 40px;
  }

  .value-unit {
    font-size: 14px;
  }

  .sensor-display {
    min-height: 100px;
  }
}

@media (max-width: 480px) {
  .sensor-card {
    padding: 12px;
  }

  .value-number {
    font-size: 32px;
  }

  .value-unit {
    font-size: 12px;
  }

  .sensor-display {
    min-height: 80px;
  }
}
</style>
