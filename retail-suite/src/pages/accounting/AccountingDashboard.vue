<!-- Dashboard Accounting.vue -->
<template>
    <div>
      <main class="flex flex-col flex-1">

        <!-- Header -->
        <Header pageTitle="Accounting Dashboard" icon="BarChart3" color="blue" />

        <!-- Stats -->
        <section class="px-2 py-2">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
            <StatsCard title="Total Revenue" :value="formatCurrency(stats.totalRevenue)" icon="TrendingUp" color="green" />
            <StatsCard title="Total Expenses" :value="formatCurrency(stats.totalExpenses)" icon="TrendingDown" color="red" />
            <StatsCard title="Net Profit" :value="formatCurrency(stats.netProfit)" icon="DollarSign" color="blue" />
            <StatsCard title="Accounts Payable" :value="formatCurrency(stats.accountsPayable)" icon="Clock" color="orange" />
          </div>
        </section>

        <!-- Cards Grid -->
        <section class="px-2 pb-2">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <DashboardCard title="Customers Invoices" description="Create, View and manage customer invoices" icon="FileCheck" color="green" @click="navigateTo('Invoices')" />
            <DashboardCard title="Suppliers Invoices" description="Create, View and manage supplier invoice" icon="FileCheck" color="orange" @click="navigateTo('SuppliersInvoices')" />
            <DashboardCard
              title="Expenses Breakdown"
              description="Detailed expense categories"
              icon="PieChart"
              @click="navigateTo('Expenses')"
            />
            <!-- Accounts Receivable -->
            <DashboardCard
              title="Accounts Receivable"
              description="Customer invoices & collections"
              icon="CreditCard"
              @click="navigateTo('AccountsReceivable')"
            />

            <!-- Accounts Payable -->
            <DashboardCard
              title="Accounts Payable"
              description="Supplier bills & payments"
              icon="Wallet"
              @click="navigateTo('AccountsPayable')"
            />

            <!-- SalesAnalytics -->
            <DashboardCard
              title="Sales Analytics"
              description="Sales Analytics "
              icon="BarChart3"
              @click="navigateTo('SalesAnalytics')"
            />

          </div>
        </section>

        <!-- Recent Activity -->
        <section class="px-2 pb-2">
          <div
            class="rounded-xl shadow-sm p-6"
            :style="{
              background: 'var(--card-bg)',
              border: '1px solid var(--card-border)'
            }"
          >
            <h2 class="text-lg font-semibold mb-4" :style="{ color: 'var(--text-main)' }">
              Recent Accounting Activity
            </h2>
            <div class="space-y-3">
              <div
                v-for="activity in recentActivities"
                :key="activity.id"
                class="flex items-center justify-between pb-3"
                :style="{ borderBottom: '1px solid var(--card-border)' }"
              >
                <div class="flex items-center gap-3">
                  <div :class="['w-10 h-10 rounded-full flex items-center justify-center', activity.bgColor]">
                    <component :is="activity.icon" class="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p class="text-sm font-medium" :style="{ color: 'var(--text-main)' }">
                      {{ activity.title }}
                    </p>
                    <p class="text-xs" :style="{ color: 'var(--text-muted)' }">
                      {{ activity.timestamp }}
                    </p>
                  </div>
                </div>
                <span :class="['text-xs font-medium px-2 py-1 rounded', activity.badgeClass]">
                  {{ activity.status }}
                </span>
              </div>
            </div>
          </div>
        </section>

      </main>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import Sidebar from '@/layout/Sidebar.vue'
import StatsCard from '@/layout/StatsCard.vue'
import DashboardCard from '@/components/modals/DashboardCard.vue'
import { useRouter } from 'vue-router'
import Header from '@/layout/Header.vue'
import { formatCurrency } from '@/utils/formatters'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Clock,
  List,
  BookOpen,
  Layers,
  Scale,
  FileText,
  CreditCard,
  FileCheck,
  Receipt,
  Users,
  Truck,
  Wallet
} from 'lucide-vue-next'
import { useSettingsStore } from '@/stores/settings'
import { safeCall } from '@/services/apiClient'

    // stores
    const settingsStore = useSettingsStore()
    const currencyCode = settingsStore?.settings?.store?.currencyCode || "USD"
    const locale = settingsStore?.settings?.store?.local || "en-US"

    const router = useRouter()
    // const accountingStore = useAccountingStore()

    const stats = reactive({
      totalRevenue: 0,
      totalExpenses: 0,
      netProfit: 0,
      accountsPayable: 0
    })

    const recentActivities = ref([
      {
        id: 1,
        title: 'New invoice created',
        timestamp: '1 hour ago',
        status: 'Created',
        bgColor: 'bg-green-500',
        icon: FileCheck,
        badgeClass: 'bg-green-100 text-green-800'
      },
      {
        id: 2,
        title: 'Customer added',
        timestamp: '3 hours ago',
        status: 'Added',
        bgColor: 'bg-blue-500',
        icon: Users,
        badgeClass: 'bg-blue-100 text-blue-800'
      },
      {
        id: 3,
        title: 'Supplier order received',
        timestamp: '5 hours ago',
        status: 'Received',
        bgColor: 'bg-purple-500',
        icon: Truck,
        badgeClass: 'bg-purple-100 text-purple-800'
      }
    ])

    const calculateStats = async () => {
      try {
        const result = await safeCall('retail.retail.api.common.get_dashboard_summary')
        if (result.success && result.data) {
          const s = result.data.sales || {}
          const c = result.data.cash || {}
          const p = result.data.purchases || {}
          stats.totalRevenue = s.this_month || 0
          stats.totalExpenses = p.this_month || 0
          stats.netProfit = (s.this_month || 0) - (p.this_month || 0)
          stats.accountsPayable = c.flow_month?.cash_out || 0
        }
      } catch (e) {
        console.error('Accounting dashboard failed:', e)
      }
    }

    const navigateTo = (route) => {
      console.log('route', route)
      router.push({ name: route })
    }

    onMounted(() => {
    //   accountingStore.loadAccountingData()
      calculateStats()
    })
</script>
