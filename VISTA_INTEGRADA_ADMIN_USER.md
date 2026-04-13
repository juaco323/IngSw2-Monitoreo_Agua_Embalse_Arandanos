# Dashboard Integrado Admin/Usuario

## 📋 Descripción General

Se ha creado una **vista unificada** (`DeviceDashboard.vue`) que integra la funcionalidad antigua del App.vue con el nuevo sistema de roles. La vista es **idéntica para admin y usuario**, con secciones adicionales exclusivas para administradores.

---

## 🎯 Características por Rol

### 👤 Usuario Regular (Employee)
- ✅ Vista de dispositivos con lista completa
- ✅ Dashboard con datos en tiempo real de sensores (pH, Temperatura, Conductividad)
- ✅ Información del sistema (sensores activos, sincronización, conexión Arduino)
- ✅ Diagnóstico de solicitudes de API
- ✅ Tabla de alertas del día actual
- ✅ Histórico de mediciones filtrable
- ✅ Gráficos de tendencias
- ✅ Exportar PDF de datos históricos
- ✅ Botón de logout

### 👨‍💼 Administrador (Admin)
- ✅ **Todo lo del usuario +**
- ✅ **Sección: Configuración de Rangos de Alertas**
  - Modificar límites mínimos y máximos de pH
  - Modificar límites de temperatura
  - Modificar límites de conductividad
  - Guardar configuración en localStorage (o Supabase)
  
- ✅ **Sección: Gestión de Usuarios**
  - Crear nuevas cuentas con email y contraseña
  - Asignar rol (Admin o Empleado) al crear cuenta
  - Crear automáticamente usuario en Supabase Auth
  - Registrar en tabla `users_roles` de Supabase
  - Ver lista de usuarios existentes
  - Eliminar usuarios

---

## 📁 Archivos Creados/Modificados

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `src/components/DeviceDashboard.vue` | ✨ NUEVO | Componente principal unificado con todas las vistas |
| `src/services/SupabaseAuthService.js` | ✨ NUEVO | Servicio para gestionar usuarios en Supabase |
| `src/router.js` | 📝 ACTUALIZADO | Apunta a DeviceDashboard en lugar de UserDashboard |

---

## 🔐 Sistema de Autenticación

### Flujo de Login
```
User Login (email + password)
  ↓
Login.vue determina rol por email
  ├─ Email contiene "admin" → role = "admin"
  └─ Otro → role = "employee"
  ↓
localStorage.setItem('userRole', role)
localStorage.setItem('isAuthenticated', 'true')
  ↓
Router → /dashboard (DeviceDashboard.vue)
  ↓
DeviceDashboard.vue calcula isAdmin = (userRole === 'admin')
  ↓
Muestra secciones admin si isAdmin = true
```

### Credenciales de Demostración

```javascript
// Admin
email: "admin@demo.com"
password: "demo123"
→ Acceso a configuración de alertas y gestión de usuarios

// Employee
email: "user@demo.com"
password: "demo123"
→ Solo acceso a visualización de datos
```

---

## ⚙️ Sección de Configuración de Alertas (Admin Only)

### Ubicación en la UI
- Aparece debajo de "Información del Sistema"
- Visible SOLO si `isAdmin = true`
- Fondo naranja para distinguir secciones de admin

### Funcionalidades
1. **Editar Límites de pH**
   - Mínimo (default: 6.0)
   - Máximo (default: 8.5)
   - Máximo Seguro (default: 8.0)

2. **Editar Límites de Temperatura**
   - Mínimo (default: 5°C)
   - Máximo (default: 35°C)
   - Máximo Seguro (default: 28°C)

3. **Editar Límites de Conductividad**
   - Mínimo (default: 100 µS/cm)
   - Máximo (default: 2000 µS/cm)
   - Máximo Seguro (default: 1500 µS/cm)

### Guardar Configuración
```javascript
// Se guarda en localStorage
localStorage.setItem('sensorLimits', JSON.stringify(SENSOR_LIMITS.value))

// En futuro, migrar a Supabase:
// INSERT INTO alert_limits (id, sensor_type, min, max, safe_max, admin_id, updated_at)
// VALUES (uuid, 'ph', 6.0, 8.5, 8.0, current_user_id, now())
```

---

## 👥 Sección de Gestión de Usuarios (Admin Only)

### Ubicación en la UI
- Aparece debajo de "Configuración de Alertas"
- Visible SOLO si `isAdmin = true`

### Crear Nuevo Usuario
```
Formulario:
├─ Email: usuario@empresa.com (validación email)
├─ Contraseña: ••••••••••
├─ Nombre Completo: Juan Pérez
└─ Rol: [Empleado | Administrador]

Al hacer clic "Crear Usuario":
1. Validar campos no vacíos
2. Llamar createUserInSupabase()
3. Automáticamente:
   - Crear en supabase.auth.users
   - Insertar en tabla users_roles
   - Email confirmado automáticamente
4. Mostrar mensaje de éxito/error
5. Recargar lista de usuarios
```

### Servicio SupabaseAuthService.js

