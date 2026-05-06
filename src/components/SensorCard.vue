<template>
  <div class="sensor-card" :class="`card-${statusClass}`">
    <div class="sensor-header">
      <h3 class="sensor-title">{{ sensorName }}</h3>
      <span class="sensor-status" :class="`status-${statusClass}`">
        {{ statusText }}
      </span>
    </div>

    <div class="value-panel" :class="`value-${statusClass}`">
      <div class="value-number">{{ formattedValue }}</div>
      <div class="value-unit">{{ unit }}</div>
    </div>

    <div class="sensor-info">
      <div class="info-row">
        <span class="info-label">Rango seguro:</span>
        <span class="info-value">{{ rangeText.safe }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Rango advertencia:</span>
        <span class="info-value">{{ rangeText.warning }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Rango peligro:</span>
        <span class="info-value">{{ rangeText.danger }}</span>
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

const formattedValue = computed(() => {
  const num = Number(props.value)
  if (!Number.isFinite(num)) return '--'
  return num.toFixed(2)
})

const formatRangeNumber = (num) => {
  if (!Number.isFinite(num)) return '--'
  return Number(num).toFixed(1)
}

const rangeText = computed(() => {
  const t = normalizedThresholds.value
  return {
    safe: `${formatRangeNumber(t.warningLow)} - ${formatRangeNumber(t.warningHigh)} ${props.unit}`,
    warning: `${formatRangeNumber(t.dangerLow)} - ${formatRangeNumber(t.warningLow)} / ${formatRangeNumber(t.warningHigh)} - ${formatRangeNumber(t.dangerHigh)} ${props.unit}`,
    danger: `${formatRangeNumber(props.min)} - ${formatRangeNumber(t.dangerLow)} / ${formatRangeNumber(t.dangerHigh)} - ${formatRangeNumber(props.max)} ${props.unit}`
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

.card-safe {
  border-color: #6aa84f;
}

.card-warning {
  border-color: #f1c232;
}

.card-danger {
  border-color: #cc0000;
}

.value-panel {
  margin: 18px 0;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 10px;
}

.value-safe {
  background: #2e7d32;
  color: #ffffff;
}

.value-warning {
  background: #f1c232;
  color: #1a1a1a;
}

.value-danger {
  background: #cc0000;
  color: #ffffff;
}

.value-number {
  font-size: 42px;
  font-weight: 800;
  line-height: 1;
}

.value-unit {
  font-size: 18px;
  font-weight: 700;
}

.sensor-info {
  margin-top: 16px;
  padding-top: 12px;
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
