<template>
   <div>
      <Header pageTitle="Archive & History" icon="ArchiveIcon" color="blue" />
      <!-- Content -->
      <main class="flex flex-1 ml-6 mr-6 overflow-hidden">
        <div class="w-full px-2 sm:px-6 lg:px-8 py-8">

          <!-- Stats Overview -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="rounded-lg shadow-sm p-6" style="background: var(--card-bg); border: 1px solid var(--card-border);">
              <div class="flex items-center">
                <div class="p-3 rounded-lg" :style="{ background: 'var(--icon-bg-blue)', color: 'var(--icon-color-blue)' }">
                  <ReceiptIcon class="w-6 h-6" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium" :style="{ color: 'var(--text-sub)' }">Total Transactions</p>
                  <p class="text-2xl font-semibold" :style="{ color: 'var(--text-main)' }">{{ totalTransactions }}</p>
                </div>
              </div>
            </div>

            <div class="rounded-lg shadow-sm p-6" style="background: var(--card-bg); border: 1px solid var(--card-border);">
              <div class="flex items-center">
                <div class="p-3 rounded-lg" :style="{ background: 'var(--icon-bg-green)', color: 'var(--icon-color-green)' }">
                  <DollarIcon class="w-6 h-6" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium" :style="{ color: 'var(--text-sub)' }">Total Sales</p>
                  <p class="text-2xl font-semibold" :style="{ color: 'var(--text-main)' }">{{ formattedTotalSales }}</p>
                </div>
              </div>
            </div>

            <div class="rounded-lg shadow-sm p-6" style="background: var(--card-bg); border: 1px solid var(--card-border);">
              <div class="flex items-center">
                <div class="p-3 rounded-lg" :style="{ background: 'var(--icon-bg-purple)', color: 'var(--icon-color-purple)' }">
                  <TrendingUpIcon class="w-6 h-6" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium" :style="{ color: 'var(--text-sub)' }">Average Transaction</p>
                  <p class="text-2xl font-semibold" :style="{ color: 'var(--text-main)' }">{{ formattedAverageSale }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Ready for Use Message -->
          <div class="rounded-lg shadow-sm p-12 text-center" style="background: var(--card-bg); border: 1px solid var(--card-border);">
            <ArchiveIcon class="w-24 h-24 mx-auto mb-6" :style="{ color: 'var(--text-muted)' }" />
            <h2 class="text-2xl font-bold mb-4" :style="{ color: 'var(--text-main)' }">Archive & History Summary</h2>
            <p class="mb-6 max-w-2xl mx-auto" :style="{ color: 'var(--text-sub)' }">
              Use this page to monitor historical transactions, sales totals, and average ticket values.
              Detailed filters and exports are grouped below for daily operations.
            </p>

            <!-- Feature List -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto mt-8">
              <div class="text-left">
                <h3 class="font-semibold mb-3" :style="{ color: 'var(--text-main)' }">Transaction History</h3>
                <ul class="space-y-2 text-sm" :style="{ color: 'var(--text-sub)' }">
                  <li class="flex items-center">
                    <CheckIcon class="w-4 h-4 text-green-500 mr-2" />
                    View all past transactions
                  </li>
                  <li class="flex items-center">
                    <CheckIcon class="w-4 h-4 text-green-500 mr-2" />
                    Search and filter by date, amount, items
                  </li>
                  <li class="flex items-center">
                    <CheckIcon class="w-4 h-4 text-green-500 mr-2" />
                    Print or email past receipts
                  </li>
                </ul>
              </div>

              <div class="text-left">
                <h3 class="font-semibold mb-3" :style="{ color: 'var(--text-main)' }">Data Management</h3>
                <ul class="space-y-2 text-sm" :style="{ color: 'var(--text-sub)' }">
                  <li class="flex items-center">
                    <CheckIcon class="w-4 h-4 text-green-500 mr-2" />
                    Export data to CSV/Excel
                  </li>
                  <li class="flex items-center">
                    <CheckIcon class="w-4 h-4 text-green-500 mr-2" />
                    Backup and restore functionality
                  </li>
                  <li class="flex items-center">
                    <CheckIcon class="w-4 h-4 text-green-500 mr-2" />
                    Data analytics and reports
                  </li>
                </ul>
              </div>
            </div>

            <div class="mt-8">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium" style="background: var(--primary-100); color: var(--primary-700)">
                <ClockIcon class="w-4 h-4 mr-1" />
                Ready for Use
              </span>
            </div>
          </div>

        </div>
      </main>
    </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { formatPrice } from '@/utils/formatters'
import ArchiveIcon from '@/components/icons/ArchiveIcon.svg'
import ReceiptIcon from '@/components/icons/ReceiptIcon.svg'
import DollarIcon from '@/components/icons/DollarIcon.svg'
import TrendingUpIcon from '@/components/icons/TrendingUpIcon.svg'
import CheckIcon from '@/components/icons/CheckIcon.svg'
import ClockIcon from '@/components/icons/ClockIcon.svg'
import { safeCall } from '@/services/apiClient'
import Header from '@/layout/Header.vue'
const totalTransactions = ref(0)
const totalSales = ref(0)
const averageSale = ref(0)

const fetchArchiveStats = async () => {
  const result = await safeCall('retail.retail.api.common.get_dashboard_summary')
  if (result.success && result.data) {
    const s = result.data.sales || {}
    totalTransactions.value = s.invoice_count_week || 0
    totalSales.value = s.this_month || 0
    averageSale.value = totalTransactions.value > 0 ? Math.round(totalSales.value / totalTransactions.value) : 0
  }
}

onMounted(() => fetchArchiveStats())
const formattedTotalSales = computed(() => formatPrice(totalSales))
const formattedAverageSale = computed(() => formatPrice(averageSale))
</script>

<style scoped>
.bg-gray-50 {
  background-color: #f8fafc;
}

/* Additional color utilities */
.bg-blue-100 { background-color: #dbeafe; }
.text-blue-600 { color: #2563eb; }
.bg-green-100 { background-color: #dcfce7; }
.text-green-600 { color: #16a34a; }
.bg-purple-100 { background-color: #f3e8ff; }
.text-purple-600 { color: #9333ea; }
.bg-cyan-100 { background-color: #cffafe; }
.text-cyan-800 { color: #155e75; }

/* Hover effects */
.hover\:bg-gray-600:hover {
  background-color: #4b5563;
}

.hover\:bg-cyan-600:hover {
  background-color: #0891b2;
}

/* Transition effects */
.transition-colors {
  transition: background-color 0.2s ease;
}
</style>
