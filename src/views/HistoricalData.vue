<template>
  <div class="historical-view">
    <header class="history-header">
      <h1>📊 Datos Históricos</h1>
      <div class="header-controls">
        <button class="logout-btn" @click="handleLogout">Cerrar Sesión</button>
      </div>
    </header>

    <main class="history-content">
      <div class="filters">
        <div class="filter-group">
          <label>Fecha Inicio</label>
          <input v-model="filters.startDate" type="date" />
        </div>
        <div class="filter-group">
          <label>Fecha Fin</label>
          <input v-model="filters.endDate" type="date" />
        </div>
        <div class="filter-group">
          <label>Sensor</label>
          <select v-model="filters.sensor">
            <option value="">Todos los sensores</option>
            <option value="ph">pH</option>
            <option value="temperature">Temperatura</option>
            <option value="turbidity">Turbidez</option>
          </select>
        </div>
        <button @click="applyFilters" class="apply-btn">Aplicar Filtros</button>
      </div>

      <div class="data-table">
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Sensor</th>
              <th>Valor</th>
              <th>Unidad</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in historicalData" :key="record.id">
              <td>{{ formatDate(record.timestamp) }}</td>
              <td>{{ record.sensorName }}</td>
              <td>{{ record.value.toFixed(2) }}</td>
              <td>{{ record.unit }}</td>
              <td>
                <span class="status" :class="`status-${record.status}`">
                  {{ record.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const filters = ref({
  startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  endDate: new Date().toISOString().split('T')[0],
  sensor: '',
})

const historicalData = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    sensorName: 'pH',
    value: 7.2,
    unit: 'pH',
    status: 'normal',
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    sensorName: 'Temperatura',
    value: 22.5,
    unit: '°C',
    status: 'normal',
  },
  {
    id: 3,
    timestamp: new Date(),
    sensorName: 'Turbidez',
    value: 1.2,
    unit: 'NTU',
    status: 'normal',
  },
])

const formatDate = (date) => {
  return new Date(date).toLocaleString('es-ES')
}

const applyFilters = () => {
  // Aquí iría la lógica para filtrar los datos
  console.log('Filtros aplicados:', filters.value)
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.historical-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

.history-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header h1 {
  margin: 0;
  font-size: 24px;
}

.header-controls {
  display: flex;
  gap: 10px;
}

.logout-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.history-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.filters {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.filter-group input,
.filter-group select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
}

.apply-btn {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  align-self: flex-end;
  transition: background 0.3s;
}

.apply-btn:hover {
  background: #5568d3;
}

.data-table {
  background: white;
  border-radius: 8px;
  overflow: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

thead {
  background: #f5f5f5;
  border-bottom: 2px solid #e0e0e0;
}

th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

td {
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
  color: #666;
}

tr:hover {
  background: #f9f9f9;
}

.status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 12px;
}

.status-normal {
  background: #d4edda;
  color: #155724;
}

.status-warning {
  background: #fff3cd;
  color: #856404;
}

.status-critical {
  background: #f8d7da;
  color: #721c24;
}
</style>
