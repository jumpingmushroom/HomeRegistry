<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1>HomeRegistry</h1>
      <h2>Create Account</h2>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="label">Username</label>
          <input
            type="text"
            v-model="username"
            class="input"
            placeholder="Choose a username"
            required
            autofocus
            minlength="3"
          />
        </div>

        <div class="form-group">
          <label class="label">Email (optional)</label>
          <input
            type="email"
            v-model="email"
            class="input"
            placeholder="Enter your email"
          />
        </div>

        <div class="form-group">
          <label class="label">Password</label>
          <input
            type="password"
            v-model="password"
            class="input"
            placeholder="Create a password"
            required
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label class="label">Confirm Password</label>
          <input
            type="password"
            v-model="confirmPassword"
            class="input"
            placeholder="Confirm your password"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Create Account' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>Already have an account? <router-link to="/login">Sign in</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const username = ref('')
    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const loading = ref(false)
    const error = ref('')

    const handleRegister = async () => {
      error.value = ''

      // Validate passwords match
      if (password.value !== confirmPassword.value) {
        error.value = 'Passwords do not match'
        return
      }

      // Validate password length
      if (password.value.length < 6) {
        error.value = 'Password must be at least 6 characters'
        return
      }

      loading.value = true

      const success = await authStore.register(
        username.value,
        password.value,
        email.value || null
      )

      if (success) {
        router.push('/')
      } else {
        error.value = authStore.error || 'Registration failed'
      }

      loading.value = false
    }

    return {
      username,
      email,
      password,
      confirmPassword,
      loading,
      error,
      handleRegister
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
