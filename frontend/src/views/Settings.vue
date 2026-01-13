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
      ollama_endpoint: 'http://ollama:11434',
      default_currency: 'NOK'
    })
    const testing = ref(false)
    const saving = ref(false)
    const testResult = ref(null)

    const loadSettings = async () => {
      try {
        const { data } = await api.getSettings()
        settings.value = {
          ai_provider: data.ai_provider || 'claude',
          claude_api_key: data.claude_api_key || '',
          openai_api_key: data.openai_api_key || '',
          gemini_api_key: data.gemini_api_key || '',
          ollama_endpoint: data.ollama_endpoint || 'http://ollama:11434',
          default_currency: data.default_currency || 'NOK'
        }
      } catch (error) {
        console.error('Failed to load settings:', error)
      }
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
      } catch (error) {
        testResult.value = {
          success: false,
          message: 'Connection test failed: ' + error.message
        }
      } finally {
        testing.value = false
      }
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

    onMounted(loadSettings)

    return {
      settings,
      testing,
      saving,
      testResult,
      testConnection,
      saveSettings
    }
  }
}
</script>
