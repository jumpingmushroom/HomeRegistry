<template>
  <div id="app">
    <nav class="nav" v-if="!isSetupRoute">
      <div class="nav-content">
        <div class="nav-left">
          <div class="nav-title">🏠 HomeRegistry</div>
          <select
            v-if="properties.length > 0"
            v-model="selectedPropertyId"
            @change="onPropertyChange"
            class="property-selector"
          >
            <option v-for="property in properties" :key="property.id" :value="property.id">
              {{ property.name }}
            </option>
          </select>
        </div>
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
import { computed, onMounted, ref, provide, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from './services/api'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const isDarkMode = ref(false)
    const properties = ref([])
    const selectedPropertyId = ref(null)

    // Provide selected property to child components
    provide('selectedPropertyId', selectedPropertyId)
    provide('properties', properties)

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

    const loadProperties = async () => {
      try {
        const { data } = await api.getProperties()
        properties.value = data

        // Restore saved property or use first one
        const savedPropertyId = localStorage.getItem('selectedPropertyId')
        if (savedPropertyId && data.some(p => p.id === savedPropertyId)) {
          selectedPropertyId.value = savedPropertyId
        } else if (data.length > 0) {
          selectedPropertyId.value = data[0].id
          localStorage.setItem('selectedPropertyId', data[0].id)
        }
      } catch (error) {
        console.error('Failed to load properties:', error)
      }
    }

    const onPropertyChange = () => {
      if (selectedPropertyId.value) {
        localStorage.setItem('selectedPropertyId', selectedPropertyId.value)
      }
    }

    onMounted(async () => {
      initDarkMode()

      try {
        const { data: settings } = await api.getSettings()
        if (!settings.setup_completed && route.path !== '/setup') {
          router.push('/setup')
        } else {
          // Load properties after setup is complete
          await loadProperties()
        }
      } catch (error) {
        console.error('Failed to check setup status:', error)
      }
    })

    return {
      isSetupRoute,
      isDarkMode,
      toggleDarkMode,
      properties,
      selectedPropertyId,
      onPropertyChange
    }
  }
}
</script>
