<template>
  <div id="app">
    <nav class="nav" v-if="!isSetupRoute">
      <div class="nav-content">
        <div class="nav-title">🏠 HomeRegistry</div>
        <button @click="toggleDarkMode" class="theme-toggle" :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
          {{ isDarkMode ? '☀️' : '🌙' }}
        </button>
      </div>
    </nav>

    <router-view />

    <nav class="bottom-nav" v-if="!isSetupRoute">
      <router-link to="/" class="bottom-nav-item" :class="{ active: $route.path === '/' }">
        <div class="bottom-nav-icon">📊</div>
        <div>Dashboard</div>
      </router-link>
      <router-link to="/items" class="bottom-nav-item" :class="{ active: $route.path.startsWith('/items') && $route.path !== '/items/add' }">
        <div class="bottom-nav-icon">📦</div>
        <div>Items</div>
      </router-link>
      <router-link to="/items/add" class="bottom-nav-item" :class="{ active: $route.path === '/items/add' }">
        <div class="bottom-nav-icon">📸</div>
        <div>Add</div>
      </router-link>
      <router-link to="/settings" class="bottom-nav-item" :class="{ active: $route.path === '/settings' }">
        <div class="bottom-nav-icon">⚙️</div>
        <div>Settings</div>
      </router-link>
    </nav>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from './services/api'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const isDarkMode = ref(false)

    const isSetupRoute = computed(() => route.path === '/setup')

    const initDarkMode = () => {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme === 'dark') {
        isDarkMode.value = true
        document.body.classList.add('dark-mode')
      } else if (savedTheme === 'light') {
        isDarkMode.value = false
        document.body.classList.remove('dark-mode')
      } else {
        // Check system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        isDarkMode.value = prefersDark
        if (prefersDark) {
          document.body.classList.add('dark-mode')
        }
      }
    }

    const toggleDarkMode = () => {
      isDarkMode.value = !isDarkMode.value
      if (isDarkMode.value) {
        document.body.classList.add('dark-mode')
        localStorage.setItem('theme', 'dark')
      } else {
        document.body.classList.remove('dark-mode')
        localStorage.setItem('theme', 'light')
      }
    }

    onMounted(async () => {
      initDarkMode()

      try {
        const { data: settings } = await api.getSettings()
        if (!settings.setup_completed && route.path !== '/setup') {
          router.push('/setup')
        }
      } catch (error) {
        console.error('Failed to check setup status:', error)
      }
    })

    return {
      isSetupRoute,
      isDarkMode,
      toggleDarkMode
    }
  }
}
</script>
