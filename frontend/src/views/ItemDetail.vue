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
          <h1 style="margin: 0;">{{ editMode ? 'Edit Item' : item.name }}</h1>
          <div style="display: flex; gap: 8px;">
            <button v-if="!editMode" @click="editMode = true" class="btn btn-outline">Edit</button>
            <button v-if="!editMode" @click="deleteItem" class="btn" style="background: var(--error-color); color: white;">Delete</button>
            <button v-if="editMode" @click="cancelEdit" class="btn btn-outline">Cancel</button>
            <button v-if="editMode" @click="saveItem" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>

        <!-- Edit Mode -->
        <div v-if="editMode">
          <div class="form-group">
            <label class="label">Item Name *</label>
            <input v-model="editForm.name" class="input" required />
          </div>

          <div class="form-group">
            <label class="label">Description</label>
            <textarea v-model="editForm.description" class="textarea" rows="3"></textarea>
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label class="label">Category</label>
              <select v-model="editForm.category_id" class="select">
                <option value="">Select category</option>
                <option v-for="cat in flatCategories" :key="cat.id" :value="cat.id">
                  {{ cat.indent }}{{ cat.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="label">Location</label>
              <select v-model="editForm.location_id" class="select">
                <option value="">Select location</option>
                <option v-for="loc in flatLocations" :key="loc.id" :value="loc.id">
                  {{ loc.indent }}{{ loc.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label class="label">Manufacturer</label>
              <input v-model="editForm.manufacturer" class="input" />
            </div>

            <div class="form-group">
              <label class="label">Model Number</label>
              <input v-model="editForm.model_number" class="input" />
            </div>
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label class="label">Serial Number</label>
              <input v-model="editForm.serial_number" class="input" />
            </div>

            <div class="form-group">
              <label class="label">Condition</label>
              <select v-model="editForm.condition" class="select">
                <option value="">Select condition</option>
                <option value="new">New</option>
                <option value="excellent">Excellent</option>
                <option value="good">Good</option>
                <option value="fair">Fair</option>
                <option value="poor">Poor</option>
              </select>
            </div>
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label class="label">Quantity</label>
              <input v-model.number="editForm.quantity" type="number" class="input" />
            </div>
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label class="label">Purchase Price (NOK)</label>
              <input v-model.number="editForm.purchase_price" type="number" step="0.01" class="input" />
            </div>

            <div class="form-group">
              <label class="label">Current Value (NOK)</label>
              <input v-model.number="editForm.current_value" type="number" step="0.01" class="input" />
            </div>
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label class="label">Purchase Date</label>
              <input v-model="editForm.purchase_date" type="date" class="input" />
            </div>

            <div class="form-group">
              <label class="label">Warranty Expiration</label>
              <input v-model="editForm.warranty_expiration" type="date" class="input" />
            </div>
          </div>

          <div class="form-group">
            <label class="label">Notes</label>
            <textarea v-model="editForm.notes" class="textarea" rows="3"></textarea>
          </div>
        </div>

        <!-- View Mode -->

        <!-- View Mode -->
        <div v-else>
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
        <!-- End View Mode -->
      </div>
    </div>

    <div v-else class="card">
      <p>Item not found</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
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
    const saving = ref(false)
    const currentImageId = ref(null)
    const categories = ref([])
    const locations = ref([])
    const editForm = ref({
      name: '',
      description: '',
      category_id: '',
      location_id: '',
      manufacturer: '',
      model_number: '',
      serial_number: '',
      condition: '',
      quantity: 1,
      purchase_price: null,
      current_value: null,
      purchase_date: '',
      warranty_expiration: '',
      notes: ''
    })

    const flatCategories = computed(() => {
      const flatten = (cats, indent = '') => {
        const result = []
        cats.forEach(cat => {
          result.push({ ...cat, indent })
          if (cat.children && cat.children.length > 0) {
            result.push(...flatten(cat.children, indent + '  '))
          }
        })
        return result
      }
      return flatten(categories.value)
    })

    const flatLocations = computed(() => {
      const flatten = (locs, indent = '') => {
        const result = []
        locs.forEach(loc => {
          result.push({ ...loc, indent })
          if (loc.children && loc.children.length > 0) {
            result.push(...flatten(loc.children, indent + '  '))
          }
        })
        return result
      }
      return flatten(locations.value)
    })

    const loadItem = async () => {
      try {
        const { data } = await api.getItem(route.params.id)
        item.value = data
        if (data.images && data.images.length > 0) {
          currentImageId.value = data.images.find(img => img.is_primary)?.id || data.images[0].id
        }

        // Initialize edit form with current data
        editForm.value = {
          name: data.name || '',
          description: data.description || '',
          category_id: data.category_id || '',
          location_id: data.location_id || '',
          manufacturer: data.manufacturer || '',
          model_number: data.model_number || '',
          serial_number: data.serial_number || '',
          condition: data.condition || '',
          quantity: data.quantity || 1,
          purchase_price: data.purchase_price || null,
          current_value: data.current_value || null,
          purchase_date: data.purchase_date || '',
          warranty_expiration: data.warranty_expiration || '',
          notes: data.notes || ''
        }
      } catch (error) {
        console.error('Failed to load item:', error)
      } finally {
        loading.value = false
      }
    }

    const loadCategories = async () => {
      try {
        const { data } = await api.getCategories()
        categories.value = data
      } catch (error) {
        console.error('Failed to load categories:', error)
      }
    }

    const loadLocations = async () => {
      try {
        const { data } = await api.getLocations()
        locations.value = data
      } catch (error) {
        console.error('Failed to load locations:', error)
      }
    }

    const saveItem = async () => {
      saving.value = true
      try {
        await api.updateItem(route.params.id, editForm.value)
        await loadItem()
        editMode.value = false
      } catch (error) {
        alert('Failed to save item: ' + error.message)
      } finally {
        saving.value = false
      }
    }

    const cancelEdit = () => {
      editMode.value = false
      // Reset form to current item data
      editForm.value = {
        name: item.value.name || '',
        description: item.value.description || '',
        category_id: item.value.category_id || '',
        location_id: item.value.location_id || '',
        manufacturer: item.value.manufacturer || '',
        model_number: item.value.model_number || '',
        serial_number: item.value.serial_number || '',
        condition: item.value.condition || '',
        quantity: item.value.quantity || 1,
        purchase_price: item.value.purchase_price || null,
        current_value: item.value.current_value || null,
        purchase_date: item.value.purchase_date || '',
        warranty_expiration: item.value.warranty_expiration || '',
        notes: item.value.notes || ''
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

    onMounted(() => {
      loadItem()
      loadCategories()
      loadLocations()
    })

    return {
      item,
      loading,
      editMode,
      saving,
      currentImageId,
      editForm,
      categories,
      locations,
      flatCategories,
      flatLocations,
      deleteItem,
      saveItem,
      cancelEdit,
      formatCurrency,
      formatDate,
      getImageUrl
    }
  }
}
</script>
