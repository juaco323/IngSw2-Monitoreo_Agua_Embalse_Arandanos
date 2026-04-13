# 🔧 Ejemplos de Código - Sistema Admin/Usuario

## 📚 Tabla de Contenidos
1. Detección de Rol
2. Creación de Usuarios
3. Gestión de Configuración
4. Llamadas a API

---

## 1️⃣ Detección de Rol

### En DeviceDashboard.vue

```javascript
// Script
import { computed } from 'vue'

// Computed que calcula si es admin
const isAdmin = computed(() => {
  const userRole = localStorage.getItem('userRole')
  return userRole === 'admin'
})

// En template
<template>
  <!-- Mostrar solo si es admin -->
  <section v-if="isAdmin" class="admin-section">
    ⚙️ Configuración de Alertas (Admin)
  </section>

  <!-- Mostrar siempre -->
  <div class="info-card">
    <div class="info-card-label">Rol de Usuario</div>
    <div class="info-card-value" :class="isAdmin ? 'admin-role' : 'user-role'">
      {{ isAdmin ? '👨‍💼 Administrador' : '👤 Empleado' }}
    </div>
  </div>
</template>

// Estilos
<style>
.info-card-value.admin-role {
  color: #d32f2f;
  background: #ffebee;
  padding: 4px 8px;
  border-radius: 4px;
}

.info-card-value.user-role {
  color: #1976d2;
  background: #e3f2fd;
  padding: 4px 8px;
  border-radius: 4px;
}
</style>
```

---

## 2️⃣ Creación de Usuarios

### Flujo Completo

```javascript
// En DeviceDashboard.vue

import { ref } from 'vue'
import { createUserInSupabase } from '@/services/SupabaseAuthService'

// State
const newUser = ref({
  email: '',
  password: '',
  fullName: '',
  role: 'employee'
})
const isCreatingUser = ref(false)
const userCreationError = ref('')
const userCreationSuccess = ref('')

// Método de creación
const createNewUser = async () => {
  // 1. Validar
  if (!newUser.value.email || !newUser.value.password || !newUser.value.fullName) {
    userCreationError.value = 'Por favor completa todos los campos'
    userCreationSuccess.value = ''
    return
  }

  // 2. Iniciar loading
  isCreatingUser.value = true
  userCreationError.value = ''
  userCreationSuccess.value = ''

  try {
    // 3. Llamar servicio
    const result = await createUserInSupabase(
      newUser.value.email,
      newUser.value.password,
      newUser.value.fullName,
      newUser.value.role
    )

    // 4. Manejar resultado
    if (result.success) {
      // ✅ Éxito
      userCreationSuccess.value = `Usuario ${newUser.value.email} creado exitosamente`
      
      // Limpiar formulario
      newUser.value = {
        email: '',
        password: '',
        fullName: '',
        role: 'employee'
      }
      
      // Recargar lista
      await loadExistingUsers()
    } else {
      // ❌ Error
      userCreationError.value = result.error || 'Error al crear usuario'
    }
  } catch (error) {
    userCreationError.value = `Error: ${error.message}`
  } finally {
    isCreatingUser.value = false
  }
}

// Template
<template>
  <section v-if="isAdmin" class="admin-section">
    <h2>👥 Gestión de Usuarios</h2>
    
    <div class="user-creation-form">
      <h3>Crear Nueva Cuenta</h3>
      
      <div class="form-grid">
        <div class="form-group">
          <label>Email:</label>
          <input v-model="newUser.email" type="email" />
        </div>
        
        <div class="form-group">
          <label>Contraseña:</label>
          <input v-model="newUser.password" type="password" />
        </div>
        
        <div class="form-group">
          <label>Nombre Completo:</label>
          <input v-model="newUser.fullName" type="text" />
        </div>
        
        <div class="form-group">
          <label>Rol:</label>
          <select v-model="newUser.role">
            <option value="employee">Empleado</option>
            <option value="admin">Administrador</option>
          </select>
        </div>
      </div>

      <!-- Mensajes -->
      <div v-if="userCreationError" class="error-message">
        {{ userCreationError }}
      </div>
      <div v-if="userCreationSuccess" class="success-message">
        {{ userCreationSuccess }}
      </div>

      <!-- Botón -->
      <button 
        @click="createNewUser"
        :disabled="isCreatingUser"
      >
        {{ isCreatingUser ? 'Creando...' : '✅ Crear Usuario' }}
      </button>
    </div>
  </section>
</template>
```

---

## 3️⃣ Servicio SupabaseAuthService.js

### Crear Usuario

```javascript
export async function createUserInSupabase(email, password, fullName, role) {
  try {
    // 1. Crear en Auth de Supabase
    const { data: authData, error: authError } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true  // Auto-confirmar email
    })

    if (authError) {
      console.error('Error creating auth user:', authError)
      return {
        success: false,
        error: authError.message
      }
    }

    const userId = authData.user.id

    // 2. Insertar en tabla users_roles
    const { error: roleError } = await supabase
      .from('users_roles')
      .insert([
        {
          id: userId,
          email,
          full_name: fullName,
          role: role === 'admin' ? 'admin' : 'employee',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ])

    if (roleError) {
      console.error('Error inserting user role:', roleError)
      
      // Limpiar si falla
      await supabase.auth.admin.deleteUser(userId)
      
      return {
        success: false,
        error: roleError.message
      }
    }

    return {
      success: true,
      userId
    }
  } catch (error) {
    console.error('Exception:', error)
    return {
      success: false,
      error: error.message
    }
  }
}
```

