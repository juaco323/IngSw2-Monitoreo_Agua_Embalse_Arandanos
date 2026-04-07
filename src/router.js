import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

// Vistas de autenticación
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

// Vistas de usuario normal
import DeviceList from '../components/DeviceList.vue'
import Dashboard from '../views/Dashboard.vue'
import HistoricalData from '../views/HistoricalData.vue'

// Vistas de administrador
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminUsers from '../views/AdminUsers.vue'
import AdminAlerts from '../views/AdminAlerts.vue'

const routes = [
  {
    path: '/',
    redirect: () => {
      const authStore = useAuthStore()
      if (!authStore.isAuthenticated) return '/login'
      return authStore.isAdmin ? '/admin' : '/devices'
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true, title: 'Iniciar Sesión' },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true, title: 'Registrarse' },
  },

  // Rutas de usuario normal
  {
    path: '/devices',
    name: 'DeviceList',
    component: DeviceList,
    meta: { requiresAuth: true, roles: ['user', 'admin'], title: 'Dispositivos' },
  },
  {
    path: '/dashboard/:deviceId',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, roles: ['user', 'admin'], title: 'Dashboard' },
  },
  {
    path: '/historical',
    name: 'HistoricalData',
    component: HistoricalData,
    meta: { requiresAuth: true, roles: ['user', 'admin'], title: 'Datos Históricos' },
  },

  // Rutas de administrador
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ['admin'], title: 'Panel de Administración' },
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsers,
    meta: { requiresAuth: true, roles: ['admin'], title: 'Gestión de Usuarios' },
  },
  {
    path: '/admin/alerts',
    name: 'AdminAlerts',
    component: AdminAlerts,
    meta: { requiresAuth: true, roles: ['admin'], title: 'Gestión de Límites de Alerta' },
  },

  // Catch-all para rutas no encontradas
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Guard global de navegación
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Inicializar autenticación si no está hecha
  if (!authStore.user && !authStore.isLoading) {
    await authStore.initializeAuth()
  }

  // Actualizar título de la página
  document.title = to.meta.title
    ? `${to.meta.title} - Monitoreo Embalse`
    : 'Monitoreo Embalse'

  // Si la ruta requiere autenticación
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return next('/login')
    }

    // Verificar roles si están definidos
    if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
      // Redirigir según el rol
      if (authStore.isAdmin) {
        return next('/admin')
      } else {
        return next('/devices')
      }
    }
  }

  // Si la ruta requiere que NO esté autenticado (login, register)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return next(authStore.isAdmin ? '/admin' : '/devices')
  }

  next()
})

router.afterEach((to) => {
  // Código que se ejecuta después de la navegación
  window.scrollTo(0, 0)
})

export default router
