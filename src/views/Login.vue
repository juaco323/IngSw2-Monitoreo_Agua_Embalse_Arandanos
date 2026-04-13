
<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>🌊 Monitoreo Embalse</h1>
        <p>Sistema de Monitoreo de Agua</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Correo Electrónico</label>
          <input
            v-model="form.email"
            type="email"
            id="email"
            placeholder="tu@email.com"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            v-model="form.password"
            type="password"
            id="password"
            placeholder="••••••••"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button
          type="submit"
          class="login-btn"
          :disabled="isLoading"
        >
          <span v-if="!isLoading">Iniciar Sesión</span>
          <span v-else>Cargando...</span>
        </button>
      </form>

      <div class="login-footer">
        <p>¿No tienes cuenta? <router-link to="/register">Regístrate aquí</router-link></p>
      </div>

      <div class="demo-info">
        <p><strong>Demostración:</strong></p>
        <p>Admin: admin@demo.com / demo123</p>
        <p>Usuario: user@demo.com / demo123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({
  email: '',
  password: '',
})

const error = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  error.value = ''

  if (!form.value.email || !form.value.password) {
    error.value = 'Por favor completa todos los campos'
    return
  }

  // Demostración: Determinar rol según el email
  let userRole = 'user'
  if (form.value.email.includes('admin')) {
    userRole = 'admin'
  }

  // Guardar información de autenticación en localStorage
  localStorage.setItem('isAuthenticated', 'true')
  localStorage.setItem('userEmail', form.value.email)
  localStorage.setItem('userRole', userRole)

  // Redirigir al dashboard
  router.push('/dashboard')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

.login-box {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  margin: 0;
  color: #333;
  font-size: 28px;
}

.login-header p {
  margin: 8px 0 0 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.form-group input {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  border-left: 4px solid #c33;
}

.login-btn {
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

.login-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.login-footer a:hover {
  text-decoration: underline;
}

.demo-info {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  margin-top: 20px;
  font-size: 12px;
  color: #666;
}

.demo-info p {
  margin: 4px 0;
}

.demo-info strong {
  color: #333;
}
</style>
