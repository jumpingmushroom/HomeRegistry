<template>
  <div class="container">
    <h1 style="margin-bottom: 24px;">Settings</h1>

    <!-- Tab Navigation -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- General Tab -->
    <div v-show="activeTab === 'general'" class="tab-content">
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

        <div class="form-group">
          <label class="label">High-Value Item Threshold</label>
          <input
            type="number"
            v-model="settings.high_value_threshold"
            class="input"
            placeholder="5000"
            min="0"
          />
          <small style="color: var(--text-secondary); display: block; margin-top: 4px;">
            Items above this value without documentation will be flagged on the dashboard.
          </small>
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

    <!-- Properties Tab -->
    <div v-show="activeTab === 'properties'" class="tab-content">
      <div class="card">
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
    </div>

    <!-- Backups Tab -->
    <div v-show="activeTab === 'backups'" class="tab-content">
      <!-- Backup Status Card -->
      <div class="card">
        <h3 style="margin-bottom: 16px;">Backup Status</h3>

        <div v-if="loadingBackupStatus" class="loading">
          <div class="spinner"></div>
        </div>

        <div v-else>
          <div class="status-grid">
            <div class="status-item">
              <span class="status-label">Status</span>
              <span :class="['status-value', backupStatus.enabled ? 'status-enabled' : 'status-disabled']">
                {{ backupStatus.enabled ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label">Interval</span>
              <span class="status-value">Every {{ backupStatus.interval_hours }} hour(s)</span>
            </div>
            <div class="status-item">
              <span class="status-label">Last Backup</span>
              <span class="status-value">{{ backupStatus.last_backup ? formatDateTime(backupStatus.last_backup) : 'Never' }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">Total Backups</span>
              <span class="status-value">{{ backupStatus.count }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">Total Size</span>
              <span class="status-value">{{ formatSize(backupStatus.total_size) }}</span>
            </div>
          </div>

          <div v-if="backupStatus.last_error" class="error-message" style="margin-top: 12px;">
            Last error: {{ backupStatus.last_error }}
          </div>
        </div>

        <div style="display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap;">
          <button @click="createBackup" class="btn btn-primary" :disabled="creatingBackup">
            {{ creatingBackup ? 'Creating...' : 'Create Backup Now' }}
          </button>
          <button @click="downloadCurrentDb" class="btn btn-outline" :disabled="downloadingCurrent">
            {{ downloadingCurrent ? 'Downloading...' : 'Download Current Database' }}
          </button>
          <button @click="showCleanupConfirm = true" class="btn btn-outline" :disabled="runningCleanup">
            {{ runningCleanup ? 'Cleaning...' : 'Run Cleanup' }}
          </button>
        </div>
      </div>

      <!-- Retention Policy Info -->
      <div class="card" style="margin-top: 16px;">
        <h3 style="margin-bottom: 12px;">Retention Policy</h3>
        <div class="info-box">
          <p><strong>Hourly:</strong> Keep all backups from the last {{ backupStatus.retention?.hourly_hours || 24 }} hours</p>
          <p><strong>Daily:</strong> Keep one backup per day for the last {{ backupStatus.retention?.daily_days || 7 }} days (prefers midnight backups)</p>
          <p><strong>Weekly:</strong> Keep one backup per week for the last {{ backupStatus.retention?.weekly_weeks || 4 }} weeks (prefers Sunday backups)</p>
          <p><strong>Monthly:</strong> Keep one backup per month for the last {{ backupStatus.retention?.monthly_months || 12 }} months (prefers 1st of month)</p>
        </div>
      </div>

      <!-- Backup List -->
      <div class="card" style="margin-top: 16px;">
        <h3 style="margin-bottom: 16px;">Available Backups</h3>

        <div v-if="loadingBackups" class="loading">
          <div class="spinner"></div>
        </div>

        <div v-else-if="backups.length === 0" style="color: var(--text-secondary); padding: 16px; text-align: center;">
          No backups available yet.
        </div>

        <div v-else class="backup-list">
          <div v-for="backup in backups" :key="backup.filename" class="backup-item">
            <div>
              <strong>{{ backup.filename }}</strong>
              <div style="font-size: 12px; color: var(--text-secondary);">
                {{ formatDateTime(backup.created_at) }} - {{ formatSize(backup.size) }}
              </div>
            </div>
            <button
              @click="downloadBackup(backup.filename)"
              class="btn btn-outline btn-sm"
              :disabled="downloadingFile === backup.filename"
            >
              {{ downloadingFile === backup.filename ? 'Downloading...' : 'Download' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Export Data -->
      <div class="card" style="margin-top: 16px;">
        <h3 style="margin-bottom: 12px;">Export Data</h3>
        <div class="info-box" style="margin-bottom: 16px;">
          <p>Download a complete backup of your inventory in a portable format. The export includes:</p>
          <ul style="margin: 8px 0 0 20px; padding: 0;">
            <li><strong>data.json</strong> - All structured data (items, categories, locations, properties, insurance policies)</li>
            <li><strong>items.csv</strong> - Spreadsheet-friendly export of all items</li>
            <li><strong>images/</strong> - All item images organized by item</li>
            <li><strong>documents/</strong> - All item documents (receipts, manuals, warranties)</li>
          </ul>
        </div>
        <button @click="exportAllData" class="btn btn-primary" :disabled="exporting">
          {{ exporting ? 'Generating Export...' : 'Download Full Export' }}
        </button>
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

    <!-- Cleanup Confirmation Modal -->
    <div v-if="showCleanupConfirm" class="modal-overlay" @click.self="showCleanupConfirm = false">
      <div class="modal" style="max-width: 400px;">
        <h2>Confirm Cleanup</h2>
        <p style="margin: 16px 0;">
          This will remove old backups according to the retention policy. This action cannot be undone.
        </p>
        <div style="display: flex; gap: 12px; margin-top: 16px;">
          <button @click="showCleanupConfirm = false" class="btn btn-outline">Cancel</button>
          <button @click="runCleanup" class="btn btn-primary">Run Cleanup</button>
        </div>
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
    // Tab state
    const tabs = [
      { id: 'general', label: 'General' },
      { id: 'properties', label: 'Properties' },
      { id: 'backups', label: 'Backups' }
    ]
    const activeTab = ref('general')

    // Settings state
    const settings = ref({
      ai_provider: 'claude',
      claude_api_key: '',
      openai_api_key: '',
      gemini_api_key: '',
      gemini_model: '',
      ollama_endpoint: 'http://ollama:11434',
      default_currency: 'NOK',
      high_value_threshold: 5000
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

    // Backup state
    const backupStatus = ref({
      enabled: false,
      interval_hours: 1,
      last_backup: null,
      last_error: null,
      count: 0,
      total_size: 0,
      retention: {}
    })
    const backups = ref([])
    const loadingBackupStatus = ref(true)
    const loadingBackups = ref(true)
    const creatingBackup = ref(false)
    const downloadingCurrent = ref(false)
    const downloadingFile = ref(null)
    const runningCleanup = ref(false)
    const showCleanupConfirm = ref(false)
    const exporting = ref(false)

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

    // Settings methods
    const loadSettings = async () => {
      try {
        const response = await api.getSettings()
        const data = response?.data || {}
        settings.value = {
          ai_provider: data.ai_provider || 'claude',
          claude_api_key: data.claude_api_key || '',
          openai_api_key: data.openai_api_key || '',
          gemini_api_key: data.gemini_api_key || '',
          gemini_model: data.gemini_model || '',
          ollama_endpoint: data.ollama_endpoint || 'http://ollama:11434',
          default_currency: data.default_currency || 'NOK',
          high_value_threshold: data.high_value_threshold || 5000
        }

        // Load Gemini models in background - don't block UI
        if (data.ai_provider === 'gemini' && data.gemini_api_key) {
          loadGeminiModels().catch(() => {})
        }
      } catch (error) {
        console.error('Failed to load settings:', error)
        // Keep default settings on error
      }
    }

    const testConnection = async () => {
      testing.value = true
      testResult.value = null

      try {
        const response = await api.testAI(
          settings.value.ai_provider,
          settings.value.ai_provider === 'claude' ? settings.value.claude_api_key :
          settings.value.ai_provider === 'openai' ? settings.value.openai_api_key :
          settings.value.ai_provider === 'gemini' ? settings.value.gemini_api_key : null,
          settings.value.ollama_endpoint
        )
        const data = response?.data || { success: false, message: 'No response from server' }
        testResult.value = data

        if (settings.value.ai_provider === 'gemini' && Array.isArray(data.available_models)) {
          availableModels.value = data.available_models
          if (!settings.value.gemini_model && data.available_models.length > 0) {
            settings.value.gemini_model = data.available_models[0].name
          }
        }
      } catch (error) {
        testResult.value = {
          success: false,
          message: 'Connection test failed: ' + (error?.message || 'Unknown error')
        }
      } finally {
        testing.value = false
      }
    }

    const loadGeminiModels = async () => {
      if (!settings.value.gemini_api_key) return

      try {
        const response = await api.testAI('gemini', settings.value.gemini_api_key, null)
        const data = response?.data
        if (data?.available_models && Array.isArray(data.available_models)) {
          availableModels.value = data.available_models
        }
      } catch (error) {
        // Silently fail - models will be loaded when user clicks Test Connection
        console.error('Failed to load Gemini models:', error)
        availableModels.value = []
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

    // Property methods
    const loadProperties = async () => {
      loadingProperties.value = true
      try {
        const response = await api.getProperties()
        properties.value = Array.isArray(response?.data) ? response.data : []
      } catch (error) {
        console.error('Failed to load properties:', error)
        properties.value = []
      } finally {
        loadingProperties.value = false
      }
    }

    const loadPoliciesForProperty = async (propertyId) => {
      try {
        const response = await api.getInsurancePolicies(propertyId)
        propertyPolicies.value[propertyId] = Array.isArray(response?.data) ? response.data : []
      } catch (error) {
        console.error('Failed to load policies:', error)
        propertyPolicies.value[propertyId] = []
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
        const index = expandedProperties.value.indexOf(propertyId)
        if (index > -1) {
          expandedProperties.value.splice(index, 1)
        }
        delete propertyPolicies.value[propertyId]
      } catch (error) {
        alert('Failed to delete property: ' + (error.response?.data?.detail || error.message))
      }
    }

    // Policy methods
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
        await loadProperties()
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
        await loadProperties()
      } catch (error) {
        alert('Failed to delete policy: ' + (error.response?.data?.detail || error.message))
      }
    }

    // Backup methods
    const loadBackupStatus = async () => {
      loadingBackupStatus.value = true
      try {
        const response = await api.getBackupStatus()
        backupStatus.value = response?.data || {
          enabled: false,
          interval_hours: 1,
          last_backup: null,
          last_error: null,
          count: 0,
          total_size: 0,
          retention: {}
        }
      } catch (error) {
        console.error('Failed to load backup status:', error)
      } finally {
        loadingBackupStatus.value = false
      }
    }

    const loadBackups = async () => {
      loadingBackups.value = true
      try {
        const response = await api.listBackups()
        backups.value = Array.isArray(response?.data?.backups) ? response.data.backups : []
      } catch (error) {
        console.error('Failed to load backups:', error)
        backups.value = []
      } finally {
        loadingBackups.value = false
      }
    }

    const createBackup = async () => {
      creatingBackup.value = true
      try {
        await api.createBackup()
        alert('Backup created successfully!')
        await loadBackupStatus()
        await loadBackups()
      } catch (error) {
        alert('Failed to create backup: ' + (error.response?.data?.detail || error.message))
      } finally {
        creatingBackup.value = false
      }
    }

    const downloadCurrentDb = async () => {
      downloadingCurrent.value = true
      try {
        const response = await api.downloadCurrentDatabase()
        const blob = new Blob([response.data], { type: 'application/x-sqlite3' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = response.headers['content-disposition']?.split('filename=')[1] || 'homeregistry_current.db'
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } catch (error) {
        alert('Failed to download database: ' + (error.response?.data?.detail || error.message))
      } finally {
        downloadingCurrent.value = false
      }
    }

    const downloadBackup = async (filename) => {
      downloadingFile.value = filename
      try {
        const response = await api.downloadBackup(filename)
        const blob = new Blob([response.data], { type: 'application/x-sqlite3' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } catch (error) {
        alert('Failed to download backup: ' + (error.response?.data?.detail || error.message))
      } finally {
        downloadingFile.value = null
      }
    }

    const runCleanup = async () => {
      showCleanupConfirm.value = false
      runningCleanup.value = true
      try {
        const { data } = await api.runBackupCleanup()
        alert(`Cleanup complete: ${data.result.deleted} backup(s) removed, ${data.result.kept} kept.`)
        await loadBackupStatus()
        await loadBackups()
      } catch (error) {
        alert('Failed to run cleanup: ' + (error.response?.data?.detail || error.message))
      } finally {
        runningCleanup.value = false
      }
    }

    const exportAllData = async () => {
      exporting.value = true
      try {
        const response = await api.exportAllData()
        const blob = new Blob([response.data], { type: 'application/zip' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url

        // Extract filename from content-disposition header or use default
        const contentDisposition = response.headers['content-disposition']
        let filename = 'homeregistry_export.zip'
        if (contentDisposition) {
          const match = contentDisposition.match(/filename=([^;]+)/)
          if (match) {
            filename = match[1].replace(/"/g, '')
          }
        }

        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } catch (error) {
        alert('Failed to export data: ' + (error.response?.data?.detail || error.message))
      } finally {
        exporting.value = false
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

    const formatDateTime = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString()
    }

    const formatSize = (bytes) => {
      if (!bytes || bytes === 0) return '0 B'
      const units = ['B', 'KB', 'MB', 'GB']
      let i = 0
      let size = bytes
      while (size >= 1024 && i < units.length - 1) {
        size /= 1024
        i++
      }
      return `${size.toFixed(1)} ${units[i]}`
    }

    onMounted(() => {
      loadSettings()
      loadProperties()
      loadBackupStatus()
      loadBackups()
    })

    return {
      // Tabs
      tabs,
      activeTab,
      // Settings
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
      formatDate,
      // Backups
      backupStatus,
      backups,
      loadingBackupStatus,
      loadingBackups,
      creatingBackup,
      downloadingCurrent,
      downloadingFile,
      runningCleanup,
      showCleanupConfirm,
      exporting,
      createBackup,
      downloadCurrentDb,
      downloadBackup,
      runCleanup,
      exportAllData,
      formatDateTime,
      formatSize
    }
  }
}
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0;
}

.tab-btn {
  padding: 12px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.tab-content {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.status-value {
  font-size: 16px;
  font-weight: 500;
}

.status-enabled {
  color: var(--success-color);
}

.status-disabled {
  color: var(--error-color);
}

.info-box {
  background: var(--surface-hover);
  padding: 16px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.info-box p {
  margin: 8px 0;
  color: var(--text-primary);
}

.info-box p:first-child {
  margin-top: 0;
}

.info-box p:last-child {
  margin-bottom: 0;
}

.backup-list {
  max-height: 400px;
  overflow-y: auto;
}

.backup-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

.backup-item:last-child {
  border-bottom: none;
}

.property-card {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}

.property-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  background: var(--surface-hover);
  color: var(--text-primary);
}

.property-header:hover {
  background: var(--surface);
}

.property-details {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  background: var(--background);
}

.policy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--surface-hover);
  border-radius: 4px;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.policy-item:last-child {
  margin-bottom: 0;
}
</style>
