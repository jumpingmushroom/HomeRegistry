<template>
  <div class="container">
    <h1 style="margin-bottom: 24px;">Items</h1>

    <div class="card">
      <input
        v-model="searchQuery"
        @input="search"
        class="input"
        placeholder="🔍 Search items..."
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

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else-if="items.length === 0" class="card">
      <p style="text-align: center; color: var(--text-secondary); padding: 40px;">
        No items found. Add your first item!
      </p>
    </div>

    <div v-else class="grid grid-3">
      <div v-for="item in items" :key="item.id"
           @click="$router.push(`/items/${item.id}`)"
           class="card"
           style="cursor: pointer; padding: 0; overflow: hidden;">
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

    <div v-if="totalPages > 1" style="display: flex; justify-content: center; gap: 8px; margin-top: 24px;">
      <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-outline">
        Previous
      </button>
      <span style="padding: 10px;">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-outline">
        Next
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, inject, watch } from 'vue'
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
    const flatCategories = ref([])
    const flatLocations = ref([])
    const selectedPropertyId = inject('selectedPropertyId')

    let searchTimeout = null

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
      } catch (error) {
        console.error('Failed to load items:', error)
      } finally {
        loading.value = false
      }
    }

    const loadFilters = async () => {
      if (!selectedPropertyId.value) return
      try {
        const [catRes, locRes] = await Promise.all([
          api.getCategories(),
          api.getLocations(selectedPropertyId.value)
        ])
        categories.value = catRes.data
        locations.value = locRes.data
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

    // Reload when property changes
    watch(selectedPropertyId, () => {
      filterLocation.value = ''
      currentPage.value = 1
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
      loadItems,
      search,
      prevPage,
      nextPage,
      formatCurrency,
      getImageUrl
    }
  }
}
</script>
