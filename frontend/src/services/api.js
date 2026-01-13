import axios from 'axios'

const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  // Health
  health() {
    return api.get('/health')
  },

  // Settings
  getSettings() {
    return api.get('/settings')
  },

  updateSettings(settings) {
    return api.put('/settings', settings)
  },

  testAI(provider, apiKey, endpoint) {
    return api.post('/settings/test-ai', {
      provider,
      api_key: apiKey,
      endpoint
    })
  },

  // Locations
  getLocations() {
    return api.get('/locations')
  },

  createLocation(location) {
    return api.post('/locations', location)
  },

  updateLocation(id, location) {
    return api.put(`/locations/${id}`, location)
  },

  deleteLocation(id) {
    return api.delete(`/locations/${id}`)
  },

  // Categories
  getCategories() {
    return api.get('/categories')
  },

  createCategory(category) {
    return api.post('/categories', category)
  },

  updateCategory(id, category) {
    return api.put(`/categories/${id}`, category)
  },

  deleteCategory(id) {
    return api.delete(`/categories/${id}`)
  },

  // Items
  getItems(params = {}) {
    return api.get('/items', { params })
  },

  getItem(id) {
    return api.get(`/items/${id}`)
  },

  createItem(item) {
    return api.post('/items', item)
  },

  updateItem(id, item) {
    return api.put(`/items/${id}`, item)
  },

  deleteItem(id) {
    return api.delete(`/items/${id}`)
  },

  analyzeImages(files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    return api.post('/items/analyze-images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  addItemImage(itemId, file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/items/${itemId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // Images
  deleteImage(id) {
    return api.delete(`/images/${id}`)
  },

  setPrimaryImage(id) {
    return api.put(`/images/${id}/primary`)
  },

  getImageUrl(id, thumbnail = false) {
    return `${API_BASE}/images/${id}/file${thumbnail ? '?thumbnail=true' : ''}`
  },

  // Documents
  uploadDocument(itemId, file, documentType) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('document_type', documentType)
    return api.post(`/items/${itemId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  getDocumentUrl(id) {
    return `${API_BASE}/documents/${id}`
  },

  deleteDocument(id) {
    return api.delete(`/documents/${id}`)
  },

  // Dashboard
  getDashboardStats() {
    return api.get('/dashboard/stats')
  }
}