### Obtener Todos los Usuarios

```javascript
export async function getAllUsers() {
  try {
    const { data, error } = await supabase
      .from('users_roles')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching users:', error)
      return []
    }

    return data || []
  } catch (error) {
    console.error('Exception:', error)
    return []
  }
}

// Uso
const existingUsers = ref([])

const loadExistingUsers = async () => {
  try {
    const users = await getAllUsers()
    existingUsers.value = users
  } catch (error) {
    console.error('Error al cargar usuarios:', error)
  }
}
```

### Eliminar Usuario

```javascript
export async function deleteUserFromSupabase(userId) {
  try {
    // 1. Eliminar de users_roles
    const { error: roleError } = await supabase
      .from('users_roles')
      .delete()
      .eq('id', userId)

    if (roleError) {
      console.error('Error deleting user role:', roleError)
      return {
        success: false,
        error: roleError.message
      }
    }

    // 2. Eliminar de Auth
    const { error: authError } = await supabase.auth.admin.deleteUser(userId)

    if (authError) {
      console.error('Error deleting auth user:', authError)
      // No retornar error - ya eliminamos del DB
    }

    return { success: true }
  } catch (error) {
    console.error('Exception:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

// Uso
const deleteUser = async (userId) => {
  if (!confirm('¿Estás seguro?')) {
    return
  }

  try {
    const result = await deleteUserFromSupabase(userId)
    if (result.success) {
      await loadExistingUsers()
    }
  } catch (error) {
    console.error('Error:', error)
  }
}
```

---

## 4️⃣ Gestión de Configuración de Alertas

### Guardar Limits

```javascript
// State
let SENSOR_LIMITS = ref({
  ph: { min: 6.0, max: 8.5, safeMax: 8.0 },
  temperature: { min: 5, max: 35, safeMax: 28 },
  conductivity: { min: 100, max: 2000, safeMax: 1500 }
})

// Método guardar
const saveAlertConfig = (sensorType) => {
  // Guardar en localStorage
  const config = {
    ...SENSOR_LIMITS.value
  }
  localStorage.setItem('sensorLimits', JSON.stringify(config))
  
  // Mostrar confirmación
  alert(`Límites de ${sensorType} guardados exitosamente`)
}

// En futuro - guardar en Supabase
const saveAlertConfigToSupabase = async (sensorType) => {
  const currentUser = await supabase.auth.getUser()
  
  const { error } = await supabase
    .from('alert_limits')
    .insert([
      {
        admin_id: currentUser.user.id,
        sensor_type: sensorType,
        min_value: SENSOR_LIMITS.value[sensorType].min,
        max_value: SENSOR_LIMITS.value[sensorType].max,
        safe_max: SENSOR_LIMITS.value[sensorType].safeMax,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ])

  if (error) {
    console.error('Error saving config:', error)
  }
}
```

### Cargar Limits

```javascript
// En onMounted
const loadSensorLimits = () => {
  // Cargar desde localStorage
  const savedLimits = localStorage.getItem('sensorLimits')
  
  if (savedLimits) {
    try {
      SENSOR_LIMITS.value = JSON.parse(savedLimits)
    } catch (e) {
      console.error('Error al cargar límites guardados:', e)
    }
  }
}

// En futuro - cargar desde Supabase
const loadSensorLimitsFromSupabase = async () => {
  const { data, error } = await supabase
    .from('alert_limits')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(3)  // Últimas 3 configuraciones (ph, temp, conductivity)

  if (error) {
    console.error('Error loading limits:', error)
    return
  }

  // Reorganizar por sensor_type
  data.forEach(limit => {
    SENSOR_LIMITS.value[limit.sensor_type] = {
      min: limit.min_value,
      max: limit.max_value,
      safeMax: limit.safe_max
    }
  })
}
```

### Template de Configuración

```vue
<template>
  <section v-if="isAdmin" class="alerts-config-section">
    <h2>⚙️ Configuración de Rangos de Alertas (Admin)</h2>
    
    <div class="alerts-config-grid">
      <!-- pH -->
      <div class="alert-config-card">
        <h3>🔬 pH</h3>
        
        <div class="config-group">
          <label>Mínimo:</label>
          <input v-model.number="SENSOR_LIMITS.ph.min" type="number" step="0.1" />
        </div>
        
        <div class="config-group">
          <label>Máximo:</label>
          <input v-model.number="SENSOR_LIMITS.ph.max" type="number" step="0.1" />
        </div>
        
        <div class="config-group">
          <label>Máximo Seguro:</label>
          <input v-model.number="SENSOR_LIMITS.ph.safeMax" type="number" step="0.1" />
        </div>
        
        <button @click="saveAlertConfig('ph')">Guardar pH</button>
      </div>

      <!-- Similar para temperatura y conductividad -->
    </div>
  </section>
</template>
```

