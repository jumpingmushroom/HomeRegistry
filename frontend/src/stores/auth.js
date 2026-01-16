import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const currentUser = computed(() => user.value)

  // Actions
  async function login(username, password) {
    loading.value = true
    error.value = null
    try {
      const response = await api.login(username, password)
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      await fetchUser()
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(username, password, email = null) {
    loading.value = true
    error.value = null
    try {
      await api.register(username, password, email)
      // Auto-login after registration
      return await login(username, password)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) {
      user.value = null
      return
    }
    try {
      const response = await api.getMe()
      user.value = response.data
    } catch (err) {
      // Token might be invalid
      logout()
    }
  }

  async function updateProfile(data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.updateMe(data)
      user.value = response.data
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Update failed'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  async function checkAuthStatus() {
    try {
      const response = await api.getAuthStatus()
      return response.data
    } catch (err) {
      return { has_users: false, user_count: 0 }
    }
  }

  // Initialize - check if we have a stored token and fetch user
  async function initialize() {
    if (token.value) {
      await fetchUser()
    }
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    currentUser,
    // Actions
    login,
    register,
    logout,
    fetchUser,
    updateProfile,
    checkAuthStatus,
    initialize
  }
})
