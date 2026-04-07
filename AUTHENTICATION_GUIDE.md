# 🔐 Sistema de Autenticación - Guía de Implementación

## 📋 Descripción General

Se ha implementado un sistema completo de autenticación y gestión de roles para la aplicación de monitoreo de embalses usando **Supabase** como servicio de autenticación y base de datos.

### Características Principales

- ✅ Autenticación segura con Supabase Auth
- ✅ Dos roles de usuario: **Usuario Normal** y **Administrador**
- ✅ Protección de rutas basada en roles
- ✅ Gestión de usuarios (solo administrador)
- ✅ Configuración de límites de alerta personalizados
- ✅ Almacenamiento seguro con Row Level Security (RLS)

---

## 🚀 Configuración Inicial

### 1. Crear Proyecto en Supabase

1. Ir a [supabase.com](https://supabase.com)
2. Crear una nueva cuenta o iniciar sesión
3. Crear un nuevo proyecto:
   - Nombre: `arandanos-monitoring`
   - Region: Seleccionar la más cercana
   - Password: Guardar de forma segura

### 2. Obtener Credenciales

1. En el dashboard de Supabase, ir a **Settings** → **API**
2. Copiar:
   - **Project URL** (VITE_SUPABASE_URL)
   - **anon public key** (VITE_SUPABASE_ANON_KEY)

### 3. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
VITE_API_URL=http://localhost:8000
```

### 4. Ejecutar Script de Setup

1. En Supabase Dashboard → SQL Editor
2. Crear nueva query
3. Copiar el contenido de `SUPABASE_SETUP.sql`
4. Ejecutar
5. Esto creará todas las tablas y políticas necesarias

---

## 📦 Instalación de Dependencias

```bash
npm install
```

Las nuevas dependencias instaladas son:
- **vue-router@4.4.0** - Enrutamiento
- **pinia@2.1.7** - State management
- **@supabase/supabase-js@2.39.8** - Cliente de Supabase

---

## 🏗️ Estructura de Carpetas Nuevas

```
src/
├── stores/
│   └── authStore.js           # Store de Pinia para autenticación
├── services/
│   └── supabaseClient.js       # Configuración y funciones de Supabase
├── views/
│   ├── Login.vue              # Pantalla de inicio de sesión
│   ├── Register.vue           # Pantalla de registro
│   ├── Dashboard.vue          # Dashboard de usuario normal
│   ├── HistoricalData.vue     # Datos históricos
│   ├── AdminDashboard.vue     # Panel principal de admin
│   ├── AdminUsers.vue         # Gestión de usuarios
│   └── AdminAlerts.vue        # Gestión de alertas
└── router.js                  # Configuración de rutas
```

---

## 👥 Roles de Usuario

### 1. Usuario Normal (`user`)

**Acceso:**
- Ver lista de dispositivos
- Ver dashboard de sensores
- Ver datos históricos
- Configuración personal

**Restricciones:**
- No puede crear usuarios
- No puede cambiar límites de alerta globales
- Solo ve sus propios datos

### 2. Administrador (`admin`)

**Acceso:**
- Panel de administración
- Crear y eliminar usuarios
- Cambiar roles de usuarios
- Configurar límites de alerta globales
- Ver todos los datos y actividades
- Gestionar sistema completo

---

## 🔑 Crear Usuarios

### Como Administrador en la Interfaz

1. Ir a **Panel de Administración** → **Gestión de Usuarios**
2. Click en **+ Nuevo Usuario**
3. Completar formulario:
   - Nombre Completo
   - Correo Electrónico
   - Contraseña Temporal
   - Rol (Usuario o Admin)
4. Click en **Crear Usuario**

### Manualmente (SQL)

```sql
-- Crear usuario en auth (usar Supabase Dashboard)
-- Ir a Authentication → New user

-- Luego en SQL Editor:
INSERT INTO users_roles (id, email, full_name, role) 
VALUES ('uuid-del-usuario', 'usuario@example.com', 'Nombre Completo', 'user')
ON CONFLICT DO NOTHING;
```

---

## ⚙️ Configurar Límites de Alerta

### Global (por Admin)

1. **Panel de Administración** → **Límites de Alertas**
2. Sección: **Configuración Global de Límites**
3. Ajustar valores para:
   - **pH**: Mínimo y Máximo
   - **Temperatura (°C)**: Mínimo y Máximo
   - **Turbidez (NTU)**: Máximo
4. Click en **Guardar Configuración**

### Por Usuario Específico

1. **Panel de Administración** → **Límites de Alertas**
2. Sección: **Límites por Usuario**
3. Seleccionar usuario del dropdown
4. Ajustar límites
5. Click en **Guardar Límites del Usuario**

### Límites Recomendados

| Sensor | Mínimo | Máximo | Unidad |
|--------|--------|--------|--------|
| **pH** | 6.5 | 8.5 | pH |
| **Temperatura** | 15 | 30 | °C |
| **Turbidez** | 0 | 5 | NTU |

---

## 📊 Tablas de Base de Datos

### `users_roles`
Almacena información de usuarios y sus roles.

```sql
id (UUID, PK)
email (TEXT, UNIQUE)
full_name (TEXT)
role (TEXT: 'user' | 'admin')
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### `alert_limits`
Almacena límites de alerta personalizados.

```sql
id (BIGSERIAL, PK)
user_id (UUID, FK → users_roles)
ph_min (DECIMAL)
ph_max (DECIMAL)
temp_min (DECIMAL)
temp_max (DECIMAL)
turbidity_max (DECIMAL)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### `sensor_readings`
Historial de lecturas de sensores (opcional).

```sql
id (BIGSERIAL, PK)
user_id (UUID, FK)
device_id (TEXT)
sensor_name (TEXT)
value (DECIMAL)
unit (TEXT)
status (TEXT: 'normal' | 'warning' | 'critical')
timestamp (TIMESTAMP)
created_at (TIMESTAMP)
```

---

## 🛡️ Seguridad (Row Level Security)

Las tablas están protegidas con políticas RLS:

- **Usuarios** solo ven sus propios datos
- **Admins** ven todos los datos
- Las inserciones/actualizaciones están restringidas según roles

---

## 🔄 Flujo de Autenticación

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       ▼
   ┌────────────┐
   │   Login    │
   │   Screen   │
   └──┬───────┬─┘
      │       │
   Email  Password
      │       │
      ▼───────▼
   ┌──────────────────┐
   │ supabase.auth    │
   │ .signInWithPwd() │
   └────────┬─────────┘
            │
      ┌─────▼──────┐
      │ Success?   │
      └─┬──────┬───┘
        │      │
       YES    NO
        │      │
        ▼      ▼
    ┌────┐  Error
    │ Get  │
    │Role  │
    └─┬──┬─┘
      │  │
   Admin User
      │  │
      ▼  ▼
  Different Routes
```

---

## 📱 Componentes Principales

### `authStore.js`
Store Pinia que maneja:
- Estado global de autenticación
- Login/logout
- Información de usuario y rol
- Suscripción a cambios de autenticación

### `supabaseClient.js`
Funciones de servicio:
- `login()` - Iniciar sesión
- `signup()` - Registrarse
- `logout()` - Cerrar sesión
- `getUserRole()` - Obtener rol de usuario
- `getAllUsers()` - Listar usuarios (admin)
- `createUserAsAdmin()` - Crear usuario
- `updateUserRole()` - Cambiar rol
- `getAlertLimits()` - Obtener límites
- `updateAlertLimits()` - Actualizar límites

### `router.js`
Configuración de rutas con guardias de protección:
- Rutas públicas: `/login`, `/register`
- Rutas de usuario: `/devices`, `/dashboard`, `/historical`
- Rutas de admin: `/admin`, `/admin/users`, `/admin/alerts`

---

## 🧪 Pruebas

### Flujo de Login

1. Ir a `http://localhost:5173/login`
2. Ingresar credenciales
3. Sistema verifica rol y redirige

### Crear Usuario Nuevo

1. Como admin, ir a `/admin/users`
2. Click en "+ Nuevo Usuario"
3. Completar datos
4. Verificar que el usuario aparece en la lista

### Cambiar Límites de Alerta

1. Como admin, ir a `/admin/alerts`
2. Ajustar valores globales
3. Guardar
4. Como usuario normal, los nuevos límites aplican

---

## ⚠️ Consideraciones Importantes

### Seguridad

1. **Nunca** guardes credenciales en el código
2. Usa variables de entorno (`.env`)
3. Las claves públicas de Supabase son seguras (anon key)
4. Implementa rate limiting en el backend para proteger contra ataques

### Escalabilidad

1. Los límites están por usuario en base de datos
2. El sistema puede manejar miles de usuarios
3. RLS asegura que cada usuario solo ve sus datos

### Mantenimiento

1. Monitorea el uso de Supabase
2. Realiza backups regularmente
3. Revisa logs de autenticación

---

## 🐛 Solución de Problemas

### Error: "Variables de Supabase no configuradas"

**Causa:** `.env` no está configurado correctamente

**Solución:**
1. Verifica que `.env` existe en la raíz
2. Comprueba que `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY` están presentes
3. Reinicia el servidor de desarrollo

### Error: "No tiene permisos para esta acción"

**Causa:** RLS está rechazando la solicitud

**Solución:**
1. Verifica el rol del usuario (`user` vs `admin`)
2. Comprueba que RLS está habilitado correctamente
3. Revisa políticas en Supabase Dashboard → SQL Editor

### Login no funciona

**Causa:** Credenciales incorrectas o usuario no existe

**Solución:**
1. Verifica email en Supabase → Authentication
2. Resetea contraseña si es necesario
3. Crea un usuario nuevo

---

## 📚 Referencias

- [Documentación de Supabase](https://supabase.com/docs)
- [Vue Router](https://router.vuejs.org/)
- [Pinia Store](https://pinia.vuejs.org/)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript/introduction)

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la consola del navegador (F12 → Console)
2. Revisa logs de Supabase
3. Verifica configuración en `.env`
4. Consulta documentación oficial

---

**Última actualización:** 2026-04-07
**Versión:** 1.0.0
