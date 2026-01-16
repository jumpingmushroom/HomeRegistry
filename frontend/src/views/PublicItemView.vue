<template>
  <div class="public-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else-if="error" class="error-card">
      <h2>Item Not Found</h2>
      <p>{{ error }}</p>
      <router-link to="/login" class="btn btn-primary">Sign In</router-link>
    </div>

    <div v-else class="public-card">
      <div class="public-header">
        <h1>{{ item.name }}</h1>
      </div>

      <div v-if="item.primary_image_id" class="public-image">
        <img :src="getImageUrl(item.primary_image_id)" :alt="item.name" />
      </div>

      <div class="public-details">
        <div v-if="item.description" class="detail-row">
          <label>Description</label>
          <p>{{ item.description }}</p>
        </div>

        <div v-if="item.category_name" class="detail-row">
          <label>Category</label>
          <p>{{ item.category_name }}</p>
        </div>

        <div v-if="item.condition" class="detail-row">
          <label>Condition</label>
          <p class="condition-badge" :class="item.condition">{{ formatCondition(item.condition) }}</p>
        </div>
      </div>

      <div class="public-footer">
        <p>This item is registered in HomeRegistry</p>
        <router-link to="/login" class="btn btn-primary">Sign in for full details</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'

export default {
  name: 'PublicItemView',
  setup() {
    const route = useRoute()
    const item = ref(null)
    const loading = ref(true)
    const error = ref(null)

    const loadItem = async () => {
      loading.value = true
      error.value = null

      try {
        const { data } = await api.getPublicItem(route.params.id)
        item.value = data
      } catch (err) {
        error.value = err.response?.data?.detail || 'Item not found'
      } finally {
        loading.value = false
      }
    }

    const getImageUrl = (imageId) => {
      return api.getImageUrl(imageId, false)
    }

    const formatCondition = (condition) => {
      const conditions = {
        new: 'New',
        excellent: 'Excellent',
        good: 'Good',
        fair: 'Fair',
        poor: 'Poor'
      }
      return conditions[condition] || condition
    }

    onMounted(() => {
      loadItem()
    })

    return {
      item,
      loading,
      error,
      getImageUrl,
      formatCondition
    }
  }
}
</script>

<style scoped>
.public-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: var(--background);
}

.public-card {
  background: var(--surface);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 500px;
  overflow: hidden;
}

.error-card {
  background: var(--surface);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  padding: 40px;
  text-align: center;
  max-width: 400px;
}

.error-card h2 {
  margin-bottom: 16px;
  color: var(--text-primary);
}

.error-card p {
  margin-bottom: 24px;
  color: var(--text-secondary);
}

.public-header {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.public-header h1 {
  margin: 0;
  font-size: 24px;
  color: var(--text-primary);
}

.public-image {
  width: 100%;
  aspect-ratio: 4/3;
  overflow: hidden;
  background: var(--background);
}

.public-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.public-details {
  padding: 24px;
}

.detail-row {
  margin-bottom: 16px;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-row label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.detail-row p {
  margin: 0;
  color: var(--text-primary);
  font-size: 16px;
}

.condition-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.condition-badge.new {
  background: #e8f5e9;
  color: #2e7d32;
}

.condition-badge.excellent {
  background: #e3f2fd;
  color: #1565c0;
}

.condition-badge.good {
  background: #fff3e0;
  color: #ef6c00;
}

.condition-badge.fair {
  background: #fff8e1;
  color: #f9a825;
}

.condition-badge.poor {
  background: #ffebee;
  color: #c62828;
}

.public-footer {
  padding: 24px;
  border-top: 1px solid var(--border-color);
  text-align: center;
  background: var(--background);
}

.public-footer p {
  margin: 0 0 16px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

/* Dark mode adjustments */
body.dark-mode .condition-badge.new {
  background: #1b5e20;
  color: #a5d6a7;
}

body.dark-mode .condition-badge.excellent {
  background: #0d47a1;
  color: #90caf9;
}

body.dark-mode .condition-badge.good {
  background: #e65100;
  color: #ffcc80;
}

body.dark-mode .condition-badge.fair {
  background: #f57f17;
  color: #fff59d;
}

body.dark-mode .condition-badge.poor {
  background: #b71c1c;
  color: #ef9a9a;
}
</style>
