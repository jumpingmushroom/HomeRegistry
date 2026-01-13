<template>
  <div id="app">
    <nav class="nav" v-if="!isSetupRoute">
      <div class="nav-content">
        <div class="nav-title">🏠 HomeRegistry</div>
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
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from './services/api'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const route = useRoute()

    const isSetupRoute = computed(() => route.path === '/setup')

    onMounted(async () => {
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
      isSetupRoute
    }
  }
}
</script>
