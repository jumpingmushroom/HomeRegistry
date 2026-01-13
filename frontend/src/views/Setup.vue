<template>
  <div class="container" style="max-width: 600px; padding-top: 40px;">
    <div class="card">
      <h1 style="margin-bottom: 16px;">Welcome to HomeRegistry! 🏠</h1>
      <p style="color: var(--text-secondary); margin-bottom: 24px;">
        Let's set up your AI provider to get started with automated item analysis.
      </p>

      <div class="form-group">
        <label class="label">AI Provider</label>
        <select v-model="provider" class="select">
          <option value="claude">Anthropic Claude</option>
          <option value="openai">OpenAI GPT-4</option>
          <option value="gemini">Google Gemini</option>
          <option value="ollama">Ollama (Local)</option>
        </select>
      </div>

      <div class="form-group" v-if="provider === 'claude'">
        <label class="label">Claude API Key</label>
        <input
          type="password"
          v-model="apiKey"
          class="input"
          placeholder="sk-ant-..."
        />
        <small style="color: var(--text-secondary);">
          Get your API key from <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a>
        </small>
      </div>

      <div class="form-group" v-if="provider === 'openai'">
        <label class="label">OpenAI API Key</label>
        <input
          type="password"
          v-model="apiKey"
          class="input"
          placeholder="sk-..."
        />
        <small style="color: var(--text-secondary);">
          Get your API key from <a href="https://platform.openai.com" target="_blank">platform.openai.com</a>
        </small>
      </div>

      <div class="form-group" v-if="provider === 'gemini'">
        <label class="label">Gemini API Key</label>
        <input
          type="password"
          v-model="apiKey"
          class="input"
          placeholder="AI..."
        />
        <small style="color: var(--text-secondary);">
          Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a>
        </small>
      </div>

      <div class="form-group" v-if="provider === 'ollama'">
        <label class="label">Ollama Endpoint</label>
        <input
          type="text"
          v-model="endpoint"
          class="input"
          placeholder="http://ollama:11434"
        />
        <small style="color: var(--text-secondary);">
          Make sure Ollama is running with the llava model: <code>ollama pull llava</code>
        </small>
      </div>

      <div v-if="testResult" :class="testResult.success ? 'success-message' : 'error-message'">
        {{ testResult.message }}
      </div>

      <div class="form-group" v-if="provider === 'gemini' && availableModels.length > 0">
        <label class="label">Select Gemini Model</label>
        <select v-model="selectedModel" class="select">
          <option v-for="model in availableModels" :key="model.name" :value="model.name">
            {{ model.display_name }}
          </option>
        </select>
        <small style="color: var(--text-secondary);" v-if="selectedModel">
          {{ getModelDescription(selectedModel) }}
        </small>
      </div>

      <div style="display: flex; gap: 12px; margin-top: 24px;">
        <button @click="testConnection" class="btn btn-outline" :disabled="testing">
          {{ testing ? 'Testing...' : 'Test Connection' }}
        </button>
        <button @click="saveSettings" class="btn btn-primary" :disabled="!testResult || !testResult.success || saving || (provider === 'gemini' && !selectedModel)">
          {{ saving ? 'Saving...' : 'Complete Setup' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'Setup',
  setup() {
    const router = useRouter()
    const provider = ref('claude')
    const apiKey = ref('')
    const endpoint = ref('http://ollama:11434')
    const testing = ref(false)
    const saving = ref(false)
    const testResult = ref(null)
    const availableModels = ref([])
    const selectedModel = ref('')

    const testConnection = async () => {
      testing.value = true
      testResult.value = null
      availableModels.value = []
      selectedModel.value = ''

      try {
        const { data } = await api.testAI(
          provider.value,
          apiKey.value,
          endpoint.value
        )
        testResult.value = data

        // If Gemini and we got models, populate the list
        if (provider.value === 'gemini' && data.available_models) {
          availableModels.value = data.available_models
          // Auto-select the first model
          if (data.available_models.length > 0) {
            selectedModel.value = data.available_models[0].name
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

    const saveSettings = async () => {
      saving.value = true

      try {
        const settings = {
          ai_provider: provider.value,
          claude_api_key: provider.value === 'claude' ? apiKey.value : null,
          openai_api_key: provider.value === 'openai' ? apiKey.value : null,
          gemini_api_key: provider.value === 'gemini' ? apiKey.value : null,
          gemini_model: provider.value === 'gemini' ? selectedModel.value : null,
          ollama_endpoint: provider.value === 'ollama' ? endpoint.value : null,
          setup_completed: true
        }

        await api.updateSettings(settings)
        router.push('/')
      } catch (error) {
        alert('Failed to save settings: ' + error.message)
      } finally {
        saving.value = false
      }
    }

    const getModelDescription = (modelName) => {
      const model = availableModels.value.find(m => m.name === modelName)
      return model?.description || 'Multimodal AI model with vision support'
    }

    return {
      provider,
      apiKey,
      endpoint,
      testing,
      saving,
      testResult,
      availableModels,
      selectedModel,
      testConnection,
      saveSettings,
      getModelDescription
    }
  }
}
</script>
