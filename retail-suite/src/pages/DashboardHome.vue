<!-- DashboardHome.vue - POS Dashboard -->
<template>
  <div :class="isDark ? 'theme-dark' : 'theme-light'">
    <header class="mx-3 mt-1 sticky top-0 z-10 rounded-xl shadow-sm" :style="{ background: 'var(--card-bg)', borderBottom: '1px solid var(--card-border)' }">
      <div class="px-4 py-3 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <ChartIcon class="w-8 h-8" :style="{ color: primaryColor }" />
          <h1 class="text-lg font-bold" :style="{ color: 'var(--text-main)' }">Dashboard</h1>
        </div>
        <button @click="loadDashboard" :disabled="isLoading" class="px-4 py-2 rounded-lg text-white text-sm font-medium transition" :style="{ background: primaryColor }">
          {{ isLoading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto p-6 space-y-6">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="card in kpiCards" :key="card.label" class="rounded-xl p-4 shadow-sm" :style="{ background: card.bg, border: '1px solid var(--card-border)' }">
          <p class="text-xs font-medium uppercase tracking-wide" :style="{ color: 'var(--text-muted)' }">{{ card.label }}</p>
          <p class="text-2xl font-bold mt-1" :style="{ color: 'var(--text-main)' }">{{ card.value }}</p>
          <p v-if="card.sub" class="text-xs mt-1" :style="{ color: card.subColor || 'var(--text-muted)' }">{{ card.sub }}</p>
        </div>
      </div>

      <div class="flex gap-2 flex-wrap">
        <button v-for="span in timeSpans" :key="span.key" @click="selectedSpan = span.key" class="px-4 py-2 rounded-lg text-sm font-medium transition"
          :style="selectedSpan === span.key ? { background: primaryColor, color: '#fff' } : { background: 'var(--item-bg)', color: 'var(--text-main)', border: '1px solid var(--item-border)' }">
          {{ span.label }}
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div class="rounded-xl p-5" :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }">
          <p class="text-sm font-semibold mb-3" :style="{ color: 'var(--text-main)' }">Sales Overview</p>
          <div class="space-y-2">
            <div v-for="row in salesBreakdown" :key="row.key" class="flex justify-between text-sm">
              <span :style="{ color: 'var(--text-muted)' }">{{ row.label }}</span>
              <span class="font-semibold" :style="{ color: 'var(--text-main)' }">{{ formatPrice(row.value) }}</span>
            </div>
          </div>
        </div>

        <div class="rounded-xl p-5" :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }">
          <p class="text-sm font-semibold mb-3" :style="{ color: 'var(--text-main)' }">Cash Flow</p>
          <div class="space-y-2">
            <div class="flex justify-between text-sm"><span :style="{ color: 'var(--text-muted)' }">Balance</span><span class="font-semibold" :style="{ color: cashBalance >= 0 ? 'var(--icon-color-green)' : 'var(--warning-border)' }">{{ formatPrice(cashBalance) }}</span></div>
            <div class="flex justify-between text-sm"><span :style="{ color: 'var(--text-muted)' }">Cash In</span><span class="font-semibold" :style="{ color: 'var(--icon-color-green)' }">{{ formatPrice(cashIn) }}</span></div>
            <div class="flex justify-between text-sm"><span :style="{ color: 'var(--text-muted)' }">Cash Out</span><span class="font-semibold" :style="{ color: 'var(--warning-border)' }">{{ formatPrice(cashOut) }}</span></div>
            <div class="flex justify-between text-sm border-t pt-2" :style="{ borderColor: 'var(--card-border)' }"><span :style="{ color: 'var(--text-muted)' }">Net</span><span class="font-semibold" :style="{ color: netFlow >= 0 ? 'var(--icon-color-green)' : 'var(--warning-border)' }">{{ formatPrice(netFlow) }}</span></div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div class="rounded-xl p-5" :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }">
          <p class="text-sm font-semibold mb-3" :style="{ color: 'var(--text-main)' }">Top Items (Today)</p>
          <div v-if="topItems.length === 0" class="text-sm" :style="{ color: 'var(--text-muted)' }">No sales today</div>
          <div v-for="(item, i) in topItems" :key="i" class="flex justify-between items-center py-2" :style="{ borderBottom: i < topItems.length - 1 ? '1px solid var(--card-border)' : '' }">
            <div class="flex items-center gap-2"><span class="text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center" :style="{ background: primaryColor, color: '#fff' }">{{ i + 1 }}</span><span class="text-sm" :style="{ color: 'var(--text-main)' }">{{ item.name }}</span></div>
            <div class="text-right"><p class="text-xs font-semibold" :style="{ color: 'var(--text-main)' }">x{{ item.qty }}</p><p class="text-xs" :style="{ color: 'var(--text-muted)' }">{{ formatPrice(item.amount) }}</p></div>
          </div>
        </div>

        <div class="rounded-xl p-5" :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }">
          <p class="text-sm font-semibold mb-3" :style="{ color: 'var(--text-main)' }">Daily Trend (7 Days)</p>
          <div class="space-y-1">
            <div v-for="day in dailyTrend" :key="day.date" class="flex items-center gap-3">
              <span class="text-xs w-16" :style="{ color: 'var(--text-muted)' }">{{ formatDay(day.date) }}</span>
              <div class="flex-1 h-6 rounded" :style="{ background: 'var(--item-bg)' }"><div class="h-full rounded" :style="{ width: barWidth(day.total, maxTrend), background: primaryColor, minWidth: '2px' }"></div></div>
              <span class="text-xs w-20 text-right font-semibold" :style="{ color: 'var(--text-main)' }">{{ formatPrice(day.total) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-xl p-5" :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }">
        <p class="text-sm font-semibold mb-3" :style="{ color: 'var(--text-main)' }">Supplier Purchases (This Month)</p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

          <div v-for="sup in purchases.top_suppliers" :key="sup.name" class="rounded-lg p-3" :style="{ background: 'var(--item-bg)', border: '1px solid var(--item-border)' }">
            <p class="text-sm font-semibold truncate" :style="{ color: 'var(--text-main)' }">{{ sup.name }}</p>
            <p class="text-lg font-bold mt-1" :style="{ color: primaryColor }">{{ formatPrice(sup.total) }}</p>
            <p class="text-xs" :style="{ color: 'var(--text-muted)' }">{{ sup.count }} invoices</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { formatPrice } from '@/utils/formatters'
import ChartIcon from '@/components/icons/ChartIcon.svg'
import { safeCall } from '@/services/apiClient'

const settingsStore = useSettingsStore()
const isDark = computed(() => settingsStore.settings.appearance.theme === 'dark')
const primaryColor = computed(() => settingsStore.settings.appearance?.primaryColor || '#06b6d4')

const isLoading = ref(false)
const dashboard = ref({ sales: {}, profit: {}, cash: {}, purchases: {}, top_items: [], daily_trend: [] })
const selectedSpan = ref('this_week')
const timeSpans = [{ key: 'today', label: 'Today' },{ key: 'this_week', label: 'This Week' },{ key: 'this_month', label: 'This Month' }]

const salesBreakdown = computed(() => [
  { key: 'today', label: 'Today', value: dashboard.value.sales?.today || 0 },
  { key: 'this_week', label: 'This Week', value: dashboard.value.sales?.this_week || 0 },
  { key: 'this_month', label: 'This Month', value: dashboard.value.sales?.this_month || 0 },
  { key: 'last_month', label: 'Last Month', value: dashboard.value.sales?.last_month || 0 },
])
const profitBreakdown = computed(() => {
  const p = dashboard.value.profit || {}
  return [
    { key: 'today', label: 'Today', value: p.today?.profit || 0 },
    { key: 'this_week', label: 'This Week', value: p.this_week?.profit || 0 },
    { key: 'this_month', label: 'This Month', value: p.this_month?.profit || 0 },
  ]
})

const cashBalance = computed(() => dashboard.value.cash?.balance || 0)
const cashIn = computed(() => {
  const f = dashboard.value.cash || {}
  return selectedSpan.value === 'today' ? f.flow_today?.cash_in || 0 : selectedSpan.value === 'this_week' ? f.flow_week?.cash_in || 0 : f.flow_month?.cash_in || 0
})
const cashOut = computed(() => {
  const f = dashboard.value.cash || {}
  return selectedSpan.value === 'today' ? f.flow_today?.cash_out || 0 : selectedSpan.value === 'this_week' ? f.flow_week?.cash_out || 0 : f.flow_month?.cash_out || 0
})
const netFlow = computed(() => cashIn.value - cashOut.value)

const kpiCards = computed(() => [
  { label: 'Sales Today', value: formatPrice(dashboard.value.sales?.today || 0), bg: 'var(--info-bg)', sub: (dashboard.value.sales?.invoice_count_today || 0) + ' invoices' },
  { label: 'Sales Month', value: formatPrice(dashboard.value.sales?.this_month || 0), bg: 'var(--card-bg)', sub: null },

  { label: 'Cash Balance', value: formatPrice(cashBalance.value), bg: cashBalance.value >= 0 ? 'var(--info-bg)' : 'var(--warning-bg)', sub: null },
])

const topItems = computed(() => dashboard.value.top_items || [])
const dailyTrend = computed(() => dashboard.value.daily_trend || [])
const maxTrend = computed(() => Math.max(...dailyTrend.value.map(d => d.total || 0), 1))
const purchases = computed(() => dashboard.value.purchases || {})

const barWidth = (val, max) => Math.max(2, (val / max) * 100) + '%'
const formatDay = (dateStr) => { try { return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'short' }) } catch { return dateStr } }

const loadDashboard = async () => {
  isLoading.value = true
  try {
    const result = await safeCall('retail.retail.api.common.get_dashboard_summary')
    if (result.success && result.data) dashboard.value = result.data
  } catch (e) {
    console.error('Dashboard load failed:', e)
  } finally { isLoading.value = false }
}
const activeFilter = ref('today')
const quickFilters = [
  { key: 'today', label: 'Today' },
  { key: 'yesterday', label: 'Yesterday' },
  { key: 'week', label: 'This Week' },
  { key: 'month', label: 'This Month' },
  { key: 'last_month', label: 'Last Month' },
  { key: 'year', label: 'This Year' },
]
const applyQuickFilter = (key) => { activeFilter.value = key }

onMounted(() => loadDashboard())
</script>