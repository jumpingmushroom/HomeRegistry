<template>
  <div class="container">
    <h1 style="margin-bottom: 24px;">Settings</h1>

    <div class="card">
      <h3 style="margin-bottom: 16px;">AI Provider Configuration</h3>

      <div class="form-group">
        <label class="label">AI Provider</label>
        <select v-model="settings.ai_provider" class="select">
          <option value="claude">Anthropic Claude</option>
          <option value="openai">OpenAI GPT-4</option>
          <option value="gemini">Google Gemini</option>
          <option value="ollama">Ollama (Local)</option>
        </select>
      </div>

      <div class="form-group" v-if="settings.ai_provider === 'claude'">
        <label class="label">Claude API Key</label>
        <input
          type="password"
          v-model="settings.claude_api_key"
          class="input"
          placeholder="sk-ant-..."
        />
      </div>

      <div class="form-group" v-if="settings.ai_provider === 'openai'">
        <label class="label">OpenAI API Key</label>
        <input
          type="password"
          v-model="settings.openai_api_key"
          class="input"
          placeholder="sk-..."
        />
      </div>

      <div class="form-group" v-if="settings.ai_provider === 'gemini'">
        <label class="label">Gemini API Key</label>
        <input
          type="password"
          v-model="settings.gemini_api_key"
          class="input"
          placeholder="AI..."
        />
      </div>

      <div class="form-group" v-if="settings.ai_provider === 'ollama'">
        <label class="label">Ollama Endpoint</label>
        <input
          type="text"
          v-model="settings.ollama_endpoint"
          class="input"
          placeholder="http://ollama:11434"
        />
      </div>

      <div v-if="testResult" :class="testResult.success ? 'success-message' : 'error-message'">
        {{ testResult.message }}
      </div>

      <div class="form-group" v-if="settings.ai_provider === 'gemini' && availableModels.length > 0">
        <label class="label">Gemini Model</label>
        <select v-model="settings.gemini_model" class="select">
          <option v-for="model in availableModels" :key="model.name" :value="model.name">
            {{ model.display_name }}
          </option>
        </select>
        <small style="color: var(--text-secondary);" v-if="settings.gemini_model">
          {{ getModelDescription(settings.gemini_model) }}
        </small>
      </div>

      <div style="display: flex; gap: 12px; margin-top: 16px;">
        <button @click="testConnection" class="btn btn-outline" :disabled="testing">
          {{ testing ? 'Testing...' : 'Test Connection' }}
        </button>
        <button @click="saveSettings" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save Settings' }}
        </button>
      </div>
    </div>

    <div class="card" style="margin-top: 16px;">
      <h3 style="margin-bottom: 16px;">General Settings</h3>

      <div class="form-group">
        <label class="label">Default Currency</label>
        <input
          type="text"
          v-model="settings.default_currency"
          class="input"
          placeholder="NOK"
        />
      </div>
    </div>

    <!-- Home Details Section -->
    <div class="card" style="margin-top: 16px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <h3>Home Details</h3>
        <button @click="openPropertyModal()" class="btn btn-primary">+ Add Property</button>
      </div>

      <div v-if="loadingProperties" class="loading">
        <div class="spinner"></div>
      </div>

      <div v-else-if="properties.length === 0" style="color: var(--text-secondary); padding: 16px; text-align: center;">
        No properties configured. Add your first property to get started.
      </div>

      <div v-else>
        <div v-for="property in properties" :key="property.id" class="property-card">
          <div class="property-header" @click="toggleProperty(property.id)">
            <div>
              <strong>{{ property.name }}</strong>
              <div style="font-size: 12px; color: var(--text-secondary);">
                {{ property.address_city }}, {{ property.address_country }}
                <span v-if="property.property_type"> - {{ formatPropertyType(property.property_type) }}</span>
              </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
              <span style="font-size: 12px; color: var(--text-secondary);">
                {{ property.policy_count }} {{ property.policy_count === 1 ? 'policy' : 'policies' }}
              </span>
              <span>{{ expandedProperties.includes(property.id) ? '▼' : '▶' }}</span>
            </div>
          </div>

          <div v-if="expandedProperties.includes(property.id)" class="property-details">
            <div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">
              <button @click="editProperty(property)" class="btn btn-outline btn-sm">Edit Property</button>
              <button @click="confirmDeleteProperty(property.id)" class="btn btn-outline btn-sm btn-danger">Delete</button>
              <button @click="openPolicyModal(property.id)" class="btn btn-primary btn-sm">+ Add Policy</button>
            </div>

            <!-- Insurance Policies List -->
            <div v-if="propertyPolicies[property.id]?.length > 0">
              <h4 style="margin-bottom: 8px; font-size: 14px;">Insurance Policies</h4>
              <div v-for="policy in propertyPolicies[property.id]" :key="policy.id" class="policy-item">
                <div>
                  <strong>{{ policy.name }}</strong> - {{ policy.company_name }}
                  <div style="font-size: 12px; color: var(--text-secondary);">
                    {{ formatPolicyType(policy.policy_type) }} | #{{ policy.policy_number }}
                    <span v-if="policy.renewal_date"> | Renews: {{ formatDate(policy.renewal_date) }}</span>
                  </div>
                </div>
                <div style="display: flex; gap: 8px;">
                  <button @click="editPolicy(policy)" class="btn btn-outline btn-sm">Edit</button>
                  <button @click="confirmDeletePolicy(policy.id, property.id)" class="btn btn-outline btn-sm btn-danger">Delete</button>
                </div>
              </div>
            </div>
            <div v-else style="color: var(--text-secondary); font-size: 14px;">
              No insurance policies for this property.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Property Modal -->
    <div v-if="showPropertyModal" class="modal-overlay" @click.self="closePropertyModal">
      <div class="modal" style="max-width: 600px;">
        <h2>{{ editingProperty ? 'Edit Property' : 'Add Property' }}</h2>

        <div class="form-group">
          <label class="label">Property Name *</label>
          <input v-model="propertyForm.name" class="input" placeholder="e.g., Main Residence" required />
        </div>

        <h4 style="margin: 16px 0 8px 0;">Address</h4>
        <div class="form-group">
          <label class="label">Street Address *</label>
          <input v-model="propertyForm.address_street" class="input" required />
        </div>
        <div class="grid grid-2">
          <div class="form-group">
            <label class="label">City *</label>
            <input v-model="propertyForm.address_city" class="input" required />
          </div>
          <div class="form-group">
            <label class="label">State/Province *</label>
            <input v-model="propertyForm.address_state" class="input" required />
          </div>
        </div>
        <div class="grid grid-2">
          <div class="form-group">
            <label class="label">Postal Code *</label>
            <input v-model="propertyForm.address_postal_code" class="input" required />
          </div>
          <div class="form-group">
            <label class="label">Country *</label>
            <input v-model="propertyForm.address_country" class="input" required />
          </div>
        </div>

        <h4 style="margin: 16px 0 8px 0;">Primary Contact</h4>
        <div class="form-group">
          <label class="label">Contact Name *</label>
          <input v-model="propertyForm.primary_contact_name" class="input" required />
        </div>
        <div class="grid grid-2">
          <div class="form-group">
            <label class="label">Email</label>
            <input v-model="propertyForm.primary_contact_email" class="input" type="email" />
          </div>
          <div class="form-group">
            <label class="label">Phone</label>
            <input v-model="propertyForm.primary_contact_phone" class="input" type="tel" />
          </div>
        </div>

        <h4 style="margin: 16px 0 8px 0;">Property Details</h4>
        <div class="grid grid-2">
          <div class="form-group">
            <label class="label">Property Type</label>
            <select v-model="propertyForm.property_type" class="select">
              <option value="house">House</option>
              <option value="apartment">Apartment</option>
              <option value="condo">Condo</option>
              <option value="townhouse">Townhouse</option>
              <option value="cabin">Cabin</option>
              <option value="storage_unit">Storage Unit</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label class="label">Year Built</label>
            <input v-model="propertyForm.year_built" class="input" type="number" />
          </div>
        </div>
        <div class="form-group">
          <label class="label">Square Meters</label>
          <input v-model="propertyForm.square_meters" class="input" type="number" />
        </div>
        <div class="form-group">
          <label class="label">Additional Residents</label>
          <textarea v-model="propertyForm.additional_residents" class="textarea" rows="2" placeholder="List other household members"></textarea>
        </div>
        <div class="form-group">
          <label class="label">Notes</label>
          <textarea v-model="propertyForm.notes" class="textarea" rows="2"></textarea>
        </div>

        <div style="display: flex; gap: 12px; margin-top: 16px;">
          <button @click="closePropertyModal" class="btn btn-outline">Cancel</button>
          <button @click="saveProperty" class="btn btn-primary" :disabled="savingProperty">
            {{ savingProperty ? 'Saving...' : (editingProperty ? 'Update' : 'Add') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Policy Modal -->
    <div v-if="showPolicyModal" class="modal-overlay" @click.self="closePolicyModal">
      <div class="modal" style="max-width: 600px;">
        <h2>{{ editingPolicy ? 'Edit Insurance Policy' : 'Add Insurance Policy' }}</h2>

        <div class="form-group">
          <label class="label">Policy Name *</label>
          <input v-model="policyForm.name" class="input" placeholder="e.g., Home Insurance 2024" required />
        </div>
        <div class="grid grid-2">
          <div class="form-group">
            <label class="label">Insurance Company *</label>
            <input v-model="policyForm.company_name" class="input" required />
          </div>
          <div class="form-group">
            <label class="label">Policy Number *</label>
            <input v-model="policyForm.policy_number" class="input" required />
          </div>
        </div>
        <div class="form-group">
          <label class="label">Policy Type *</label>
          <select v-model="policyForm.policy_type" class="select" required>
            <option value="homeowners">Homeowners</option>
            <option value="renters">Renters</option>
            <option value="flood">Flood</option>
            <option value="earthquake">Earthquake</option>
            <option value="umbrella">Umbrella</option>
            <option value="contents">Contents</option>
            <option value="building">Building</option>
            <option value="other">Other</option>
          </select>
        </div>

        <h4 style="margin: 16px 0 8px 0;">Coverage Details</h4>
        <div class="grid grid-2">
          <div class="form-group">
            <label class="label">Coverage Amount</label>
            <input v-model="policyForm.coverage_amount" class="input" type="number" step="0.01" />
          </div>
          <div class="form-group">
            <label class="label">Deductible</label>
            <input v-model="policyForm.deductible" class="input" type="number" step="0.01" />
          </div>
        </div>
        <div class="grid grid-2">
          <div class="form-group">
            <label class="label">Premium</label>
            <input v-model="policyForm.premium" class="input" type="number" step="0.01" />
          </div>
          <div class="form-group">
            <label class="label">Currency</label>
            <input v-model="policyForm.currency" class="input" placeholder="NOK" />
          </div>
        </div>

        <h4 style="margin: 16px 0 8px 0;">Dates</h4>
        <div class="grid grid-2">
          <div class="form-group">
            <label class="label">Start Date</label>
            <input v-model="policyForm.start_date" class="input" type="date" />
          </div>
          <div class="form-group">
            <label class="label">Renewal Date</label>
            <input v-model="policyForm.renewal_date" class="input" type="date" />
          </div>
        </div>

        <h4 style="margin: 16px 0 8px 0;">Agent Information</h4>
        <div class="form-group">
          <label class="label">Agent Name</label>
          <input v-model="policyForm.agent_name" class="input" />
        </div>
        <div class="grid grid-2">
          <div class="form-group">
            <label class="label">Agent Phone</label>
            <input v-model="policyForm.agent_phone" class="input" type="tel" />
          </div>
          <div class="form-group">
            <label class="label">Agent Email</label>
            <input v-model="policyForm.agent_email" class="input" type="email" />
          </div>
        </div>

        <div class="form-group">
          <label class="label">Notes</label>
          <textarea v-model="policyForm.notes" class="textarea" rows="2"></textarea>
        </div>

        <div style="display: flex; gap: 12px; margin-top: 16px;">
          <button @click="closePolicyModal" class="btn btn-outline">Cancel</button>
          <button @click="savePolicy" class="btn btn-primary" :disabled="savingPolicy">
            {{ savingPolicy ? 'Saving...' : (editingPolicy ? 'Update' : 'Add') }}
          </button>
        </div>
      </div>
    </div>

    <div class="card" style="margin-top: 16px;">
      <h3 style="margin-bottom: 16px;">Quick Links</h3>
      <div style="display: flex; flex-direction: column; gap: 8px;">
        <router-link to="/locations" class="btn btn-outline">Manage Locations</router-link>
        <router-link to="/categories" class="btn btn-outline">Manage Categories</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'Settings',
  setup() {
    const settings = ref({
      ai_provider: 'claude',
      claude_api_key: '',
      openai_api_key: '',
      gemini_api_key: '',
      gemini_model: '',
      ollama_endpoint: 'http://ollama:11434',
      default_currency: 'NOK'
    })
    const testing = ref(false)
    const saving = ref(false)
    const testResult = ref(null)
    const availableModels = ref([])

    // Property state
    const properties = ref([])
    const loadingProperties = ref(true)
    const expandedProperties = ref([])
    const propertyPolicies = ref({})
    const showPropertyModal = ref(false)
    const editingProperty = ref(null)
    const savingProperty = ref(false)
    const propertyForm = ref(getEmptyPropertyForm())

    // Policy state
    const showPolicyModal = ref(false)
    const editingPolicy = ref(null)
    const savingPolicy = ref(false)
    const currentPropertyId = ref(null)
    const policyForm = ref(getEmptyPolicyForm())

    function getEmptyPropertyForm() {
      return {
        name: '',
        address_street: '',
        address_city: '',
        address_state: '',
        address_postal_code: '',
        address_country: '',
        primary_contact_name: '',
        primary_contact_email: '',
        primary_contact_phone: '',
        additional_residents: '',
        property_type: 'house',
        year_built: null,
        square_meters: null,
        notes: ''
      }
    }

    function getEmptyPolicyForm() {
      return {
        name: '',
        company_name: '',
        policy_number: '',
        policy_type: 'homeowners',
        coverage_amount: null,
        deductible: null,
        premium: null,
        currency: 'NOK',
        start_date: '',
        renewal_date: '',
        agent_name: '',
        agent_phone: '',
        agent_email: '',
        notes: ''
      }
    }

    const loadSettings = async () => {
      try {
        const { data } = await api.getSettings()
        settings.value = {
          ai_provider: data.ai_provider || 'claude',
          claude_api_key: data.claude_api_key || '',
          openai_api_key: data.openai_api_key || '',
          gemini_api_key: data.gemini_api_key || '',
          gemini_model: data.gemini_model || '',
          ollama_endpoint: data.ollama_endpoint || 'http://ollama:11434',
          default_currency: data.default_currency || 'NOK'
        }

        // If Gemini is selected and we have an API key, load available models
        if (data.ai_provider === 'gemini' && data.gemini_api_key) {
          await loadGeminiModels()
        }
      } catch (error) {
        console.error('Failed to load settings:', error)
      }
    }

    const loadProperties = async () => {
      loadingProperties.value = true
      try {
        const { data } = await api.getProperties()
        properties.value = data
      } catch (error) {
        console.error('Failed to load properties:', error)
      } finally {
        loadingProperties.value = false
      }
    }

    const loadPoliciesForProperty = async (propertyId) => {
      try {
        const { data } = await api.getInsurancePolicies(propertyId)
        propertyPolicies.value[propertyId] = data
      } catch (error) {
        console.error('Failed to load policies:', error)
      }
    }

    const toggleProperty = async (propertyId) => {
      const index = expandedProperties.value.indexOf(propertyId)
      if (index > -1) {
        expandedProperties.value.splice(index, 1)
      } else {
        expandedProperties.value.push(propertyId)
        if (!propertyPolicies.value[propertyId]) {
          await loadPoliciesForProperty(propertyId)
        }
      }
    }

    // Property CRUD
    const openPropertyModal = () => {
      editingProperty.value = null
      propertyForm.value = getEmptyPropertyForm()
      showPropertyModal.value = true
    }

    const editProperty = async (property) => {
      try {
        const { data } = await api.getProperty(property.id)
        editingProperty.value = data
        propertyForm.value = {
          name: data.name || '',
          address_street: data.address_street || '',
          address_city: data.address_city || '',
          address_state: data.address_state || '',
          address_postal_code: data.address_postal_code || '',
          address_country: data.address_country || '',
          primary_contact_name: data.primary_contact_name || '',
          primary_contact_email: data.primary_contact_email || '',
          primary_contact_phone: data.primary_contact_phone || '',
          additional_residents: data.additional_residents || '',
          property_type: data.property_type || 'house',
          year_built: data.year_built,
          square_meters: data.square_meters,
          notes: data.notes || ''
        }
        showPropertyModal.value = true
      } catch (error) {
        alert('Failed to load property: ' + error.message)
      }
    }

    const closePropertyModal = () => {
      showPropertyModal.value = false
      editingProperty.value = null
      propertyForm.value = getEmptyPropertyForm()
    }

    const saveProperty = async () => {
      if (!propertyForm.value.name || !propertyForm.value.address_street || !propertyForm.value.primary_contact_name) {
        alert('Please fill in all required fields')
        return
      }

      savingProperty.value = true
      try {
        if (editingProperty.value) {
          await api.updateProperty(editingProperty.value.id, propertyForm.value)
        } else {
          await api.createProperty(propertyForm.value)
        }
        closePropertyModal()
        await loadProperties()
      } catch (error) {
        alert('Failed to save property: ' + (error.response?.data?.detail || error.message))
      } finally {
        savingProperty.value = false
      }
    }

    const confirmDeleteProperty = async (propertyId) => {
      if (!confirm('Are you sure you want to delete this property? All associated insurance policies will also be deleted.')) {
        return
      }
      try {
        await api.deleteProperty(propertyId)
        await loadProperties()
        // Remove from expanded list if present
        const index = expandedProperties.value.indexOf(propertyId)
        if (index > -1) {
          expandedProperties.value.splice(index, 1)
        }
        delete propertyPolicies.value[propertyId]
      } catch (error) {
        alert('Failed to delete property: ' + (error.response?.data?.detail || error.message))
      }
    }

    // Policy CRUD
    const openPolicyModal = (propertyId) => {
      currentPropertyId.value = propertyId
      editingPolicy.value = null
      policyForm.value = getEmptyPolicyForm()
      showPolicyModal.value = true
    }

    const editPolicy = (policy) => {
      editingPolicy.value = policy
      currentPropertyId.value = policy.property_id
      policyForm.value = {
        name: policy.name || '',
        company_name: policy.company_name || '',
        policy_number: policy.policy_number || '',
        policy_type: policy.policy_type || 'homeowners',
        coverage_amount: policy.coverage_amount,
        deductible: policy.deductible,
        premium: policy.premium,
        currency: policy.currency || 'NOK',
        start_date: policy.start_date || '',
        renewal_date: policy.renewal_date || '',
        agent_name: policy.agent_name || '',
        agent_phone: policy.agent_phone || '',
        agent_email: policy.agent_email || '',
        notes: policy.notes || ''
      }
      showPolicyModal.value = true
    }

    const closePolicyModal = () => {
      showPolicyModal.value = false
      editingPolicy.value = null
      currentPropertyId.value = null
      policyForm.value = getEmptyPolicyForm()
    }

    const savePolicy = async () => {
      if (!policyForm.value.name || !policyForm.value.company_name || !policyForm.value.policy_number) {
        alert('Please fill in all required fields')
        return
      }

      savingPolicy.value = true
      try {
        if (editingPolicy.value) {
          await api.updateInsurancePolicy(editingPolicy.value.id, policyForm.value)
        } else {
          await api.createInsurancePolicy({
            ...policyForm.value,
            property_id: currentPropertyId.value
          })
        }
        const propId = currentPropertyId.value
        closePolicyModal()
        await loadPoliciesForProperty(propId)
        await loadProperties() // Refresh policy counts
      } catch (error) {
        alert('Failed to save policy: ' + (error.response?.data?.detail || error.message))
      } finally {
        savingPolicy.value = false
      }
    }

    const confirmDeletePolicy = async (policyId, propertyId) => {
      if (!confirm('Are you sure you want to delete this insurance policy?')) {
        return
      }
      try {
        await api.deleteInsurancePolicy(policyId)
        await loadPoliciesForProperty(propertyId)
        await loadProperties() // Refresh policy counts
      } catch (error) {
        alert('Failed to delete policy: ' + (error.response?.data?.detail || error.message))
      }
    }

    // Formatters
    const formatPropertyType = (type) => {
      const types = {
        house: 'House',
        apartment: 'Apartment',
        condo: 'Condo',
        townhouse: 'Townhouse',
        cabin: 'Cabin',
        storage_unit: 'Storage Unit',
        other: 'Other'
      }
      return types[type] || type
    }

    const formatPolicyType = (type) => {
      const types = {
        homeowners: 'Homeowners',
        renters: 'Renters',
        flood: 'Flood',
        earthquake: 'Earthquake',
        umbrella: 'Umbrella',
        contents: 'Contents',
        building: 'Building',
        other: 'Other'
      }
      return types[type] || type
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString()
    }

    const testConnection = async () => {
      testing.value = true
      testResult.value = null

      try {
        const { data } = await api.testAI(
          settings.value.ai_provider,
          settings.value.ai_provider === 'claude' ? settings.value.claude_api_key :
          settings.value.ai_provider === 'openai' ? settings.value.openai_api_key :
          settings.value.ai_provider === 'gemini' ? settings.value.gemini_api_key : null,
          settings.value.ollama_endpoint
        )
        testResult.value = data

        // If Gemini and we got models, populate the list
        if (settings.value.ai_provider === 'gemini' && data.available_models) {
          availableModels.value = data.available_models
          // Auto-select the first model if none selected
          if (!settings.value.gemini_model && data.available_models.length > 0) {
            settings.value.gemini_model = data.available_models[0].name
          }
        }
      } catch (error) {
        testResult.value = {
          success: false,
          message: 'Connection test failed: ' + error.message
        }
      } finally {
        testing.value = false
      }
    }

    const loadGeminiModels = async () => {
      if (!settings.value.gemini_api_key) return

      try {
        const { data } = await api.testAI(
          'gemini',
          settings.value.gemini_api_key,
          null
        )
        if (data.available_models) {
          availableModels.value = data.available_models
        }
      } catch (error) {
        console.error('Failed to load Gemini models:', error)
      }
    }

    const getModelDescription = (modelName) => {
      const model = availableModels.value.find(m => m.name === modelName)
      return model?.description || 'Multimodal AI model with vision support'
    }

    const saveSettings = async () => {
      saving.value = true

      try {
        await api.updateSettings(settings.value)
        alert('Settings saved successfully!')
      } catch (error) {
        alert('Failed to save settings: ' + error.message)
      } finally {
        saving.value = false
      }
    }

    onMounted(() => {
      loadSettings()
      loadProperties()
    })

    return {
      settings,
      testing,
      saving,
      testResult,
      availableModels,
      testConnection,
      saveSettings,
      getModelDescription,
      // Property
      properties,
      loadingProperties,
      expandedProperties,
      propertyPolicies,
      showPropertyModal,
      editingProperty,
      savingProperty,
      propertyForm,
      toggleProperty,
      openPropertyModal,
      editProperty,
      closePropertyModal,
      saveProperty,
      confirmDeleteProperty,
      formatPropertyType,
      // Policy
      showPolicyModal,
      editingPolicy,
      savingPolicy,
      policyForm,
      openPolicyModal,
      editPolicy,
      closePolicyModal,
      savePolicy,
      confirmDeletePolicy,
      formatPolicyType,
      formatDate
    }
  }
}
</script>
