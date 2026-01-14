<template>
  <div class="container">
    <h1 style="margin-bottom: 24px;">Add New Item</h1>

    <div class="card">
      <h3 style="margin-bottom: 16px;">📸 Capture or Upload Photos</h3>

      <div style="display: flex; gap: 12px; margin-bottom: 16px;">
        <button @click="openCamera" class="btn btn-primary">
          📷 Take Photo
        </button>
        <label class="btn btn-outline">
          📁 Upload from Gallery
          <input type="file" multiple accept="image/*" @change="handleFileSelect" style="display: none;" />
        </label>
      </div>

      <div v-if="selectedFiles.length > 0" class="grid grid-3">
        <div v-for="(file, index) in selectedFiles" :key="index" style="position: relative;">
          <img :src="file.preview" style="width: 100%; height: 150px; object-fit: cover; border-radius: var(--border-radius);" />
          <button @click="removeFile(index)"
                  style="position: absolute; top: 8px; right: 8px; background: var(--error-color); color: white; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer;">
            ×
          </button>
        </div>
      </div>

      <button v-if="selectedFiles.length > 0 && !analyzing && !analysisResult"
              @click="analyzeWithAI"
              class="btn btn-primary"
              style="width: 100%; margin-top: 16px;">
        🤖 Analyze with AI
      </button>

      <div v-if="analyzing" class="loading">
        <div class="spinner"></div>
        <div style="margin-left: 16px;">Analyzing images...</div>
      </div>

      <div v-if="analysisError" class="error-message">
        {{ analysisError }}
      </div>
    </div>

    <div v-if="analysisResult" class="card" style="margin-top: 16px;">
      <h3 style="margin-bottom: 16px;">✨ AI Analysis Results</h3>
      <small style="color: var(--text-secondary);">Review and edit the information below</small>

      <div class="form-group" style="margin-top: 16px;">
        <label class="label">Item Name *</label>
        <input v-model="form.name" class="input" required />
      </div>

      <div class="form-group">
        <label class="label">Description</label>
        <textarea v-model="form.description" class="textarea" rows="3"></textarea>
      </div>

      <div class="grid grid-2">
        <div class="form-group">
          <label class="label">Category</label>
          <select v-model="form.category_id" class="select">
            <option value="">Select category</option>
            <option v-for="cat in flatCategories" :key="cat.id" :value="cat.id">
              {{ cat.indent }}{{ cat.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="label">Location</label>
          <select v-model="form.location_id" class="select">
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
          <input v-model="form.manufacturer" class="input" />
        </div>

        <div class="form-group">
          <label class="label">Model Number</label>
          <input v-model="form.model_number" class="input" />
        </div>
      </div>

      <div class="grid grid-2">
        <div class="form-group">
          <label class="label">Serial Number</label>
          <input v-model="form.serial_number" class="input" />
        </div>

        <div class="form-group">
          <label class="label">Barcode/UPC</label>
          <input v-model="form.barcode" class="input" />
        </div>
      </div>

      <div class="grid grid-2">
        <div class="form-group">
          <label class="label">Condition</label>
          <select v-model="form.condition" class="select">
            <option value="">Select condition</option>
            <option value="new">New</option>
            <option value="excellent">Excellent</option>
            <option value="good">Good</option>
            <option value="fair">Fair</option>
            <option value="poor">Poor</option>
          </select>
        </div>

        <div class="form-group">
          <label class="label">Purchase Location</label>
          <input v-model="form.purchase_location" class="input" />
        </div>
      </div>

      <div class="grid grid-2">
        <div class="form-group">
          <label class="label">Purchase Price (NOK)</label>
          <input v-model.number="form.purchase_price" type="number" step="0.01" class="input" />
        </div>

        <div class="form-group">
          <label class="label">Current Value (NOK)</label>
          <input v-model.number="form.current_value" type="number" step="0.01" class="input" />
        </div>
      </div>

      <div class="grid grid-2">
        <div class="form-group">
          <label class="label">Purchase Date</label>
          <input v-model="form.purchase_date" type="date" class="input" />
        </div>

        <div class="form-group">
          <label class="label">Warranty Expiration</label>
          <input v-model="form.warranty_expiration" type="date" class="input" />
        </div>
      </div>

      <div class="form-group">
        <label class="label">Notes</label>
        <textarea v-model="form.notes" class="textarea" rows="3"></textarea>
      </div>

      <div class="form-group">
        <label class="label">Tags</label>
        <input v-model="tagsInput" @input="updateTags" class="input" placeholder="Enter tags separated by commas" />
        <small style="color: var(--text-secondary); display: block; margin-top: 4px;">
          Separate multiple tags with commas (e.g., electronics, warranty, fragile)
        </small>
      </div>

      <button @click="saveItem" class="btn btn-primary" :disabled="saving || !form.name">
        {{ saving ? 'Saving...' : 'Save Item' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'AddItem',
  setup() {
    const router = useRouter()
    const selectedPropertyId = inject('selectedPropertyId')
    const selectedFiles = ref([])
    const analyzing = ref(false)
    const analysisResult = ref(null)
    const analysisError = ref(null)
    const saving = ref(false)
    const categories = ref([])
    const locations = ref([])
    const flatCategories = ref([])
    const flatLocations = ref([])
    const tagsInput = ref('')

    const form = ref({
      name: '',
      description: '',
      property_id: '',
      category_id: '',
      location_id: '',
      manufacturer: '',
      model_number: '',
      serial_number: '',
      barcode: '',
      condition: '',
      purchase_price: null,
      purchase_location: '',
      current_value: null,
      purchase_date: null,
      warranty_expiration: null,
      tags: [],
      notes: '',
      ai_metadata: null
    })

    const openCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        // For simplicity, we'll use file input. Full camera implementation would need canvas capture
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = 'image/*'
        input.capture = 'environment'
        input.onchange = (e) => handleFileSelect(e)
        input.click()
      } catch (error) {
        // Fallback to file input
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = 'image/*'
        input.capture = 'environment'
        input.onchange = (e) => handleFileSelect(e)
        input.click()
      }
    }

    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      files.forEach(file => {
        const reader = new FileReader()
        reader.onload = (e) => {
          selectedFiles.value.push({
            file,
            preview: e.target.result
          })
        }
        reader.readAsDataURL(file)
      })
    }

    const removeFile = (index) => {
      selectedFiles.value.splice(index, 1)
    }

    const updateTags = () => {
      // Convert comma-separated string to array
      form.value.tags = tagsInput.value
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)
    }

    const analyzeWithAI = async () => {
      analyzing.value = true
      analysisError.value = null

      try {
        const files = selectedFiles.value.map(f => f.file)
        const { data } = await api.analyzeImages(files)

        if (data.success && data.analysis) {
          analysisResult.value = data.analysis

          // Pre-fill form with AI results
          form.value.name = data.analysis.item_name || ''
          form.value.description = data.analysis.description || ''
          form.value.manufacturer = data.analysis.manufacturer || ''
          form.value.model_number = data.analysis.model_number || ''
          form.value.serial_number = data.analysis.serial_number || ''
          form.value.barcode = data.analysis.barcode || ''
          form.value.condition = data.analysis.condition || ''
          form.value.purchase_location = data.analysis.purchase_location || ''
          form.value.current_value = data.analysis.estimated_value_nok || null
          form.value.ai_metadata = data.analysis

          // Handle tags
          if (data.analysis.tags && Array.isArray(data.analysis.tags)) {
            form.value.tags = data.analysis.tags
            tagsInput.value = data.analysis.tags.join(', ')
          }

          // Find matching category
          const categoryName = data.analysis.category
          const matchingCategory = findCategoryByName(categoryName)
          if (matchingCategory) {
            form.value.category_id = matchingCategory.id
          }

          // Find matching location
          const locationName = data.analysis.suggested_location
          if (locationName) {
            const matchingLocation = findLocationByName(locationName)
            if (matchingLocation) {
              form.value.location_id = matchingLocation.id
            }
          }
        } else {
          analysisError.value = data.error || 'Analysis failed'
        }
      } catch (error) {
        analysisError.value = 'Failed to analyze images: ' + error.message
      } finally {
        analyzing.value = false
      }
    }

    const findCategoryByName = (name) => {
      const search = (cats) => {
        for (const cat of cats) {
          if (cat.name.toLowerCase() === name.toLowerCase()) {
            return cat
          }
          if (cat.children) {
            const found = search(cat.children)
            if (found) return found
          }
        }
        return null
      }
      return search(categories.value)
    }

    const findLocationByName = (name) => {
      const search = (locs) => {
        for (const loc of locs) {
          if (loc.name.toLowerCase().includes(name.toLowerCase())) {
            return loc
          }
          if (loc.children) {
            const found = search(loc.children)
            if (found) return found
          }
        }
        return null
      }
      return search(locations.value)
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

    const saveItem = async () => {
      if (!form.value.name) {
        alert('Please enter an item name')
        return
      }

      saving.value = true

      try {
        // Create item with selected property
        const { data: item } = await api.createItem({
          ...form.value,
          property_id: selectedPropertyId.value,
          category_id: form.value.category_id || null,
          location_id: form.value.location_id || null
        })

        // Upload images
        for (const file of selectedFiles.value) {
          await api.addItemImage(item.id, file.file)
        }

        router.push(`/items/${item.id}`)
      } catch (error) {
        alert('Failed to save item: ' + error.message)
      } finally {
        saving.value = false
      }
    }

    const loadLocations = async () => {
      if (!selectedPropertyId.value) return
      try {
        const { data } = await api.getLocations(selectedPropertyId.value)
        locations.value = data
        flatLocations.value = flattenTree(data)
      } catch (error) {
        console.error('Failed to load locations:', error)
      }
    }

    // Reload locations when property changes
    watch(selectedPropertyId, () => {
      form.value.location_id = ''
      loadLocations()
    })

    onMounted(async () => {
      try {
        const { data: catData } = await api.getCategories()
        categories.value = catData
        flatCategories.value = flattenTree(catData)

        if (selectedPropertyId.value) {
          await loadLocations()
        }
      } catch (error) {
        console.error('Failed to load categories/locations:', error)
      }
    })

    return {
      selectedFiles,
      analyzing,
      analysisResult,
      analysisError,
      saving,
      form,
      flatCategories,
      flatLocations,
      tagsInput,
      openCamera,
      handleFileSelect,
      removeFile,
      analyzeWithAI,
      updateTags,
      saveItem
    }
  }
}
</script>
