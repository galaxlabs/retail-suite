<template>
<div class="fixed inset-0  bg-opacity-50 flex items-center justify-center p-4 z-[9999]"
        v-if="shift">
    <!-- Modal Background -->
    <div
      class="absolute inset-0"
      @click="$emit('close')"
    ></div>

    <!-- Modal Content -->
    <div class="relative bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-screen overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 rounded-lg mr-3">
              <InfoIcon class="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Current Shift Details</h3>
              <p class="text-sm text-gray-600">
                Shift ID: {{ shift.name }}
              </p>
            </div>
          </div>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-colors duration-200 p-1"
          >
            <CloseIcon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="overflow-y-auto max-h-96">
        <!-- Basic Information -->
        <div class="px-6 py-4 border-b border-gray-100">
          <h4 class="text-md font-semibold text-gray-900 mb-4 flex items-center">
            <UserIcon class="w-5 h-5 text-blue-600 mr-2" />
            Basic Information
          </h4>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-600">Cashier:</span>
              <div class="font-medium text-gray-900">{{ shift.user }}</div>
              <div class="text-xs text-gray-500">{{ getUserRole(shift.user) }}</div>
            </div>
            <div>
              <span class="text-gray-600">Status:</span>
              <div class="flex items-center mt-1">
                <div
                  class="w-2 h-2 rounded-full mr-2"
                  :class="{
                    'bg-green-500': shift.status === 'Open',
                    'bg-red-500': shift.status === 'Closed'
                  }"
                ></div>
                <span class="font-medium capitalize" :class="{
                  'text-green-600': shift.status === 'open',
                  'text-red-600': shift.status === 'closed'
                }">
                  {{ shift.status }}
                </span>
              </div>
            </div>
            <div>
              <span class="text-gray-600">Started:</span>
              <div class="font-medium">{{ formatDateTime12h(shift.period_start_date)}}</div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-gray-600">Duration:</span>

              <div class="font-medium flex items-center gap-1">
                <ClockIcon class="w-4 h-4 text-gray-600" />
                <span>{{ formatDuration(shift) }}</span>
              </div>
            </div>

          </div>

          <!-- Notes -->
          <div v-if="shift.notes" class="mt-4">
            <span class="text-gray-600 text-sm">Opening Notes:</span>
            <div class="mt-1 p-2 bg-gray-50 rounded text-sm">{{ shift.notes }}</div>
          </div>
        </div>

        <!-- Financial Summary -->
        <div class="px-6 py-4 border-b border-gray-100">
          <h4 class="text-md font-semibold text-gray-900 mb-4 flex items-center">
            <CashIcon class="w-5 h-5 text-green-600 mr-2" />
            Financial Summary
          </h4>
          <div class="grid grid-cols-2 gap-4">
            <!-- Opening Balance -->
            <div class="bg-blue-50 p-3 rounded-lg">
              <div class="text-sm text-gray-600">Opening Balance</div>
              <div class="text-lg font-semibold text-blue-900">
                {{ formatPrice(shift.openingBalance || 0) }}
              </div>
            </div>

            <!-- Total Sales -->
            <div class="bg-green-50 p-3 rounded-lg">
              <div class="text-sm text-gray-600">Total Sales</div>
              <div class="text-lg font-semibold text-green-900">
                {{ formatPrice(shift.totalSales || 0) }}
              </div>
            </div>

            <!-- Expected Cash -->
            <div class="bg-yellow-50 p-3 rounded-lg">
              <div class="text-sm text-gray-600">Expected Cash</div>
              <div class="text-lg font-semibold text-yellow-900">
                {{ formatPrice(expectedCash) }}
              </div>
            </div>

            <!-- Average Transaction -->
            <div class="bg-purple-50 p-3 rounded-lg">
              <div class="text-sm text-gray-600">Avg. Transaction</div>
              <div class="text-lg font-semibold text-purple-900">
                {{ formatPrice(averageTransaction) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Transaction Summary -->
        <div class="px-6 py-4 border-b border-gray-100">
          <h4 class="text-md font-semibold text-gray-900 mb-4 flex items-center">
            <ReceiptIcon class="w-5 h-5 text-purple-600 mr-2" />
            Transaction Summary
          </h4>
          <div class="grid grid-cols-3 gap-4 text-center">
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ shift.transactions.length || 0 }}</div>
              <div class="text-sm text-gray-600">Total Transactions</div>
            </div>
            <div>
              <div class="text-2xl font-bold text-green-600">{{ completedTransactions }}</div>
              <div class="text-sm text-gray-600">Completed</div>
            </div>
            <div>
              <div class="text-2xl font-bold text-blue-600">{{ formatPrice(largestTransaction) }}</div>
              <div class="text-sm text-gray-600">Largest Sale</div>
            </div>
          </div>
        </div>

        <!-- Recent Transactions -->
        <div class="px-6 py-4">
          <h4 class="text-md font-semibold text-gray-900 mb-4 flex items-center">
            <ChartIcon class="w-5 h-5 text-indigo-600 mr-2" />
            Recent Transactions
            <span class="ml-2 text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">
              Last {{ Math.min(5, recentTransactions.length) }}
            </span>
          </h4>

          <div v-if="recentTransactions.length > 0" class="space-y-2">
            <div
              v-for="(transaction, index) in recentTransactions.slice(0, 5)"
              :key="transaction.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm"
            >
              <div class="flex items-center">
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <span class="text-blue-600 font-medium text-xs">#{{ index + 1 }}</span>
                </div>
                <div>
                  <div class="font-medium">{{ formatPrice(transaction.grand_total) }}</div>
                  <div class="text-gray-500 text-xs">{{ transaction.posting_time }}</div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-gray-600">{{ transaction.total_qty || 0 }} items</div>
                <div class="text-xs text-gray-500 capitalize">{{ transaction.paymentMethod || 'cash' }}</div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-500">
            <ReceiptIcon class="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No transactions yet</p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex space-x-3">
        <button
          @click="exportShiftData"
          class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
        >
          <ExportIcon class="w-4 h-4 mr-2 text-white" />

          Export Data
        </button>
        <button
          @click="printShiftSummary"
          class="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors duration-200 flex items-center justify-center"
        >
          <PrintIcon class="w-4 h-4 mr-2" />
          Print Summary
        </button>
        <button
          @click="$emit('close')"
          class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors duration-200"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useShiftStore } from '@/stores/shift'
