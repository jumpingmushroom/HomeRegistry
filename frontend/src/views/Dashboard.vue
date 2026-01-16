<template>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
      <h1 style="margin: 0;">Dashboard</h1>
      <button @click="generateReport" class="btn btn-primary" :disabled="generatingReport">
        {{ generatingReport ? 'Generating...' : '📄 Insurance Report' }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else>
      <div class="grid grid-2">
        <div class="card">
          <h3 style="color: var(--text-secondary); font-size: 14px; margin-bottom: 8px;">Total Items</h3>
          <div style="font-size: 32px; font-weight: 600;">{{ stats.total_items }}</div>
        </div>

        <div class="card">
          <h3 style="color: var(--text-secondary); font-size: 14px; margin-bottom: 8px;">Total Value</h3>
          <div style="font-size: 32px; font-weight: 600;">{{ formatCurrency(stats.total_value) }}</div>
        </div>
      </div>

      <div class="grid grid-2" style="margin-top: 16px;">
        <div class="card">
          <h3 style="margin-bottom: 16px;">Items by Category</h3>
          <div v-for="cat in stats.items_by_category" :key="cat.name" style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between;">
              <span>{{ cat.name }}</span>
              <span style="font-weight: 600;">{{ cat.count }}</span>
            </div>
          </div>
        </div>

        <div class="card">
          <h3 style="margin-bottom: 16px;">Items by Location</h3>
          <div v-for="loc in stats.items_by_location" :key="loc.name" style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between;">
              <span>{{ loc.name }}</span>
              <span style="font-weight: 600;">{{ loc.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="margin-top: 16px;">
        <h3 style="margin-bottom: 16px;">Recent Items</h3>
        <div v-for="item in stats.recent_items" :key="item.id"
             @click="$router.push(`/items/${item.id}`)"
             style="padding: 12px; border-bottom: 1px solid var(--divider-color); cursor: pointer;">
          <div style="font-weight: 500;">{{ item.name }}</div>
          <div style="font-size: 12px; color: var(--text-secondary);">
            {{ item.category }} • {{ item.location }} • {{ formatDate(item.created_at) }}
          </div>
        </div>
      </div>

      <div class="card" style="margin-top: 16px;" v-if="stats.expiring_warranties.length > 0">
        <h3 style="margin-bottom: 16px;">⚠️ Expiring Warranties</h3>
        <div v-for="item in stats.expiring_warranties" :key="item.id"
             @click="$router.push(`/items/${item.id}`)"
             style="padding: 12px; border-bottom: 1px solid var(--divider-color); cursor: pointer;">
          <div style="font-weight: 500;">{{ item.name }}</div>
          <div style="font-size: 12px; color: var(--warning-color);">
            Expires in {{ item.days_remaining }} days ({{ formatDate(item.warranty_expiration) }})
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, inject, watch } from 'vue'
import api from '../services/api'

export default {
  name: 'Dashboard',
  setup() {
    const loading = ref(true)
    const generatingReport = ref(false)
    const selectedPropertyId = inject('selectedPropertyId')
    const stats = ref({
      total_items: 0,
      total_value: 0,
      items_by_category: [],
      items_by_location: [],
      recent_items: [],
      expiring_warranties: []
    })

    const loadStats = async () => {
      loading.value = true
      try {
        const { data } = await api.getDashboardStats(selectedPropertyId.value)
        stats.value = data
      } catch (error) {
        console.error('Failed to load stats:', error)
      } finally {
        loading.value = false
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

    const generateReport = async () => {
      if (!selectedPropertyId.value) {
        alert('Please select a property first')
        return
      }
      generatingReport.value = true
      try {
        // Fetch the PDF and trigger download
        const reportUrl = api.getInsuranceReportUrl(selectedPropertyId.value)
        const response = await fetch(reportUrl)
        if (!response.ok) throw new Error('Failed to generate report')

        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `insurance_report_${selectedPropertyId.value}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Failed to generate report:', error)
        alert('Failed to generate report. Please try again.')
      } finally {
        generatingReport.value = false
      }
    }

    // Reload stats when selected property changes
    watch(selectedPropertyId, () => {
      if (selectedPropertyId.value) {
        loadStats()
      }
    })

    onMounted(() => {
      if (selectedPropertyId.value) {
        loadStats()
      }
    })

    return {
      loading,
      generatingReport,
      stats,
      formatCurrency,
      formatDate,
      generateReport
    }
  }
}
</script>
