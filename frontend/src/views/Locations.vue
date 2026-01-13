<template>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
      <h1>Locations</h1>
      <button @click="showAddModal = true" class="btn btn-primary">+ Add Location</button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else class="card">
      <div v-for="location in locations" :key="location.id">
        <LocationTreeItem
          :location="location"
          @edit="editLocation"
          @delete="deleteLocation"
        />
      </div>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <h2>Add Location</h2>
        <div class="form-group">
          <label class="label">Name *</label>
          <input v-model="newLocation.name" class="input" required />
        </div>
        <div class="form-group">
          <label class="label">Description</label>
          <textarea v-model="newLocation.description" class="textarea" rows="2"></textarea>
        </div>
        <div class="form-group">
          <label class="label">Type *</label>
          <select v-model="newLocation.location_type" class="select" required>
            <option value="home">Home</option>
            <option value="floor">Floor</option>
            <option value="room">Room</option>
            <option value="storage">Storage Unit</option>
          </select>
        </div>
        <div class="form-group">
          <label class="label">Parent Location</label>
          <select v-model="newLocation.parent_id" class="select">
            <option value="">None (Top Level)</option>
            <option v-for="loc in flatLocations" :key="loc.id" :value="loc.id">
              {{ loc.indent }}{{ loc.name }}
            </option>
          </select>
        </div>
        <div style="display: flex; gap: 12px;">
          <button @click="showAddModal = false" class="btn btn-outline">Cancel</button>
          <button @click="addLocation" class="btn btn-primary">Add</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'Locations',
  setup() {
    const locations = ref([])
    const loading = ref(true)
    const showAddModal = ref(false)
    const newLocation = ref({
      name: '',
      description: '',
      location_type: 'room',
      parent_id: ''
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

    const loadLocations = async () => {
      try {
        const { data } = await api.getLocations()
        locations.value = data
      } catch (error) {
        console.error('Failed to load locations:', error)
      } finally {
        loading.value = false
      }
    }

    const addLocation = async () => {
      try {
        await api.createLocation({
          ...newLocation.value,
          parent_id: newLocation.value.parent_id || null
        })
        showAddModal.value = false
        newLocation.value = { name: '', description: '', location_type: 'room', parent_id: '' }
        loadLocations()
      } catch (error) {
        alert('Failed to add location: ' + error.message)
      }
    }

    const editLocation = (location) => {
      // Simplified - just reload for now
      console.log('Edit location:', location)
    }

    const deleteLocation = async (locationId) => {
      if (!confirm('Are you sure you want to delete this location?')) {
        return
      }

      try {
        await api.deleteLocation(locationId)
        loadLocations()
      } catch (error) {
        alert('Failed to delete location: ' + error.message)
      }
    }

    onMounted(loadLocations)

    return {
      locations,
      loading,
      showAddModal,
      newLocation,
      flatLocations,
      addLocation,
      editLocation,
      deleteLocation
    }
  },
  components: {
    LocationTreeItem: {
      props: ['location'],
      emits: ['edit', 'delete'],
      template: `
        <div style="margin-bottom: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; border-bottom: 1px solid var(--divider-color);">
            <div>
              <strong>{{ location.name }}</strong>
              <span style="margin-left: 8px; font-size: 12px; color: var(--text-secondary);">
                ({{ location.location_type }}) • {{ location.item_count }} items
              </span>
            </div>
            <button @click="$emit('delete', location.id)" style="color: var(--error-color); background: none; border: none; cursor: pointer;">
              Delete
            </button>
          </div>
          <div v-if="location.children && location.children.length > 0" style="margin-left: 24px;">
            <LocationTreeItem
              v-for="child in location.children"
              :key="child.id"
              :location="child"
              @edit="$emit('edit', $event)"
              @delete="$emit('delete', $event)"
            />
          </div>
        </div>
      `
    }
  }
}
</script>

<style scoped>
/* Modal styles moved to global style.css for dark mode support */
</style>
