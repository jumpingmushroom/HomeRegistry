<template>
  <div class="container">
    <h1 style="margin-bottom: 24px;">Items</h1>

    <div class="card">
      <input
        v-model="searchQuery"
        @input="search"
        class="input"
        placeholder="Search items..."
      />

      <div style="display: flex; gap: 12px; margin-top: 12px; flex-wrap: wrap;">
        <select v-model="filterCategory" @change="loadItems" class="select" style="flex: 1; min-width: 150px;">
          <option value="">All Categories</option>
          <option v-for="cat in flatCategories" :key="cat.id" :value="cat.id">
            {{ cat.indent }}{{ cat.name }}
          </option>
        </select>

        <select v-model="filterLocation" @change="loadItems" class="select" style="flex: 1; min-width: 150px;">
          <option value="">All Locations</option>
          <option v-for="loc in flatLocations" :key="loc.id" :value="loc.id">
            {{ loc.indent }}{{ loc.name }}
          </option>
        </select>

        <select v-model="filterCondition" @change="loadItems" class="select" style="flex: 1; min-width: 150px;">
          <option value="">All Conditions</option>
          <option value="new">New</option>
          <option value="excellent">Excellent</option>
          <option value="good">Good</option>
          <option value="fair">Fair</option>
          <option value="poor">Poor</option>
        </select>
      </div>
    </div>

    <!-- Batch Action Bar -->
    <div v-if="selectedItems.length > 0" class="batch-action-bar">
      <div class="batch-info">
        <input
          type="checkbox"
          :checked="allSelected"
          :indeterminate="someSelected && !allSelected"
          @change="toggleSelectAll"
          class="checkbox"
        />
        <span>{{ selectedItems.length }} item{{ selectedItems.length !== 1 ? 's' : '' }} selected</span>
      </div>
      <div class="batch-actions">
        <button @click="showBatchEditModal = true" class="btn btn-outline">
          Edit Selected
        </button>
        <button @click="showDeleteConfirmModal = true" class="btn btn-danger">
          Delete Selected
        </button>
        <button @click="clearSelection" class="btn btn-outline">
          Clear Selection
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else-if="items.length === 0" class="card">
      <p style="text-align: center; color: var(--text-secondary); padding: 40px;">
        No items found. Add your first item!
      </p>
    </div>

    <div v-else>
      <!-- Select All row when items exist but none selected -->
      <div v-if="selectedItems.length === 0" style="margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <input
          type="checkbox"
          @change="toggleSelectAll"
          class="checkbox"
        />
        <span style="color: var(--text-secondary); font-size: 14px;">Select all {{ items.length }} items</span>
      </div>

      <div class="grid grid-3">
        <div v-for="item in items" :key="item.id"
             class="card item-card"
             :class="{ 'item-selected': isSelected(item.id) }">
          <div class="item-checkbox" @click.stop>
            <input
              type="checkbox"
              :checked="isSelected(item.id)"
              @change="toggleSelect(item.id)"
              class="checkbox"
            />
          </div>
          <div @click="$router.push(`/items/${item.id}`)" style="cursor: pointer;">
            <div v-if="item.images && item.images.length > 0">
              <img :src="getImageUrl(item.images[0].id, true)"
                   style="width: 100%; height: 150px; object-fit: cover;" />
            </div>
            <div v-else style="width: 100%; height: 150px; background: var(--divider-color); display: flex; align-items: center; justify-content: center; font-size: 48px;">
              📦
            </div>
            <div style="padding: 12px;">
              <h3 style="font-size: 16px; margin-bottom: 4px;">{{ item.name }}</h3>
              <div style="font-size: 12px; color: var(--text-secondary);">
                {{ item.category_name || 'No category' }}
              </div>
              <div style="font-size: 12px; color: var(--text-secondary);">
                {{ item.location_name || 'No location' }}
              </div>
              <div v-if="item.current_value" style="font-size: 14px; font-weight: 600; margin-top: 8px;">
                {{ formatCurrency(item.current_value) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="totalPages > 1" style="display: flex; justify-content: center; gap: 8px; margin-top: 24px;">
      <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-outline">
        Previous
      </button>
      <span style="padding: 10px;">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-outline">
        Next
      </button>
    </div>

    <!-- Batch Edit Modal -->
    <div v-if="showBatchEditModal" class="modal-overlay" @click.self="showBatchEditModal = false">
      <div class="modal">
        <h2 style="margin-bottom: 16px;">Edit {{ selectedItems.length }} Item{{ selectedItems.length !== 1 ? 's' : '' }}</h2>
        <p style="color: var(--text-secondary); margin-bottom: 20px; font-size: 14px;">
          Only fields you change will be updated. Leave fields empty to keep existing values.
        </p>

        <div class="form-group">
          <label class="label">Location</label>
          <select v-model="batchEdit.location_id" class="select">
            <option value="">-- No change --</option>
            <option v-for="loc in flatLocations" :key="loc.id" :value="loc.id">
              {{ loc.indent }}{{ loc.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="label">Condition</label>
          <select v-model="batchEdit.condition" class="select">
            <option value="">-- No change --</option>
            <option value="new">New</option>
            <option value="excellent">Excellent</option>
            <option value="good">Good</option>
            <option value="fair">Fair</option>
            <option value="poor">Poor</option>
          </select>
        </div>

        <div class="form-group">
          <label class="label">Category</label>
          <select v-model="batchEdit.category_id" class="select">
            <option value="">-- No change --</option>
            <option v-for="cat in flatCategories" :key="cat.id" :value="cat.id">
              {{ cat.indent }}{{ cat.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="label">Property</label>
          <select v-model="batchEdit.property_id" class="select">
            <option value="">-- No change --</option>
            <option v-for="prop in properties" :key="prop.id" :value="prop.id">
              {{ prop.name }}
            </option>
          </select>
        </div>

        <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px;">
          <button @click="showBatchEditModal = false" class="btn btn-outline">Cancel</button>
          <button @click="executeBatchEdit" :disabled="batchEditLoading || !hasEditChanges" class="btn btn-primary">
            {{ batchEditLoading ? 'Updating...' : 'Update Items' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmModal" class="modal-overlay" @click.self="showDeleteConfirmModal = false">
      <div class="modal">
        <h2 style="margin-bottom: 16px; color: var(--danger-color);">Delete {{ selectedItems.length }} Item{{ selectedItems.length !== 1 ? 's' : '' }}?</h2>
        <p style="margin-bottom: 16px;">This action cannot be undone. The following items will be permanently deleted:</p>

        <div class="delete-item-list">
          <div v-for="itemId in selectedItems" :key="itemId" class="delete-item">
            {{ getItemName(itemId) }}
          </div>
        </div>

        <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px;">
          <button @click="showDeleteConfirmModal = false" class="btn btn-outline">Cancel</button>
          <button @click="executeBatchDelete" :disabled="batchDeleteLoading" class="btn btn-danger">
            {{ batchDeleteLoading ? 'Deleting...' : 'Delete Items' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject, watch } from 'vue'
import api from '../services/api'

export default {
  name: 'ItemsList',
  setup() {
    const items = ref([])
    const loading = ref(true)
    const searchQuery = ref('')
    const filterCategory = ref('')
    const filterLocation = ref('')
    const filterCondition = ref('')
    const currentPage = ref(1)
    const totalPages = ref(1)
    const pageSize = ref(30)
    const categories = ref([])
    const locations = ref([])
    const properties = ref([])
    const flatCategories = ref([])
    const flatLocations = ref([])
    const selectedPropertyId = inject('selectedPropertyId')

    // Selection state
    const selectedItems = ref([])

    // Batch edit state
    const showBatchEditModal = ref(false)
    const batchEditLoading = ref(false)
    const batchEdit = ref({
      location_id: '',
      condition: '',
      category_id: '',
      property_id: ''
    })

    // Batch delete state
    const showDeleteConfirmModal = ref(false)
    const batchDeleteLoading = ref(false)

    let searchTimeout = null

    // Computed
    const allSelected = computed(() => {
      return items.value.length > 0 && selectedItems.value.length === items.value.length
    })

    const someSelected = computed(() => {
      return selectedItems.value.length > 0
    })

    const hasEditChanges = computed(() => {
      return batchEdit.value.location_id ||
             batchEdit.value.condition ||
             batchEdit.value.category_id ||
             batchEdit.value.property_id
    })

    const loadItems = async () => {
      if (!selectedPropertyId.value) return
      loading.value = true
      try {
        const { data } = await api.getItems({
          skip: (currentPage.value - 1) * pageSize.value,
          limit: pageSize.value,
          search: searchQuery.value || undefined,
          property_id: selectedPropertyId.value,
          category_id: filterCategory.value || undefined,
          location_id: filterLocation.value || undefined,
          condition: filterCondition.value || undefined
        })
        items.value = data.items
        totalPages.value = Math.ceil(data.total / pageSize.value)
        // Clear selection when items change
        selectedItems.value = []
      } catch (error) {
        console.error('Failed to load items:', error)
      } finally {
        loading.value = false
      }
    }

    const loadFilters = async () => {
      if (!selectedPropertyId.value) return
      try {
        const [catRes, locRes, propRes] = await Promise.all([
          api.getCategories(),
          api.getLocations(selectedPropertyId.value),
          api.getProperties()
        ])
        categories.value = catRes.data
        locations.value = locRes.data
        properties.value = propRes.data
        flatCategories.value = flattenTree(catRes.data)
        flatLocations.value = flattenTree(locRes.data)
      } catch (error) {
        console.error('Failed to load categories/locations:', error)
      }
    }

    const search = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        currentPage.value = 1
        loadItems()
      }, 300)
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        loadItems()
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        loadItems()
      }
    }

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('nb-NO', {
        style: 'currency',
        currency: 'NOK'
      }).format(value)
    }

    const getImageUrl = (imageId, thumbnail = false) => {
      return api.getImageUrl(imageId, thumbnail)
    }

    const flattenTree = (items, indent = '') => {
      const result = []
      items.forEach(item => {
        result.push({ ...item, indent })
        if (item.children && item.children.length > 0) {
          result.push(...flattenTree(item.children, indent + '  '))
        }
      })
      return result
    }

    // Selection methods
    const isSelected = (itemId) => {
      return selectedItems.value.includes(itemId)
    }

    const toggleSelect = (itemId) => {
      const index = selectedItems.value.indexOf(itemId)
      if (index === -1) {
        selectedItems.value.push(itemId)
      } else {
        selectedItems.value.splice(index, 1)
      }
    }

    const toggleSelectAll = () => {
      if (allSelected.value) {
        selectedItems.value = []
      } else {
        selectedItems.value = items.value.map(item => item.id)
      }
    }

    const clearSelection = () => {
      selectedItems.value = []
    }

    const getItemName = (itemId) => {
      const item = items.value.find(i => i.id === itemId)
      return item ? item.name : 'Unknown item'
    }

    // Batch operations
    const executeBatchEdit = async () => {
      batchEditLoading.value = true
      try {
        const updates = {}
        if (batchEdit.value.location_id) updates.location_id = batchEdit.value.location_id
        if (batchEdit.value.condition) updates.condition = batchEdit.value.condition
        if (batchEdit.value.category_id) updates.category_id = batchEdit.value.category_id
        if (batchEdit.value.property_id) updates.property_id = batchEdit.value.property_id

        await api.batchUpdateItems(selectedItems.value, updates)

        showBatchEditModal.value = false
        batchEdit.value = { location_id: '', condition: '', category_id: '', property_id: '' }
        selectedItems.value = []
        await loadItems()
      } catch (error) {
        console.error('Failed to batch update items:', error)
        alert('Failed to update items. Please try again.')
      } finally {
        batchEditLoading.value = false
      }
    }

    const executeBatchDelete = async () => {
      batchDeleteLoading.value = true
      try {
        await api.batchDeleteItems(selectedItems.value)

        showDeleteConfirmModal.value = false
        selectedItems.value = []
        await loadItems()
      } catch (error) {
        console.error('Failed to batch delete items:', error)
        alert('Failed to delete items. Please try again.')
      } finally {
        batchDeleteLoading.value = false
      }
    }

    // Reload when property changes
    watch(selectedPropertyId, () => {
      filterLocation.value = ''
      currentPage.value = 1
      selectedItems.value = []
      loadFilters()
      loadItems()
    })

    onMounted(async () => {
      if (selectedPropertyId.value) {
        await loadFilters()
        loadItems()
      }
    })

    return {
      items,
      loading,
      searchQuery,
      filterCategory,
      filterLocation,
      filterCondition,
      currentPage,
      totalPages,
      flatCategories,
      flatLocations,
      properties,
      loadItems,
      search,
      prevPage,
      nextPage,
      formatCurrency,
      getImageUrl,
      // Selection
      selectedItems,
      allSelected,
      someSelected,
      isSelected,
      toggleSelect,
      toggleSelectAll,
      clearSelection,
      getItemName,
      // Batch edit
      showBatchEditModal,
      batchEditLoading,
      batchEdit,
      hasEditChanges,
      executeBatchEdit,
      // Batch delete
      showDeleteConfirmModal,
      batchDeleteLoading,
      executeBatchDelete
    }
  }
}
</script>

<style scoped>
.batch-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--primary-color);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
}

.batch-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.batch-action-bar .btn-outline {
  background: transparent;
  border-color: white;
  color: white;
}

.batch-action-bar .btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
}

.batch-action-bar .btn-danger {
  background: var(--danger-color);
  border-color: var(--danger-color);
}

.item-card {
  position: relative;
  padding: 0;
  overflow: hidden;
}

.item-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  background: white;
  border-radius: 4px;
  padding: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.item-selected {
  outline: 3px solid var(--primary-color);
  outline-offset: -3px;
}

.checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--primary-color);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: var(--card-bg);
  padding: 24px;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 16px;
}

.label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--text-primary);
}

.delete-item-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--divider-color);
  border-radius: 8px;
  padding: 8px;
}

.delete-item {
  padding: 8px 12px;
  border-bottom: 1px solid var(--divider-color);
  font-size: 14px;
}

.delete-item:last-child {
  border-bottom: none;
}

.btn-danger {
  background-color: var(--danger-color);
  color: white;
  border: none;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-danger:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
