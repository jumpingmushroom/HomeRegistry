<template>
  <div class="container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else-if="item">
      <button @click="$router.push('/items')" class="btn btn-outline" style="margin-bottom: 16px;">
        ← Back to Items
      </button>

      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
          <h1 style="margin: 0;">{{ item.name }}</h1>
          <div style="display: flex; gap: 8px;">
            <button @click="editMode = true" class="btn btn-outline">Edit</button>
            <button @click="deleteItem" class="btn" style="background: var(--error-color); color: white;">Delete</button>
          </div>
        </div>

        <div v-if="item.images && item.images.length > 0" style="margin-bottom: 16px;">
          <div style="width: 100%; max-width: 600px; margin: 0 auto;">
            <img :src="getImageUrl(currentImageId)"
                 style="width: 100%; border-radius: var(--border-radius);" />
          </div>
          <div style="display: flex; gap: 8px; margin-top: 12px; overflow-x: auto; padding: 8px 0;">
            <img v-for="img in item.images" :key="img.id"
                 :src="getImageUrl(img.id, true)"
                 @click="currentImageId = img.id"
                 :style="{
                   width: '80px',
                   height: '80px',
                   objectFit: 'cover',
                   borderRadius: 'var(--border-radius)',
                   cursor: 'pointer',
                   border: img.id === currentImageId ? '3px solid var(--primary-color)' : 'none'
                 }" />
          </div>
        </div>

        <div class="grid grid-2">
          <div>
            <strong>Category:</strong> {{ item.category_name || 'None' }}
          </div>
          <div>
            <strong>Location:</strong> {{ item.location_name || 'None' }}
          </div>
          <div>
            <strong>Condition:</strong> {{ item.condition || 'Not specified' }}
          </div>
          <div>
            <strong>Quantity:</strong> {{ item.quantity }}
          </div>
        </div>

        <div v-if="item.description" style="margin-top: 16px;">
          <strong>Description:</strong>
          <p style="margin-top: 8px; color: var(--text-secondary);">{{ item.description }}</p>
        </div>

        <div class="grid grid-2" style="margin-top: 16px;">
          <div v-if="item.manufacturer">
            <strong>Manufacturer:</strong> {{ item.manufacturer }}
          </div>
          <div v-if="item.model_number">
            <strong>Model:</strong> {{ item.model_number }}
          </div>
          <div v-if="item.serial_number">
            <strong>Serial:</strong> {{ item.serial_number }}
          </div>
        </div>

        <div class="grid grid-2" style="margin-top: 16px;">
          <div v-if="item.purchase_price">
            <strong>Purchase Price:</strong> {{ formatCurrency(item.purchase_price) }}
          </div>
          <div v-if="item.current_value">
            <strong>Current Value:</strong> {{ formatCurrency(item.current_value) }}
          </div>
          <div v-if="item.purchase_date">
            <strong>Purchase Date:</strong> {{ formatDate(item.purchase_date) }}
          </div>
          <div v-if="item.warranty_expiration">
            <strong>Warranty Expires:</strong> {{ formatDate(item.warranty_expiration) }}
          </div>
        </div>

        <div v-if="item.notes" style="margin-top: 16px;">
          <strong>Notes:</strong>
          <p style="margin-top: 8px; color: var(--text-secondary); white-space: pre-wrap;">{{ item.notes }}</p>
        </div>
      </div>
    </div>

    <div v-else class="card">
      <p>Item not found</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'ItemDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const item = ref(null)
    const loading = ref(true)
    const editMode = ref(false)
    const currentImageId = ref(null)

    const loadItem = async () => {
      try {
        const { data } = await api.getItem(route.params.id)
        item.value = data
        if (data.images && data.images.length > 0) {
          currentImageId.value = data.images.find(img => img.is_primary)?.id || data.images[0].id
        }
      } catch (error) {
        console.error('Failed to load item:', error)
      } finally {
        loading.value = false
      }
    }

    const deleteItem = async () => {
      if (!confirm('Are you sure you want to delete this item?')) {
        return
      }

      try {
        await api.deleteItem(route.params.id)
        router.push('/items')
      } catch (error) {
        alert('Failed to delete item: ' + error.message)
      }
    }

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('nb-NO', {
        style: 'currency',
        currency: 'NOK'
      }).format(value)
    }

    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleDateString('nb-NO')
    }

    const getImageUrl = (imageId, thumbnail = false) => {
      return api.getImageUrl(imageId, thumbnail)
    }

    onMounted(loadItem)

    return {
      item,
      loading,
      editMode,
      currentImageId,
      deleteItem,
      formatCurrency,
      formatDate,
      getImageUrl
    }
  }
}
</script>