---

## 5️⃣ Validación de Alertas

### Verificar si Valor está en Rango

```javascript
const getStatus = (value, min, max) => {
  const percentage = ((value - min) / (max - min)) * 100
  
  if (percentage < 15 || percentage > 85) {
    return 'danger'  // Rojo
  }
  if (percentage < 35 || percentage > 65) {
    return 'warning'  // Naranja
  }
  return 'safe'  // Verde
}

// Uso
const phStatus = getStatus(7.2, SENSOR_LIMITS.value.ph.min, SENSOR_LIMITS.value.ph.max)
// phStatus = 'safe' (7.2 está entre 6.0 y 8.5)
```

### Estado General del Sistema

```javascript
const overallStatus = computed(() => {
  const statuses = [
    getStatus(sensors.value.ph.value, SENSOR_LIMITS.value.ph.min, SENSOR_LIMITS.value.ph.max),
    getStatus(sensors.value.temperature.value, SENSOR_LIMITS.value.temperature.min, SENSOR_LIMITS.value.temperature.max),
    getStatus(sensors.value.conductivity.value, SENSOR_LIMITS.value.conductivity.min, SENSOR_LIMITS.value.conductivity.max)
  ]
  
  if (statuses.includes('danger')) return 'danger'
  if (statuses.includes('warning')) return 'warning'
  return 'safe'
})

const overallStatusText = computed(() => {
  if (overallStatus.value === 'danger') return 'Situación Peligrosa'
  if (overallStatus.value === 'warning') return 'Advertencia'
  return 'Sistema Normal'
})
```

---

## 6️⃣ Flujo de Datos Actualización

### Polling de Sensores (cada 5s)

```javascript
const updateSensorData = async () => {
  if (!selectedDeviceId.value) return

  // 1. Obtener datos del API
  await loadDashboardFromApi()

  // 2. Obtener histórico
  if (currentView.value === 'dashboard' || currentView.value === 'history') {
    await loadHistoryFromApi()
  }

  // 3. Actualizar UI
  requestMonitor.value.ui.lastRenderedAt = formatDateTime(new Date())

  // 4. Si hay alertas y no es modo simulado
  if (currentView.value !== 'dashboard') return
  if (IS_SIMULATED_MODE) return

  const latestRecord = historyRecords.value[0]
  if (!latestRecord || !latestRecord.isAlert) return

  // 5. Procesar alertas (Telegram, Email, etc)
  if (latestRecord.timestamp > lastProcessedAlertTimestamp.value) {
    await checkAndSendAlerts(devices.value[0], SENSOR_LIMITS.value)
    lastProcessedAlertTimestamp.value = latestRecord.timestamp
  }
}

// Iniciar polling
const startSensorUpdates = () => {
  if (updateInterval) clearInterval(updateInterval)
  updateSensorData()  // Inmediato
  updateInterval = setInterval(updateSensorData, 5000)  // Cada 5s
}

// Detener polling
const stopSensorUpdates = () => {
  if (updateInterval) {
    clearInterval(updateInterval)
    updateInterval = null
  }
}

// En onMounted
onMounted(() => {
  startSensorUpdates()
})

// En onUnmounted
onUnmounted(() => {
  stopSensorUpdates()
})
```

---

## 7️⃣ Métodos de Utilidad

### Formatear Fechas

```javascript
const formatDate = (date) => {
  if (!date) return 'N/A'
  const d = typeof date === 'string' ? new Date(date) : date
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}-${month}-${year}`
}

const formatTime = (date) => {
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  const second = String(date.getSeconds()).padStart(2, '0')
  return `${hour}:${minute}:${second}`
}

const formatDateTime = (date) => {
  return `${formatDate(date)} ${formatTime(date)}`
}

// Uso
console.log(formatDate(new Date()))          // "13-04-2026"
console.log(formatTime(new Date()))          // "14:30:45"
console.log(formatDateTime(new Date()))      // "13-04-2026 14:30:45"
```

### Escape HTML (para PDF)

```javascript
const escapeHtml = (value) => {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

// Uso en PDF export
const htmlContent = `
  <td>${escapeHtml(row.deviceName)}</td>
  <td>${escapeHtml(row.temperature)}</td>
`
```

---

## 🧪 Testing en Console

```javascript
// Ver rol actual
console.log(localStorage.getItem('userRole'))
// → "admin" o "employee"

// Ver si está autenticado
console.log(localStorage.getItem('isAuthenticated'))
// → "true"

// Simular logout
localStorage.removeItem('isAuthenticated')
localStorage.removeItem('userRole')
location.reload()

// Ver límites guardados
console.log(JSON.parse(localStorage.getItem('sensorLimits')))
// → { ph: {...}, temperature: {...}, conductivity: {...} }

// Cambiar rol (solo para testing!)
localStorage.setItem('userRole', 'admin')
location.reload()
```

---

¡Ejemplos completos y listos para usar! 🚀
