# Plan de Pruebas - Dashboard Multirol

## 🧪 Casos de Prueba

### Caso 1: Usuario Regular
**Entrada:** Login con `user@demo.com / demo123`
**Acciones:**
1. Completar formulario de login
2. Verificar redirección a `/dashboard`
3. Verificar que localStorage contiene:
   - `isAuthenticated: "true"`
   - `userEmail: "user@demo.com"`
   - `userRole: "user"`
4. Verificar que el botón "⚙️ Modificar Alertas" NO aparece
5. Verificar que sección de admin NO aparece
6. Clic en "Cerrar Sesión"
7. Verificar limpieza de localStorage

**Resultado Esperado:**
- ✅ Login exitoso
- ✅ Dashboard sin botón de admin
- ✅ Sección de usuario visible
- ✅ Logout limpia datos

---

### Caso 2: Usuario Admin
**Entrada:** Login con `admin@demo.com / demo123`
**Acciones:**
1. Completar formulario de login
2. Verificar redirección a `/dashboard`
3. Verificar que localStorage contiene:
   - `isAuthenticated: "true"`
   - `userEmail: "admin@demo.com"`
   - `userRole: "admin"`
4. Verificar que el botón "⚙️ Modificar Alertas" SÍ aparece
5. Verificar que sección de admin SÍ aparece
6. Clic en botón "⚙️ Modificar Alertas"
7. Verificar redirección a `/alerts`

**Resultado Esperado:**
- ✅ Login exitoso con role "admin"
- ✅ Dashboard muestra botón de admin
- ✅ Sección admin visible
- ✅ Navegación a `/alerts` funciona

---

### Caso 3: Gestión de Alertas
**Entrada:** Usuario admin en `/alerts`
**Acciones:**
1. Verificar que solo aparece si userRole === "admin"
2. Ingresar valores en formularios:
   - pH: 7.0 - 7.5
   - Temperatura: 18 - 25
   - Conductividad: 400 - 600
3. Clic en "Guardar" para cada sensor
4. Verificar localStorage.alertLimits contiene nuevos valores
5. Clic en "Volver"
6. Verificar redirección a `/dashboard`

**Resultado Esperado:**
- ✅ Acceso permitido solo para admin
- ✅ Valores guardados en localStorage
- ✅ Botón volver funciona
- ✅ Vuelve correctamente al dashboard

---

### Caso 4: Acceso Directo a /alerts (Usuario)
**Entrada:** Usuario regular intenta acceder directamente a `/alerts`
**Acciones:**
1. Logout para limpiar datos
2. Login como `user@demo.com`
3. Escribir directamente en URL: `http://localhost:5174/alerts`
4. Verificar que se permite pero el botón admin no aparece

**Resultado Esperado:**
- ✅ Página carga (no hay bloqueo de ruta)
- ✅ Pero sin funciones de admin (verificación en el componente)

---

### Caso 5: Autenticación Required
**Entrada:** Intento acceder a `/dashboard` sin login
**Acciones:**
1. Logout para limpiar localStorage
2. Escribir directamente: `http://localhost:5174/dashboard`
3. Verificar redirección

**Resultado Esperado:**
- ✅ Redirige automáticamente a `/login`

---

### Caso 6: Email con "admin"
**Entrada:** Login con email que contiene "admin" pero sin ser admin@demo.com
**Acciones:**
1. Login: `administrador@empresa.com / cualquier_password`
2. Verificar que userRole = "admin"
3. Verificar que botón "Modificar Alertas" aparece

**Resultado Esperado:**
- ✅ Rol determinado correctamente por email
- ✅ Acceso de admin otorgado

---

## 📊 Matriz de Pruebas

| Email | Contain "admin"? | Expected Role | Admin Button | /alerts Access |
|-------|------------------|----------------|--------------|----------------|
| user@demo.com | ❌ | user | ❌ No | ✅ Sí (sin admin) |
| admin@demo.com | ✅ | admin | ✅ Sí | ✅ Sí (con admin) |
| administrador@empresa.com | ✅ | admin | ✅ Sí | ✅ Sí (con admin) |
| desarrollo@admin.com | ✅ | admin | ✅ Sí | ✅ Sí (con admin) |
| regular@user.com | ❌ | user | ❌ No | ✅ Sí (sin admin) |

---

## 🔍 Verificaciones en DevTools

### LocalStorage
```javascript
// Después de login como user:
localStorage.getItem('isAuthenticated')  // "true"
localStorage.getItem('userRole')         // "user"

// Después de login como admin:
localStorage.getItem('isAuthenticated')  // "true"
localStorage.getItem('userRole')         // "admin"

// Después de logout:
localStorage.getItem('isAuthenticated')  // null
```

### Variables Computed
```javascript
// En UserDashboard.vue
isAdmin  // ref que depende de localStorage.userRole
```

---

## ✅ Checklist Final

- [ ] Caso 1: Usuario regular - Login, dashboard, logout
- [ ] Caso 2: Usuario admin - Login, dashboard + botón, alertas
- [ ] Caso 3: Configuración de alertas guardada
- [ ] Caso 4: Usuario regular no puede ver admin features
- [ ] Caso 5: Sin auth → redirect a login
- [ ] Caso 6: Email con "admin" → rol admin
- [ ] Botón ubicado en esquina superior izquierda
- [ ] Estilos responsive en móvil
- [ ] Navegación fluida entre vistas
- [ ] localStorage se limpia al logout

---

## 🐛 Debugging

### Si el botón no aparece:
1. Verifica: `console.log(isAdmin.value)`
2. Verifica: `localStorage.getItem('userRole')`
3. Comprueba red tab: GET `/dashboard` vs `/alerts`

### Si no se guarda configuración:
1. Abre DevTools → Application → LocalStorage
2. Busca la key: `alertLimits`
3. Verifica que el JSON es válido

### Si hay error de navegación:
1. Abre DevTools → Network
2. Verifica respuestas HTTP
3. Revisa Console para errores JavaScript

---

¡Listo para pruebas! 🚀
