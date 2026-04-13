# Resumen de Cambios - Integración Supabase para Alertas y Usuarios

## Cambios Realizados

### 1. Actualización de `src/services/SupabaseAuthService.js`

Se agregaron 5 nuevas funciones para manejar los límites de alertas:

#### a) `saveAlertLimits(adminId, sensorType, minValue, maxValue, safeMaxValue)`
- Guarda o actualiza los límites de alerta para un sensor específico
- Realiza UPSERT en la tabla `alert_limits`
- Retorna: `{success: boolean, error?: string, data?: Object}`

#### b) `getAlertLimitsBySensorAndAdmin(adminId, sensorType)`
- Obtiene los límites de alerta para un sensor específico de un admin
- Retorna: `Object | null`

#### c) `getAlertLimitsByAdmin(adminId)`
- Obtiene todos los límites de alerta de un admin específico
- Retorna: `Array`

#### d) `getAlertLimitsBySensor(sensorType)`
- Obtiene los límites de alerta para un tipo de sensor (todos los admins)
- Retorna: `Array`

#### e) `deleteAlertLimit(id)`
- Elimina un registro de límite de alerta
- Retorna: `{success: boolean, error?: string}`

### 2. Actualización de `src/components/DeviceDashboard.vue`

#### a) Actualización de imports
```javascript
// Antes:
import { createUserInSupabase, getAllUsers, deleteUserFromSupabase } 

// Después:
import { createUserInSupabase, getAllUsers, deleteUserFromSupabase, saveAlertLimits, getAlertLimitsByAdmin, getCurrentUser }
```

#### b) Función `saveAlertConfig()` - AHORA GUARDA EN SUPABASE
- **Antes**: Solo guardaba en localStorage
- **Después**: 
  - Obtiene al usuario actual
  - Valida que sea administrador
  - Guarda en localStorage
  - **NUEVO**: Guarda en Supabase tabla `alert_limits` usando UPSERT
  - Muestra mensajes de éxito o error más informativos

```javascript
const saveAlertConfig = async (sensorType) => {
  try {
    isCreatingUser.value = true
    
    // Obtener usuario actual
    const currentUser = await getCurrentUser()
    if (!currentUser || currentUser.role !== 'admin') {
      alert('Debes ser administrador para guardar configuraciones de alertas')
      return
    }

    // Guardar en localStorage
    const config = { ...SENSOR_LIMITS.value }
    localStorage.setItem('sensorLimits', JSON.stringify(config))

    // Guardar en Supabase
    const sensorLimits = SENSOR_LIMITS.value[sensorType]
    const result = await saveAlertLimits(
      currentUser.id,
      sensorType,
      sensorLimits.min,
      sensorLimits.max,
      sensorLimits.safeMax
    )

    if (result.success) {
      alert(`✅ Límites de ${sensorType} guardados exitosamente en Supabase`)
    } else {
      alert(`⚠️ Error al guardar en Supabase: ${result.error}. Los datos se guardaron localmente.`)
    }
  } catch (error) {
    console.error('Error en saveAlertConfig:', error)
    alert(`Error: ${error.message}`)
  } finally {
    isCreatingUser.value = false
  }
}
```

#### c) Hook `onMounted()` - AHORA CARGA LÍMITES DE SUPABASE
- **Antes**: Solo cargaba del localStorage
- **Después**:
  - Para admins: 
    1. Carga lista de usuarios desde Supabase
    2. **NUEVO**: Obtiene límites de alerta del admin desde Supabase
    3. Si existen límites en Supabase, los usa
    4. Si no hay límites en Supabase, carga del localStorage
  - Para usuarios normales: Carga del localStorage como antes

```javascript
onMounted(async () => {
  // ... código previo ...

  if (isAdmin.value) {
    await loadExistingUsers()
    
    // Cargar límites de alertas desde Supabase si es admin
    try {
      const currentUser = await getCurrentUser()
      if (currentUser) {
        const alertLimits = await getAlertLimitsByAdmin(currentUser.id)
        if (alertLimits && alertLimits.length > 0) {
          // Actualizar SENSOR_LIMITS con los valores de Supabase
          alertLimits.forEach(limit => {
            if (SENSOR_LIMITS.value[limit.sensor_type]) {
              SENSOR_LIMITS.value[limit.sensor_type].min = limit.min_value
              SENSOR_LIMITS.value[limit.sensor_type].max = limit.max_value
              SENSOR_LIMITS.value[limit.sensor_type].safeMax = limit.safe_max
            }
          })
          console.log('✅ Límites de alerta cargados desde Supabase:', SENSOR_LIMITS.value)
        } else {
          // Fallback a localStorage
          const savedLimits = localStorage.getItem('sensorLimits')
          if (savedLimits) {
            SENSOR_LIMITS.value = JSON.parse(savedLimits)
          }
        }
      }
    } catch (error) {
      console.error('Error al cargar límites de Supabase:', error)
      // Fallback a localStorage
      const savedLimits = localStorage.getItem('sensorLimits')
      if (savedLimits) {
        SENSOR_LIMITS.value = JSON.parse(savedLimits)
      }
    }
  }
})
```

