import axios from 'axios'

const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear it
      localStorage.removeItem('token')
      // Redirect to login if not already there
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default {
  // Auth
  login(username, password) {
    return api.post('/auth/login', { username, password })
  },

  register(username, password, email = null) {
    return api.post('/auth/register', { username, password, email })
  },

  getMe() {
    return api.get('/auth/me')
  },

  updateMe(data) {
    return api.put('/auth/me', data)
  },

  getAuthStatus() {
    return api.get('/auth/status')
  },

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
  getLocations(propertyId = null) {
    const params = propertyId ? { property_id: propertyId } : {}
    return api.get('/locations', { params })
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

  batchUpdateItems(itemIds, updates) {
    return api.post('/items/batch-update', {
      item_ids: itemIds,
      ...updates
    })
  },

  batchDeleteItems(itemIds) {
    return api.post('/items/batch-delete', {
      item_ids: itemIds
    })
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
  getDashboardStats(propertyId = null) {
    const params = propertyId ? { property_id: propertyId } : {}
    return api.get('/dashboard/stats', { params })
  },

  // Properties
  getProperties() {
    return api.get('/properties')
  },

  getProperty(id) {
    return api.get(`/properties/${id}`)
  },

  createProperty(property) {
    return api.post('/properties', property)
  },

  updateProperty(id, property) {
    return api.put(`/properties/${id}`, property)
  },

  deleteProperty(id) {
    return api.delete(`/properties/${id}`)
  },

  // Insurance Policies
  getInsurancePolicies(propertyId = null) {
    const params = propertyId ? { property_id: propertyId } : {}
    return api.get('/insurance-policies', { params })
  },

  getInsurancePolicy(id) {
    return api.get(`/insurance-policies/${id}`)
  },

  createInsurancePolicy(policy) {
    return api.post('/insurance-policies', policy)
  },

  updateInsurancePolicy(id, policy) {
    return api.put(`/insurance-policies/${id}`, policy)
  },

  deleteInsurancePolicy(id) {
    return api.delete(`/insurance-policies/${id}`)
  },

  // Reports
  getInsuranceReportUrl(propertyId) {
    return `${API_BASE}/reports/insurance/${propertyId}`
  },

  // Public (no auth required)
  getPublicItem(id) {
    return api.get(`/public/items/${id}`)
  },

  // QR Code
  getItemQrCodeUrl(id, baseUrl = null) {
    const params = baseUrl ? `?base_url=${encodeURIComponent(baseUrl)}` : ''
    return `${API_BASE}/items/${id}/qr${params}`
  },

  // Backups
  getBackupStatus() {
    return api.get('/backup/status')
  },

  listBackups() {
    return api.get('/backup/list')
  },

  createBackup() {
    return api.post('/backup/create')
  },

  downloadBackup(filename) {
    return api.get(`/backup/download/${filename}`, {
      responseType: 'blob'
    })
  },

  downloadCurrentDatabase() {
    return api.get('/backup/download-current', {
      responseType: 'blob'
    })
  },

  runBackupCleanup() {
    return api.delete('/backup/cleanup')
  },

  exportAllData() {
    return api.get('/backup/export', {
      responseType: 'blob'
    })
  }
}
