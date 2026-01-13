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

      <div style="display: flex; gap: 12px; margin-top: 24px;">
        <button @click="testConnection" class="btn btn-outline" :disabled="testing">
          {{ testing ? 'Testing...' : 'Test Connection' }}
        </button>
        <button @click="saveSettings" class="btn btn-primary" :disabled="!testResult || !testResult.success || saving">
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

    const testConnection = async () => {
      testing.value = true
      testResult.value = null

      try {
        const { data } = await api.testAI(
          provider.value,
          apiKey.value,
          endpoint.value
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
        await api.updateSettings({
          ai_provider: provider.value,
          claude_api_key: provider.value === 'claude' ? apiKey.value : null,
          openai_api_key: provider.value === 'openai' ? apiKey.value : null,
          ollama_endpoint: provider.value === 'ollama' ? endpoint.value : null,
          setup_completed: true
        })

        router.push('/')
      } catch (error) {
        alert('Failed to save settings: ' + error.message)
      } finally {
        saving.value = false
      }
    }

    return {
      provider,
      apiKey,
      endpoint,
      testing,
      saving,
      testResult,
      testConnection,
      saveSettings
    }
  }
}
</script>