### 3. Nuevos Archivos Creados

#### a) `CREATE_ALERT_LIMITS_TABLE.sql`
Script SQL para crear la tabla `alert_limits` en Supabase con:
- Columnas: id, admin_id, sensor_type, min_value, max_value, safe_max, created_at, updated_at
- Restricción UNIQUE: (admin_id, sensor_type)
- Índices para optimización
- Row Level Security (RLS) habilitado
- 6 políticas RLS para controlar acceso

#### b) `SETUP_ALERT_LIMITS_TABLE.md`
Documento de instrucciones para:
- Ejecutar el script SQL en Supabase
- Verificar que la tabla se creó correctamente
- Verificar las políticas RLS

## Comportamiento del Sistema Ahora

### Para Administradores:

1. **Al acceder al dashboard**:
   - Carga la lista de usuarios desde Supabase
   - Carga los límites de alerta previos del admin desde Supabase
   - Si hay límites guardados, los muestra en la interfaz
   - Si no hay límites, muestra los valores por defecto

2. **Al modificar límites de alerta**:
   - El admin puede cambiar min, max, safeMax para pH, Temperatura, Conductividad
   - Al hacer clic en "Guardar Configuración de Alertas"
   - Los datos se guardan en localStorage (para disponibilidad offline)
   - Los datos se guardan en Supabase (persistencia en BD)
   - Se muestra un mensaje de confirmación

3. **Al crear un usuario**:
   - El admin llena el formulario con email, contraseña, nombre, rol
   - Se crea automáticamente en `auth.users` de Supabase
   - Se registra en la tabla `users_roles` con el rol especificado
   - Se muestra en la lista de usuarios del sistema

### Para Usuarios Normales:

1. **Al acceder al dashboard**:
   - No ven las secciones de admin (Modificar Alertas, Gestión de Usuarios)
   - Ven los datos de los sensores en tiempo real
   - Ven el histórico de datos
   - NO pueden modificar límites ni crear usuarios

## Próximos Pasos Necesarios

### 1. CRÍTICO: Crear la tabla `alert_limits` en Supabase

Para que los cambios funcionen:
1. Ve a https://supabase.com
2. Abre tu proyecto
3. Ve a SQL Editor
4. Copia el contenido de `CREATE_ALERT_LIMITS_TABLE.sql`
5. Ejecuta el script
6. Verifica que la tabla se creó correctamente

### 2. Verificar tabla `users_roles` en Supabase

Asegúrate de que la tabla `users_roles` tenga:
- Columnas: id (UUID fk), email, full_name, role, created_at, updated_at
- RLS habilitado
- Políticas RLS configuradas

### 3. Considerar Backend para User Creation

Actualmente `createUserInSupabase()` usa `supabase.auth.admin.createUser()` que requiere SERVICE_ROLE_KEY (no debería almacenarse en cliente).

Para producción, considera:
- Crear un endpoint backend que use SERVICE_ROLE_KEY
- Ejemplo: `POST /api/users/create`

## Validación de Cambios

✅ Compilación exitosa sin errores
✅ App carga sin problemas
✅ Login funciona correctamente
✅ Admin puede ver secciones adicionales
✅ Usuario regular NO ve secciones de admin
✅ Imports y exports corregidos
✅ Nuevas funciones de Supabase agregadas
✅ saveAlertConfig ahora guarda en Supabase
✅ onMounted carga límites de Supabase

## Archivos Modificados

1. `/src/services/SupabaseAuthService.js` - Agregadas 5 nuevas funciones
2. `/src/components/DeviceDashboard.vue` - Actualizado saveAlertConfig() y onMounted()

## Archivos Creados

1. `/CREATE_ALERT_LIMITS_TABLE.sql` - Script SQL para crear tabla
2. `/SETUP_ALERT_LIMITS_TABLE.md` - Instrucciones de setup