import { formatPrice } from '../../utils/formatters';
import { formatDateTime12h } from '../../utils/formatters';
import InfoIcon from '@/components/icons/InfoIcon.svg'
import CloseIcon from '@/components/icons/CloseIcon.svg'
import UserIcon from '@/components/icons/UserIcon.svg'
import CashIcon from '@/components/icons/CashIcon.svg'
import ReceiptIcon from '@/components/icons/ReceiptIcon.svg'
import ChartIcon from '@/components/icons/ChartIcon.svg'
import ExportIcon from '@/components/icons/ExportIcon.svg'
import PrintIcon from '@/components/icons/PrintIcon.svg'
import ClockIcon from '@/components/icons/ClockIcon.svg'

  const props = defineProps( {
    shift: {
      type: Object,
      required: true
    }
  })
  const emit = defineEmits(['close'])

  console.log('Shift prop:', props.shift)
  const shiftStore = useShiftStore()
  console.log('==> shiftStore.$state.CurrentUserInfo',shiftStore.$state.CurrentUserInfo)
  // Computed properties
  const expectedCash = computed(() => {
    return (props.shift.openingBalance || 0) + (props.shift.totalSales || 0)
  })

  const averageTransaction = computed(() => {
    const total = props.shift.totalTransactions || 0
    const sales = props.shift.totalSales || 0
    return total > 0 ? sales / total : 0
  })

  const completedTransactions = computed(() => {
    return props.shift.transactions?.length || 0
  })

  const largestTransaction = computed(() => {
    const transactions = props.shift.transactions || []
    console.log("largestTransaction",transactions)
    return transactions.length > 0 ?
      Math.max(...transactions.map(t => t.grand_total || 0)) : 0
  })

  const recentTransactions = computed(() => {
    const transactions = props.shift.transactions || []
    console.log('recentTransactions', [...transactions].reverse())
    return [...transactions].reverse() // Most recent first
  })




  const formatTime = (dateTime) => {
    return new Date(dateTime).toLocaleTimeString('id-ID', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatDuration = (shift) => {
    const start = new Date(shift.period_start_date)
    const end = shift.period_end_date ? new Date(shift.period_end_date) : new Date()
    const duration = end.getTime() - start.getTime()

    const hours = Math.floor(duration / (1000 * 60 * 60))
    const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60))

    return `${hours}h ${minutes}m`
  }


  function getUserRole(userId) {
      const shiftStore = useShiftStore();

      // هات معلومات اليوزر سے الـ store
      const userInfo = shiftStore.$state.CurrentUserInfo;

      // لو مفيش يوزر أو نام مش مطابق
      if (!userInfo || userInfo.user !== userId) {
        return null;
      }

      // const userRoles = userInfo.roles || [];
      // const shiftRoles = ['Cashier', 'System Manager', 'Sales User', 'Administrator'];
        const userRoles = (userInfo.roles || []).map(r => r.trim().toLowerCase());
        const shiftRoles = ['Cashier', 'System Manager', 'Sales User', 'Administrator']
  .map(r => r.trim().toLowerCase());
      // هات أول رول سے userRoles موجود داخل shiftRoles
      const match = userRoles.find(role => shiftRoles.includes(role));
      console.log('match',match)
      console.log('userRoles',userRoles)
      console.log('shiftRoles',shiftRoles)
      return match || null;
}

  // Actions
  const exportShiftData = async () => {
    try {
      const exportData = await shiftStore.exportShiftData(props.shift.id)

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `shift_${props.shift.id}_${new Date().toISOString().slice(0, 10)}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      if (window.$toast) {
        window.$toast.success('Shift data exported successfully')
      }
    } catch (error) {
      console.error('Export failed:', error)
      if (window.$toast) {
        window.$toast.error('Failed to export shift data')
      }
    }
  }

  const printShiftSummary = () => {
    const printWindow = window.open('', '_blank')
    const printContent = generatePrintContent()

    printWindow.document.write(printContent)
    printWindow.document.close()
    printWindow.print()
  }

  const generatePrintContent = () => {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Shift Summary - ${props.shift.name}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { text-align: center; margin-bottom: 20px; }
          .summary { margin-bottom: 20px; }
          .transactions { margin-top: 20px; }
          table { width: 100%; border-collapse: collapse; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #f2f2f2; }
        </style>
      </head>
      <body>
        <div class="header">
          <h2>Shift Summary</h2>
          <p>Shift ID: ${props.shift.id}</p>
          <p>Date: ${formatDateTime12h(props.shift.period_start_date)}</p>
        </div>

        <div class="summary">
          <h3>Summary</h3>
          <p><strong>Cashier:</strong> ${props.shift.user}</p>
          <p><strong>Duration:</strong> ${formatDuration(props.shift)}</p>
          <p><strong>Opening Balance:</strong> ${formatPrice(props.shift.openingBalance || 0)}</p>
          <p><strong>Total Sales:</strong> ${formatPrice(props.shift.totalSales || 0)}</p>
          <p><strong>Total Transactions:</strong> ${props.shift.transactions.length || 0}</p>

        </div>

        <div class="transactions">
          <h3>Recent Transactions</h3>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Amount</th>
                <th>Items</th>
                <th>Payment</th>
              </tr>
            </thead>
            <tbody>
              ${recentTransactions.value.slice(0, 10).map(t => `
                <tr>
                  <td>${t.posting_date}</td>
                  <td>${t.posting_time}</td>
                  <td>${formatPrice(t.grand_total)}</td>
                  <td>${t.total_qty || 0}</td>
                  <td>${t.paymentMethod || 'Cash'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </body>
      </html>
    `
  }

</script>

<style scoped>
/* Gradient backgrounds */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

.from-blue-50 {
  --tw-gradient-from: #eff6ff;
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(239, 246, 255, 0));
}

.to-indigo-50 {
  --tw-gradient-to: #eef2ff;
}

/* Status indicator colors */
.bg-green-500 { background-color: #10b981; }
.bg-red-500 { background-color: #ef4444; }
.text-green-600 { color: #059669; }
.text-red-600 { color: #dc2626; }

/* Background colors for summary cards */
.bg-blue-50 { background-color: #eff6ff; }
.bg-green-50 { background-color: #f0fdf4; }
.bg-yellow-50 { background-color: #fffbeb; }
.bg-purple-50 { background-color: #faf5ff; }

/* Text colors for summary cards */
.text-blue-900 { color: #1e3a8a; }
.text-green-900 { color: #14532d; }
.text-yellow-900 { color: #92400e; }
.text-purple-900 { color: #581c87; }

/* Responsive adjustments */
@media (max-width: 768px) {
  .max-w-2xl {
    max-width: calc(100vw - 2rem);
  }

  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }

  .grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* Scrollbar styling */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
</style>
