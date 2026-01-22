<template>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
      <h1 style="margin: 0;">Dashboard</h1>
      <button @click="generateReport" class="btn btn-primary" :disabled="generatingReport">
        {{ generatingReport ? 'Generating...' : 'Insurance Report' }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else>
      <!-- Top Stats Row -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Total Items</div>
          <div class="stat-value">{{ stats.total_items }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">Total Value</div>
          <div class="stat-value">{{ formatCurrency(stats.total_value) }}</div>
        </div>

        <div class="stat-card" :class="getCoverageClass(stats.insurance_analysis?.coverage_ratio)">
          <div class="stat-label">Coverage Ratio</div>
          <div class="stat-value">
            <span class="status-icon">
              <Check v-if="(stats.insurance_analysis?.coverage_ratio || 0) >= 100" :size="20" />
              <AlertTriangle v-else-if="(stats.insurance_analysis?.coverage_ratio || 0) >= 80" :size="20" />
              <X v-else :size="20" />
            </span>
            {{ stats.insurance_analysis?.coverage_ratio || 0 }}%
          </div>
          <div class="stat-subtext">{{ getCoverageText(stats.insurance_analysis?.coverage_ratio) }}</div>
        </div>

        <div class="stat-card" :class="getDocScoreClass(stats.coverage_gaps?.documentation_score)">
          <div class="stat-label">Doc Score</div>
          <div class="stat-value">
            <span class="status-icon">
              <Check v-if="(stats.coverage_gaps?.documentation_score || 0) >= 80" :size="20" />
              <AlertTriangle v-else-if="(stats.coverage_gaps?.documentation_score || 0) >= 50" :size="20" />
              <X v-else :size="20" />
            </span>
            {{ stats.coverage_gaps?.documentation_score || 0 }}%
          </div>
          <div class="stat-subtext">Items fully documented</div>
        </div>
      </div>

      <!-- Insurance Coverage Analysis -->
      <div class="card" style="margin-top: 16px;" v-if="stats.insurance_analysis">
        <h3 style="margin-bottom: 16px;">Insurance Coverage Analysis</h3>

        <div class="coverage-summary">
          <div class="coverage-row">
            <span>Inventory Value:</span>
            <span class="coverage-value">{{ formatCurrency(stats.insurance_analysis.total_inventory_value) }}</span>
          </div>
          <div class="coverage-row">
            <span>Policy Coverage:</span>
            <span class="coverage-value">{{ formatCurrency(stats.insurance_analysis.total_policy_coverage) }}</span>
          </div>
          <div class="coverage-row" :class="stats.insurance_analysis.coverage_gap >= 0 ? 'positive' : 'negative'">
            <span>{{ stats.insurance_analysis.coverage_gap >= 0 ? 'Surplus:' : 'Gap:' }}</span>
            <span class="coverage-value">{{ formatCurrency(Math.abs(stats.insurance_analysis.coverage_gap)) }}</span>
          </div>
        </div>

        <!-- Coverage Bar -->
        <div class="coverage-bar-container" v-if="stats.insurance_analysis.total_inventory_value > 0">
          <div
            class="coverage-bar"
            :style="{ width: Math.min(stats.insurance_analysis.coverage_ratio, 100) + '%' }"
            :class="getCoverageBarClass(stats.insurance_analysis.coverage_ratio)"
          ></div>
        </div>

        <!-- Per Property Breakdown -->
        <div v-if="stats.insurance_analysis.per_property?.length > 0" style="margin-top: 16px;">
          <div
            v-for="prop in stats.insurance_analysis.per_property"
            :key="prop.property_id"
            class="property-coverage-item"
            :class="'status-' + prop.status"
          >
            <div class="property-name">{{ prop.property_name }}</div>
            <div class="property-details">
              <span>Items: {{ formatCurrency(prop.inventory_value) }}</span>
              <span>Policy: {{ formatCurrency(prop.policy_coverage) }}</span>
              <span class="property-status">
                <span v-if="prop.status === 'covered'" class="status-inline"><Check :size="14" /> Covered</span>
                <span v-else-if="prop.status === 'warning'" class="status-inline"><AlertTriangle :size="14" /> Close</span>
                <span v-else-if="prop.status === 'under_insured'" class="status-inline"><X :size="14" /> Under-insured</span>
                <span v-else>— No items</span>
              </span>
            </div>
          </div>
        </div>

        <div v-else style="color: var(--text-secondary); font-size: 14px;">
          No properties configured. <router-link to="/settings">Add properties</router-link> to see coverage analysis.
        </div>
      </div>

      <!-- Documentation Gaps -->
      <div class="card" style="margin-top: 16px;">
        <h3 style="margin-bottom: 16px;">Documentation Gaps</h3>

        <div class="gaps-grid">
          <div
            class="gap-card"
            :class="{ 'has-issues': stats.coverage_gaps?.no_documents?.count > 0 }"
            @click="navigateToGap('no_documents')"
          >
            <div class="gap-icon"><FileText :size="24" /></div>
            <div class="gap-label">No Receipts</div>
            <div class="gap-count">{{ stats.coverage_gaps?.no_documents?.count || 0 }} items</div>
            <div class="gap-action" v-if="stats.coverage_gaps?.no_documents?.count > 0">View →</div>
          </div>

          <div
            class="gap-card"
            :class="{ 'has-issues': stats.coverage_gaps?.no_images?.count > 0 }"
            @click="navigateToGap('no_images')"
          >
            <div class="gap-icon"><ImageIcon :size="24" /></div>
            <div class="gap-label">No Images</div>
            <div class="gap-count">{{ stats.coverage_gaps?.no_images?.count || 0 }} items</div>
            <div class="gap-action" v-if="stats.coverage_gaps?.no_images?.count > 0">View →</div>
          </div>

          <div
            class="gap-card"
            :class="{ 'has-issues': stats.coverage_gaps?.high_value_undocumented?.count > 0, 'critical': stats.coverage_gaps?.high_value_undocumented?.count > 0 }"
            @click="navigateToGap('high_value_undocumented')"
          >
            <div class="gap-icon"><DollarSign :size="24" /></div>
            <div class="gap-label">High-Value*</div>
            <div class="gap-count">{{ stats.coverage_gaps?.high_value_undocumented?.count || 0 }} items</div>
            <div class="gap-action" v-if="stats.coverage_gaps?.high_value_undocumented?.count > 0">View →</div>
          </div>

          <div
            class="gap-card"
            :class="{ 'has-issues': stats.coverage_gaps?.no_purchase_info?.count > 0 }"
            @click="navigateToGap('no_purchase_info')"
          >
            <div class="gap-icon"><ShoppingCart :size="24" /></div>
            <div class="gap-label">No Purchase Info</div>
            <div class="gap-count">{{ stats.coverage_gaps?.no_purchase_info?.count || 0 }} items</div>
            <div class="gap-action" v-if="stats.coverage_gaps?.no_purchase_info?.count > 0">View →</div>
          </div>
        </div>

        <div class="threshold-note" v-if="stats.high_value_threshold">
          * Items over {{ formatCurrency(stats.high_value_threshold) }} without documentation
        </div>
      </div>

      <!-- Bottom Row: Recent Items and Expiring Warranties -->
      <div class="grid grid-2" style="margin-top: 16px;">
        <div class="card">
          <h3 style="margin-bottom: 16px;">Recent Items</h3>
          <div v-if="stats.recent_items?.length > 0">
            <div v-for="item in stats.recent_items.slice(0, 5)" :key="item.id"
                 @click="$router.push(`/items/${item.id}`)"
                 class="list-item">
              <div class="list-item-name">{{ item.name }}</div>
              <div class="list-item-meta">
                {{ item.category || 'No category' }} • {{ formatDate(item.created_at) }}
              </div>
            </div>
          </div>
          <div v-else style="color: var(--text-secondary); font-size: 14px;">
            No items added yet.
          </div>
        </div>

        <div class="card">
          <h3 style="margin-bottom: 16px; display: flex; align-items: center; gap: 6px;">
            <AlertTriangle v-if="stats.expiring_warranties?.length > 0" :size="18" style="color: var(--warning-color);" />
            <span>Expiring Warranties</span>
          </h3>
          <div v-if="stats.expiring_warranties?.length > 0">
            <div v-for="item in stats.expiring_warranties.slice(0, 5)" :key="item.id"
                 @click="$router.push(`/items/${item.id}`)"
                 class="list-item warranty-item">
              <div class="list-item-name">{{ item.name }}</div>
              <div class="list-item-meta warning">
                {{ item.days_remaining }} days ({{ formatDate(item.warranty_expiration) }})
              </div>
            </div>
          </div>
          <div v-else style="color: var(--text-secondary); font-size: 14px;">
            No warranties expiring in the next 30 days.
          </div>
        </div>
      </div>

      <!-- Items by Category/Location (collapsed by default) -->
      <div class="grid grid-2" style="margin-top: 16px;">
        <div class="card collapsible" :class="{ expanded: showCategories }">
          <h3 @click="showCategories = !showCategories" style="cursor: pointer; margin-bottom: 0; display: flex; justify-content: space-between; align-items: center;">
            <span>Items by Category</span>
            <ChevronDown v-if="showCategories" :size="18" />
            <ChevronRight v-else :size="18" />
          </h3>
          <div v-show="showCategories" style="margin-top: 16px;">
            <div v-for="cat in stats.items_by_category" :key="cat.name" style="margin-bottom: 8px;">
              <div style="display: flex; justify-content: space-between;">
                <span>{{ cat.name }}</span>
                <span style="font-weight: 600;">{{ cat.count }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card collapsible" :class="{ expanded: showLocations }">
          <h3 @click="showLocations = !showLocations" style="cursor: pointer; margin-bottom: 0; display: flex; justify-content: space-between; align-items: center;">
            <span>Items by Location</span>
            <ChevronDown v-if="showLocations" :size="18" />
            <ChevronRight v-else :size="18" />
          </h3>
          <div v-show="showLocations" style="margin-top: 16px;">
            <div v-for="loc in stats.items_by_location" :key="loc.name" style="margin-bottom: 8px;">
              <div style="display: flex; justify-content: space-between;">
                <span>{{ loc.name }}</span>
                <span style="font-weight: 600;">{{ loc.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { Check, AlertTriangle, X, FileText, ImageIcon, DollarSign, ShoppingCart, ChevronDown, ChevronRight } from 'lucide-vue-next'

export default {
  name: 'Dashboard',
  components: {
    Check,
    AlertTriangle,
    X,
    FileText,
    ImageIcon,
    DollarSign,
    ShoppingCart,
    ChevronDown,
    ChevronRight
  },
  setup() {
    const router = useRouter()
    const loading = ref(true)
    const generatingReport = ref(false)
    const selectedPropertyId = inject('selectedPropertyId')
    const showCategories = ref(false)
    const showLocations = ref(false)
    const stats = ref({
      total_items: 0,
      total_value: 0,
      items_by_category: [],
      items_by_location: [],
      recent_items: [],
      expiring_warranties: [],
      coverage_gaps: null,
      insurance_analysis: null,
      high_value_threshold: 5000
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
      if (value === null || value === undefined) return '0 kr'
      return new Intl.NumberFormat('nb-NO', {
        style: 'currency',
        currency: 'NOK',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value)
    }

    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleDateString('nb-NO')
    }

    const getCoverageClass = (ratio) => {
      if (ratio >= 100) return 'status-good'
      if (ratio >= 80) return 'status-warning'
      return 'status-danger'
    }

    const getCoverageIcon = (ratio) => {
      if (ratio >= 100) return '✓'
      if (ratio >= 80) return '⚠️'
      return '✗'
    }

    const getCoverageText = (ratio) => {
      if (ratio >= 100) return 'Fully covered'
      if (ratio >= 80) return 'Nearly covered'
      return 'Under-insured'
    }

    const getCoverageBarClass = (ratio) => {
      if (ratio >= 100) return 'bar-good'
      if (ratio >= 80) return 'bar-warning'
      return 'bar-danger'
    }

    const getDocScoreClass = (score) => {
      if (score >= 80) return 'status-good'
      if (score >= 50) return 'status-warning'
      return 'status-danger'
    }

    const getDocScoreIcon = (score) => {
      if (score >= 80) return '✓'
      if (score >= 50) return '⚠️'
      return '✗'
    }

    const navigateToGap = (gapType) => {
      const gapData = stats.value.coverage_gaps?.[gapType]
      if (gapData?.count > 0) {
        router.push({ path: '/items', query: { gap_filter: gapType } })
      }
    }

    const generateReport = async () => {
      if (!selectedPropertyId.value) {
        alert('Please select a property first')
        return
      }
      generatingReport.value = true
      try {
        const reportUrl = api.getInsuranceReportUrl(selectedPropertyId.value)
        const token = localStorage.getItem('token')
        const response = await fetch(reportUrl, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
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
      showCategories,
      showLocations,
      formatCurrency,
      formatDate,
      getCoverageClass,
      getCoverageIcon,
      getCoverageText,
      getCoverageBarClass,
      getDocScoreClass,
      getDocScoreIcon,
      navigateToGap,
      generateReport
    }
  }
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 16px;
  text-align: center;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
}

.stat-subtext {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.status-icon {
  margin-right: 4px;
  display: inline-flex;
  align-items: center;
}

.status-inline {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.status-good { border-color: var(--success-color); }
.status-good .stat-value { color: var(--success-color); }

.status-warning { border-color: var(--warning-color); }
.status-warning .stat-value { color: var(--warning-color); }

.status-danger { border-color: var(--error-color); }
.status-danger .stat-value { color: var(--error-color); }

/* Coverage Analysis */
.coverage-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.coverage-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--surface-hover);
  border-radius: 4px;
}

.coverage-row.positive .coverage-value { color: var(--success-color); }
.coverage-row.negative .coverage-value { color: var(--error-color); }

.coverage-value {
  font-weight: 600;
}

.coverage-bar-container {
  height: 8px;
  background: var(--surface-hover);
  border-radius: 4px;
  overflow: hidden;
}

.coverage-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.bar-good { background: var(--success-color); }
.bar-warning { background: var(--warning-color); }
.bar-danger { background: var(--error-color); }

.property-coverage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-top: 8px;
  background: var(--surface-hover);
  border-radius: 8px;
  border-left: 4px solid var(--border-color);
}

.property-coverage-item.status-covered { border-left-color: var(--success-color); }
.property-coverage-item.status-warning { border-left-color: var(--warning-color); }
.property-coverage-item.status-under_insured { border-left-color: var(--error-color); }

.property-name {
  font-weight: 600;
}

.property-details {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

.property-status {
  font-weight: 500;
}

/* Documentation Gaps */
.gaps-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

@media (max-width: 800px) {
  .gaps-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.gap-card {
  background: var(--surface-hover);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  cursor: default;
  transition: all 0.2s;
}

.gap-card.has-issues {
  cursor: pointer;
  border-color: var(--warning-color);
}

.gap-card.has-issues:hover {
  background: var(--surface);
  transform: translateY(-2px);
}

.gap-card.critical {
  border-color: var(--error-color);
  background: rgba(239, 68, 68, 0.1);
}

.gap-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.gap-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.gap-count {
  font-size: 18px;
  font-weight: 600;
}

.gap-action {
  margin-top: 8px;
  font-size: 12px;
  color: var(--primary-color);
}

.threshold-note {
  margin-top: 12px;
  font-size: 12px;
  color: var(--text-secondary);
  font-style: italic;
}

/* List Items */
.list-item {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.2s;
}

.list-item:hover {
  background: var(--surface-hover);
}

.list-item:last-child {
  border-bottom: none;
}

.list-item-name {
  font-weight: 500;
}

.list-item-meta {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.list-item-meta.warning {
  color: var(--warning-color);
}

/* Collapsible */
.collapsible h3 {
  transition: margin 0.2s;
}
</style>
