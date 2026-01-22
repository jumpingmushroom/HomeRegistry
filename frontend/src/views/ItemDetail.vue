<template>
  <div class="container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else-if="item">
      <button @click="$router.push('/items')" class="btn btn-outline" style="margin-bottom: 16px; display: flex; align-items: center; gap: 6px;">
        <ArrowLeft :size="18" />
        <span>Back to Items</span>
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
              <label class="label">Barcode/UPC</label>
              <input v-model="editForm.barcode" class="input" />
            </div>
          </div>

          <div class="grid grid-2">
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

            <div class="form-group">
              <label class="label">Purchase Location</label>
              <input v-model="editForm.purchase_location" class="input" />
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

          <div class="form-group">
            <label class="label">Tags</label>
            <input v-model="editTagsInput" @input="updateEditTags" class="input" placeholder="Enter tags separated by commas" />
            <small style="color: var(--text-secondary); display: block; margin-top: 4px;">
              Separate multiple tags with commas (e.g., electronics, warranty, fragile)
            </small>
          </div>

          <!-- Images Section in Edit Mode -->
          <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--border-color);">
            <h3 style="margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
              <ImageIcon :size="20" />
              <span>Images</span>
            </h3>

            <div v-if="item.images && item.images.length > 0" style="margin-bottom: 16px;">
              <div style="display: flex; flex-wrap: wrap; gap: 12px;">
                <div v-for="img in item.images" :key="img.id"
                     style="position: relative; width: 120px;">
                  <img :src="getImageUrl(img.id, true)"
                       style="width: 120px; height: 120px; object-fit: cover; border-radius: var(--border-radius);" />
                  <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                    <button
                      @click="setImageAsPrimary(img.id)"
                      class="btn btn-outline"
                      :style="{
                        padding: '4px 8px',
                        fontSize: '12px',
                        background: img.is_primary ? 'var(--primary-color)' : 'transparent',
                        color: img.is_primary ? 'white' : 'var(--text-primary)',
                        border: img.is_primary ? 'none' : '1px solid var(--border-color)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }"
                      :disabled="img.is_primary"
                      :title="img.is_primary ? 'Primary image' : 'Set as primary'">
                      <Star :size="14" :fill="img.is_primary ? 'currentColor' : 'none'" />
                    </button>
                    <button
                      @click="deleteImage(img.id)"
                      class="btn"
                      style="padding: 4px 8px; font-size: 12px; background: var(--error-color); color: white; border: none; display: flex; align-items: center; justify-content: center;"
                      title="Delete image">
                      <X :size="14" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else style="margin-bottom: 16px; color: var(--text-secondary);">
              No images uploaded yet.
            </div>

            <div class="form-group">
              <label class="btn btn-primary" style="margin: 0; display: inline-block;">
                + Add Image
                <input type="file" @change="handleImageSelect" accept="image/jpeg,image/png,image/webp" style="display: none;" />
              </label>
              <small style="color: var(--text-secondary); display: block; margin-top: 8px;">
                Supported: JPG, PNG, WebP (max 20MB)
              </small>
            </div>
          </div>

          <!-- Documents Section in Edit Mode -->
          <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--border-color);">
            <h3 style="margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
              <Paperclip :size="20" />
              <span>Documents</span>
            </h3>

            <div v-if="item.documents && item.documents.length > 0" style="margin-bottom: 16px;">
              <div v-for="doc in item.documents" :key="doc.id"
                   style="display: flex; justify-content: space-between; align-items: center; padding: 12px; margin-bottom: 8px; background: var(--surface-hover); border-radius: var(--border-radius);">
                <div style="flex: 1;">
                  <a :href="getDocumentUrl(doc.id)" target="_blank" style="font-weight: 500; color: var(--primary-color);">
                    {{ doc.original_filename }}
                  </a>
                  <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                    {{ formatDocumentType(doc.document_type) }} • {{ formatFileSize(doc.file_size) }}
                  </div>
                </div>
                <button @click="deleteDocument(doc.id)" class="btn btn-outline" style="padding: 6px 12px; font-size: 12px; background: var(--error-color); color: white; border: none;">
                  Delete
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="label">Add Document</label>
              <div style="display: flex; gap: 12px; align-items: end;">
                <div style="flex: 1;">
                  <select v-model="newDocumentType" class="select">
                    <option value="receipt">Receipt</option>
                    <option value="manual">Manual</option>
                    <option value="warranty">Warranty</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <label class="btn btn-primary" style="margin: 0;">
                  Choose File
                  <input type="file" @change="handleDocumentSelect" accept=".pdf,.jpg,.jpeg,.png" style="display: none;" />
                </label>
              </div>
              <small style="color: var(--text-secondary); display: block; margin-top: 8px;">
                Supported: PDF, JPG, PNG (max 50MB)
              </small>
            </div>
          </div>
        </div>

        <!-- View Mode -->

        <!-- View Mode -->
        <div v-else>
        <div v-if="item.images && item.images.length > 0" style="margin-bottom: 16px;">
          <div style="width: 100%; max-width: 600px; margin: 0 auto;">
            <img :src="getImageUrl(currentImageId)"
                 @click="openImageViewer(item.images.findIndex(img => img.id === currentImageId))"
                 style="width: 100%; border-radius: var(--border-radius); cursor: pointer;"
                 title="Click to view larger" />
          </div>
          <div style="display: flex; gap: 8px; margin-top: 12px; overflow-x: auto; padding: 8px 0;">
            <img v-for="(img, idx) in item.images" :key="img.id"
                 :src="getImageUrl(img.id, true)"
                 @click="currentImageId = img.id"
                 @dblclick="openImageViewer(idx)"
                 :style="{
                   width: '80px',
                   height: '80px',
                   objectFit: 'cover',
                   borderRadius: 'var(--border-radius)',
                   cursor: 'pointer',
                   border: img.id === currentImageId ? '3px solid var(--primary-color)' : 'none'
                 }"
                 title="Click to select, double-click to view larger" />
          </div>
        </div>

        <!-- Image Viewer Modal -->
        <ImageViewer
          v-model="imageViewerOpen"
          :images="item.images || []"
          :start-index="imageViewerStartIndex"
        />

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
          <div v-if="item.barcode">
            <strong>Barcode/UPC:</strong> {{ item.barcode }}
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
          <div v-if="item.purchase_location">
            <strong>Purchase Location:</strong> {{ item.purchase_location }}
          </div>
          <div v-if="item.warranty_expiration">
            <strong>Warranty Expires:</strong> {{ formatDate(item.warranty_expiration) }}
          </div>
        </div>

        <div v-if="item.notes" style="margin-top: 16px;">
          <strong>Notes:</strong>
          <p style="margin-top: 8px; color: var(--text-secondary); white-space: pre-wrap;">{{ item.notes }}</p>
        </div>

        <div v-if="item.tags && item.tags.length > 0" style="margin-top: 16px;">
          <strong>Tags:</strong>
          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
            <span v-for="tag in item.tags" :key="tag"
                  style="padding: 4px 12px; background: var(--primary-color); color: white; border-radius: 16px; font-size: 14px;">
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- Documents Section in View Mode -->
        <div v-if="item.documents && item.documents.length > 0" style="margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--border-color);">
          <h3 style="margin-bottom: 16px;">Attached Documents</h3>
          <div class="grid grid-2">
            <a v-for="doc in item.documents" :key="doc.id"
               :href="getDocumentUrl(doc.id)"
               target="_blank"
               style="display: flex; align-items: center; padding: 12px; background: var(--surface-hover); border-radius: var(--border-radius); text-decoration: none; color: var(--text-primary);">
              <div style="margin-right: 12px; color: var(--text-secondary);">
                <ImageIcon v-if="doc.mime_type && doc.mime_type.startsWith('image/')" :size="32" />
                <FileText v-else-if="doc.mime_type === 'application/pdf'" :size="32" />
                <Receipt v-else-if="doc.document_type === 'receipt'" :size="32" />
                <BookOpen v-else-if="doc.document_type === 'manual'" :size="32" />
                <Shield v-else-if="doc.document_type === 'warranty'" :size="32" />
                <Paperclip v-else :size="32" />
              </div>
              <div style="flex: 1; min-width: 0;">
                <div style="font-weight: 500; color: var(--primary-color); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  {{ doc.original_filename }}
                </div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                  {{ formatDocumentType(doc.document_type) }} • {{ formatFileSize(doc.file_size) }}
                </div>
              </div>
            </a>
          </div>
        </div>

        <!-- QR Code Section -->
        <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--border-color);">
          <h3 style="margin-bottom: 16px;">QR Code</h3>
          <div style="display: flex; gap: 24px; align-items: start; flex-wrap: wrap;">
            <div style="background: white; padding: 16px; border-radius: var(--border-radius); display: inline-block;">
              <img :src="getQrCodeUrl()" alt="Item QR Code" style="width: 150px; height: 150px;" />
            </div>
            <div style="flex: 1; min-width: 200px;">
              <p style="color: var(--text-secondary); margin-bottom: 12px; font-size: 14px;">
                Scan this QR code to quickly look up this item. Print and attach it to the physical item for easy identification.
              </p>
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <a :href="getQrCodeUrl()" download :download="'qr_' + item.id + '.png'" class="btn btn-primary">
                  Download QR Code
                </a>
                <button @click="copyPublicLink" class="btn btn-outline">
                  Copy Link
                </button>
              </div>
              <div v-if="linkCopied" style="color: var(--primary-color); font-size: 12px; margin-top: 8px;">
                Link copied to clipboard!
              </div>
            </div>
          </div>
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
import { ref, computed, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import ImageViewer from '../components/ImageViewer.vue'
import { ArrowLeft, ImageIcon, Paperclip, Star, X, FileText, Receipt, BookOpen, Shield } from 'lucide-vue-next'

export default {
  name: 'ItemDetail',
  components: {
    ImageViewer,
    ArrowLeft,
    ImageIcon,
    Paperclip,
    Star,
    X,
    FileText,
    Receipt,
    BookOpen,
    Shield
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const selectedPropertyId = inject('selectedPropertyId')
    const item = ref(null)
    const loading = ref(true)
    const editMode = ref(false)
    const saving = ref(false)
    const currentImageId = ref(null)
    const categories = ref([])
    const locations = ref([])
    const newDocumentType = ref('receipt')
    const uploadingDocument = ref(false)
    const linkCopied = ref(false)
    const imageViewerOpen = ref(false)
    const imageViewerStartIndex = ref(0)
    const editForm = ref({
      name: '',
      description: '',
      category_id: '',
      location_id: '',
      manufacturer: '',
      model_number: '',
      serial_number: '',
      barcode: '',
      condition: '',
      quantity: 1,
      purchase_price: null,
      purchase_location: '',
      current_value: null,
      purchase_date: '',
      warranty_expiration: '',
      tags: [],
      notes: ''
    })
    const editTagsInput = ref('')

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
          barcode: data.barcode || '',
          condition: data.condition || '',
          quantity: data.quantity || 1,
          purchase_price: data.purchase_price || null,
          purchase_location: data.purchase_location || '',
          current_value: data.current_value || null,
          purchase_date: data.purchase_date || '',
          warranty_expiration: data.warranty_expiration || '',
          tags: data.tags || [],
          notes: data.notes || ''
        }
        // Initialize tags input
        editTagsInput.value = (data.tags || []).join(', ')
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

    const loadLocations = async (propertyId = null) => {
      try {
        const { data } = await api.getLocations(propertyId || selectedPropertyId.value)
        locations.value = data
      } catch (error) {
        console.error('Failed to load locations:', error)
      }
    }

    const saveItem = async () => {
      saving.value = true
      try {
        // Clean form data: convert empty strings to null for optional fields
        const cleanedData = { ...editForm.value }
        const nullableFields = [
          'description', 'category_id', 'location_id', 'manufacturer',
          'model_number', 'serial_number', 'barcode', 'condition',
          'purchase_price', 'purchase_location', 'current_value',
          'purchase_date', 'warranty_expiration', 'notes'
        ]
        for (const field of nullableFields) {
          if (cleanedData[field] === '' || cleanedData[field] === undefined) {
            cleanedData[field] = null
          }
        }
        await api.updateItem(route.params.id, cleanedData)
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
        barcode: item.value.barcode || '',
        condition: item.value.condition || '',
        quantity: item.value.quantity || 1,
        purchase_price: item.value.purchase_price || null,
        purchase_location: item.value.purchase_location || '',
        current_value: item.value.current_value || null,
        purchase_date: item.value.purchase_date || '',
        warranty_expiration: item.value.warranty_expiration || '',
        tags: item.value.tags || [],
        notes: item.value.notes || ''
      }
      editTagsInput.value = (item.value.tags || []).join(', ')
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

    const getDocumentUrl = (documentId) => {
      return api.getDocumentUrl(documentId)
    }

    const formatDocumentType = (type) => {
      const types = {
        receipt: 'Receipt',
        manual: 'Manual',
        warranty: 'Warranty',
        other: 'Other'
      }
      return types[type] || type
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    const getDocumentIcon = (type, mimeType) => {
      if (mimeType && mimeType.startsWith('image/')) return '🖼️'
      if (mimeType && mimeType === 'application/pdf') return '📄'

      const icons = {
        receipt: '🧾',
        manual: '📖',
        warranty: '🛡️',
        other: '📎'
      }
      return icons[type] || '📎'
    }

    const handleDocumentSelect = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      // Validate file size (50MB max)
      const maxSize = 50 * 1024 * 1024
      if (file.size > maxSize) {
        alert('File is too large. Maximum size is 50MB.')
        return
      }

      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
      if (!allowedTypes.includes(file.type)) {
        alert('Invalid file type. Only PDF, JPG, and PNG files are allowed.')
        return
      }

      uploadingDocument.value = true
      try {
        await api.uploadDocument(route.params.id, file, newDocumentType.value)
        await loadItem()
        event.target.value = '' // Reset file input
        alert('Document uploaded successfully!')
      } catch (error) {
        alert('Failed to upload document: ' + error.message)
      } finally {
        uploadingDocument.value = false
      }
    }

    const deleteDocument = async (documentId) => {
      if (!confirm('Are you sure you want to delete this document?')) {
        return
      }

      try {
        await api.deleteDocument(documentId)
        await loadItem()
      } catch (error) {
        alert('Failed to delete document: ' + error.message)
      }
    }

    const handleImageSelect = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      // Validate file size (20MB max)
      const maxSize = 20 * 1024 * 1024
      if (file.size > maxSize) {
        alert('File is too large. Maximum size is 20MB.')
        return
      }

      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        alert('Invalid file type. Only JPG, PNG, and WebP images are allowed.')
        return
      }

      try {
        await api.addItemImage(route.params.id, file)
        await loadItem()
        event.target.value = '' // Reset file input
      } catch (error) {
        alert('Failed to upload image: ' + error.message)
      }
    }

    const deleteImage = async (imageId) => {
      if (!confirm('Are you sure you want to delete this image?')) {
        return
      }

      try {
        await api.deleteImage(imageId)
        await loadItem()
        // Reset current image if it was deleted
        if (currentImageId.value === imageId && item.value.images?.length > 0) {
          currentImageId.value = item.value.images[0].id
        }
      } catch (error) {
        alert('Failed to delete image: ' + error.message)
      }
    }

    const setImageAsPrimary = async (imageId) => {
      try {
        await api.setPrimaryImage(imageId)
        await loadItem()
      } catch (error) {
        alert('Failed to set primary image: ' + error.message)
      }
    }

    const updateEditTags = () => {
      // Convert comma-separated string to array
      editForm.value.tags = editTagsInput.value
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)
    }

    const getQrCodeUrl = () => {
      // Use the current origin as the base URL for the QR code
      const baseUrl = window.location.origin
      return api.getItemQrCodeUrl(route.params.id, baseUrl)
    }

    const copyPublicLink = async () => {
      const publicUrl = `${window.location.origin}/public/items/${route.params.id}`
      try {
        await navigator.clipboard.writeText(publicUrl)
        linkCopied.value = true
        setTimeout(() => {
          linkCopied.value = false
        }, 3000)
      } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea')
        textArea.value = publicUrl
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
        linkCopied.value = true
        setTimeout(() => {
          linkCopied.value = false
        }, 3000)
      }
    }

    const openImageViewer = (index = 0) => {
      imageViewerStartIndex.value = index
      imageViewerOpen.value = true
    }

    onMounted(async () => {
      await loadItem()
      loadCategories()
      // Load locations filtered by item's property
      if (item.value && item.value.property_id) {
        loadLocations(item.value.property_id)
      } else {
        loadLocations()
      }
    })

    return {
      item,
      loading,
      editMode,
      saving,
      currentImageId,
      editForm,
      editTagsInput,
      categories,
      locations,
      flatCategories,
      flatLocations,
      newDocumentType,
      uploadingDocument,
      deleteItem,
      saveItem,
      cancelEdit,
      formatCurrency,
      formatDate,
      getImageUrl,
      getDocumentUrl,
      formatDocumentType,
      formatFileSize,
      getDocumentIcon,
      handleDocumentSelect,
      deleteDocument,
      handleImageSelect,
      deleteImage,
      setImageAsPrimary,
      updateEditTags,
      getQrCodeUrl,
      copyPublicLink,
      linkCopied,
      imageViewerOpen,
      imageViewerStartIndex,
      openImageViewer
    }
  }
}
</script>
