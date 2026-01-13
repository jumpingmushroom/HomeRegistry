<template>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
      <h1>Categories</h1>
      <button @click="showAddModal = true" class="btn btn-primary">+ Add Category</button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else class="card">
      <div v-for="category in categories" :key="category.id">
        <CategoryTreeItem
          :category="category"
          @delete="deleteCategory"
        />
      </div>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <h2>Add Category</h2>
        <div class="form-group">
          <label class="label">Name *</label>
          <input v-model="newCategory.name" class="input" required />
        </div>
        <div class="form-group">
          <label class="label">Parent Category</label>
          <select v-model="newCategory.parent_id" class="select">
            <option value="">None (Top Level)</option>
            <option v-for="cat in flatCategories" :key="cat.id" :value="cat.id">
              {{ cat.indent }}{{ cat.name }}
            </option>
          </select>
        </div>
        <div style="display: flex; gap: 12px;">
          <button @click="showAddModal = false" class="btn btn-outline">Cancel</button>
          <button @click="addCategory" class="btn btn-primary">Add</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'Categories',
  setup() {
    const categories = ref([])
    const loading = ref(true)
    const showAddModal = ref(false)
    const newCategory = ref({
      name: '',
      parent_id: ''
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

    const loadCategories = async () => {
      try {
        const { data } = await api.getCategories()
        categories.value = data
      } catch (error) {
        console.error('Failed to load categories:', error)
      } finally {
        loading.value = false
      }
    }

    const addCategory = async () => {
      try {
        await api.createCategory({
          ...newCategory.value,
          parent_id: newCategory.value.parent_id || null
        })
        showAddModal.value = false
        newCategory.value = { name: '', parent_id: '' }
        loadCategories()
      } catch (error) {
        alert('Failed to add category: ' + error.message)
      }
    }

    const deleteCategory = async (categoryId) => {
      if (!confirm('Are you sure you want to delete this category?')) {
        return
      }

      try {
        await api.deleteCategory(categoryId)
        loadCategories()
      } catch (error) {
        alert('Failed to delete category: ' + error.message)
      }
    }

    onMounted(loadCategories)

    return {
      categories,
      loading,
      showAddModal,
      newCategory,
      flatCategories,
      addCategory,
      deleteCategory
    }
  },
  components: {
    CategoryTreeItem: {
      props: ['category'],
      emits: ['delete'],
      template: `
        <div style="margin-bottom: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; border-bottom: 1px solid var(--divider-color);">
            <div>
              <strong>{{ category.name }}</strong>
              <span style="margin-left: 8px; font-size: 12px; color: var(--text-secondary);">
                {{ category.item_count }} items
              </span>
            </div>
            <button @click="$emit('delete', category.id)" style="color: var(--error-color); background: none; border: none; cursor: pointer;">
              Delete
            </button>
          </div>
          <div v-if="category.children && category.children.length > 0" style="margin-left: 24px;">
            <CategoryTreeItem
              v-for="child in category.children"
              :key="child.id"
              :category="child"
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
}

.modal {
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}
</style>
