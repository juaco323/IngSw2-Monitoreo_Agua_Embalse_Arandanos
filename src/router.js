import { createRouter, createWebHistory } from 'vue-router'

// Importación lazy de vistas
const Login = () => import('./views/Login.vue')
const Register = () => import('./views/Register.vue')
const DeviceDashboard = () => import('./components/DeviceDashboard.vue')

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: 'Iniciar Sesión' },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: 'Registrarse' },
  },

  // Dashboard unificado para usuario normal y admin
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DeviceDashboard,
    meta: { title: 'Dashboard' },
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
router.beforeEach((to, from, next) => {
  // Actualizar título de la página
  document.title = to.meta.title
    ? `${to.meta.title} - Monitoreo Embalse`
    : 'Monitoreo Embalse'

  // Redirigir a login si no estamos autenticados y no es login/register
  if (to.path !== '/login' && to.path !== '/register') {
    const isAuthenticated = localStorage.getItem('isAuthenticated')
    if (!isAuthenticated) {
      next('/login')
      return
    }
  }

  next()
})

router.afterEach((to) => {
  // Código que se ejecuta después de la navegación
  window.scrollTo(0, 0)
})

export default router
