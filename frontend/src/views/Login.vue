<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1>HomeRegistry</h1>
      <h2>Sign In</h2>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="label">Username</label>
          <input
            type="text"
            v-model="username"
            class="input"
            placeholder="Enter your username"
            required
            autofocus
          />
        </div>

        <div class="form-group">
          <label class="label">Password</label>
          <input
            type="password"
            v-model="password"
            class="input"
            placeholder="Enter your password"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>Don't have an account? <router-link to="/register">Create one</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const username = ref('')
    const password = ref('')
    const loading = ref(false)
    const error = ref('')

    const handleLogin = async () => {
      error.value = ''
      loading.value = true

      const success = await authStore.login(username.value, password.value)

      if (success) {
        router.push('/')
      } else {
        error.value = authStore.error || 'Login failed'
      }

      loading.value = false
    }

    return {
      username,
      password,
      loading,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: var(--bg-secondary);
}

.auth-card {
  background: var(--bg-primary);
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.auth-card h1 {
  text-align: center;
  color: var(--primary);
  margin-bottom: 8px;
  font-size: 28px;
}

.auth-card h2 {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 32px;
  font-size: 20px;
  font-weight: 500;
}

.btn-full {
  width: 100%;
  margin-top: 16px;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  color: var(--text-secondary);
}

.auth-footer a {
  color: var(--primary);
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}

.error-message {
  background: var(--danger-bg, #fef2f2);
  color: var(--danger, #dc2626);
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}
</style>