```javascript
// Crear usuario
await createUserInSupabase(email, password, fullName, role)
// ↓
// 1. Crea en Auth
// 2. Inserta en users_roles con role='admin' o 'employee'

// Obtener todos
await getAllUsers()
// ↓
// SELECT * FROM users_roles ORDER BY created_at DESC

// Eliminar usuario
await deleteUserFromSupabase(userId)
// ↓
// 1. DELETE FROM users_roles
// 2. DELETE FROM auth.users
```

### Estado de Usuarios
Cuando admin accede a DeviceDashboard:
1. Se carga lista de usuarios existentes
2. Muestra tabla con: Email | Nombre | Rol | Fecha Creación | Acciones
3. Rol mostrado con badge coloreado (rojo=admin, azul=employee)
4. Botón "Eliminar" para cada usuario

---

## 🎨 Interfaz de Usuario

### Layout General
```
┌─ HEADER ─────────────────────────────────────────┐
│ [←] Nombre Dispositivo │ Status │ 📊 Datos │ 🚪 └─ Footer

┌─ CONTENT ────────────────────────────────────────┐
│ 
│ [Sensores Grid: pH | Temperatura | Conductividad]
│
│ [Información del Sistema]
│
│ ⚙️ CONFIGURACIÓN DE ALERTAS (solo admin)
│    [pH Card | Temp Card | Conductivity Card]
│
│ 👥 GESTIÓN DE USUARIOS (solo admin)
│    [Formulario Crear | Tabla Usuarios]
│
│ [Diagnóstico de Solicitudes]
│
│ [Tabla de Alertas]
│
│ [Histórico / Gráficos / Filtros]
│
└──────────────────────────────────────────────────┘
```

### Estilos de Admin
- Fondo naranja para secciones admin: `#ff9800`
- Texto "⚙️" para alertas, "👥" para usuarios
- Cards con borde naranja 2px
- Botones guardador verdes `#4caf50`
- Botones eliminar naranjas `#ff9800`

---

## 🔄 Flujo de Datos

### Al Montar Componente (onMounted)
```javascript
1. Verificar localStorage.isAuthenticated
   ├─ No auth → Redirect a /login
   └─ Auth OK → Continuar

2. Si es admin:
   ├─ Cargar lista de usuarios (getAllUsers)
   └─ Mostrar sección de gestión

3. Cargar sensores guardados
   └─ localStorage.sensorLimits

4. Iniciar polling de datos
   └─ updateSensorData() cada 5 segundos
```

### Actualización de Datos (cada 5s)
```javascript
1. GET /api/dashboard → sensores en tiempo real
2. GET /api/sensors/history → histórico
3. Procesar alertas si es necesario
4. Renderizar UI
```

---

## 🔧 Integración con Supabase (Cuando esté configurado)

### Variables de Entorno Requeridas
```
.env
VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
VITE_SUPABASE_ANON_KEY=tu-clave-anonima
```

### Tablas Necesarias

#### `users_roles`
```sql
CREATE TABLE users_roles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email text NOT NULL,
  full_name text,
  role text NOT NULL CHECK (role IN ('admin', 'employee')),
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);
```

#### `alert_limits`
```sql
CREATE TABLE alert_limits (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  admin_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  sensor_type text NOT NULL CHECK (sensor_type IN ('ph', 'temperature', 'conductivity')),
  min_value float NOT NULL,
  max_value float NOT NULL,
  safe_max float,
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);
```

---

## 📝 Notas Importantes

### Diferencia con Vista Anterior
**Antes:** Dos vistas separadas (Dashboard.vue, AdminDashboard.vue)
**Ahora:** Una sola vista (DeviceDashboard.vue) con secciones condicionales

### Ventajas
- ✅ Menos duplicación de código
- ✅ Sincronización automática de datos
- ✅ Fácil agregar nuevas funciones compartidas
- ✅ Controles admin integrados en el mismo lugar

### Limitaciones Actuales
- ⚠️ Autenticación simplificada (localStorage)
- ⚠️ Roles determinados por email
- ⚠️ Sin validación de permisos en backend
- ⚠️ Configuración de alertas guardada en localStorage

### Próximas Mejoras
1. [ ] Implementar autenticación Supabase completa
2. [ ] Guardar límites de alertas en BD
3. [ ] Validación de roles en backend
4. [ ] Auditoría de cambios por admin
5. [ ] Notificaciones en tiempo real
6. [ ] Logs de acceso y cambios

---

## 🧪 Pruebas Recomendadas

### Como Empleado
1. Login: `user@demo.com / demo123`
2. Verificar que NO aparecen secciones de admin
3. Visualizar sensores y datos históricos
4. Exportar PDF
5. Logout

### Como Admin
1. Login: `admin@demo.com / demo123`
2. Verificar que aparecen secciones de admin
3. Expandir "Configuración de Rangos"
   - Modificar valores
   - Guardar
   - Verificar localStorage
4. Expandir "Gestión de Usuarios"
   - Crear nuevo usuario
   - Asignar rol
   - Verificar en lista
   - Eliminar
5. Logout

---

## 🚀 Deployment

Para producción:
1. Configurar variables de Supabase en `.env`
2. Habilitar auth de Supabase en Login.vue
3. Implementar autenticación con Supabase en lugar de localStorage
4. Guardar límites de alertas en tabla `alert_limits`
5. Implementar RLS (Row Level Security) en Supabase
6. Validar permisos en backend API

---

¡Sistema completamente integrado y listo para usar! 🎉
