<template>

    <div class="w-full flex min-h-screen bg-gray-50">

      <!-- Main Content -->
      <main class="w-full sm:w-[75%] md:w-[80%] lg:w-[90%] flex flex-col min-h-screen">

        <header class="ml-6 mr-6 sticky top-0 z-10 bg-white rounded-xl shadow-sm border-b border-gray-200">
          <div class="px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
              <ShoppingCart class="w-8 h-8 text-orange-600 mr-3" />
              <h1 class="text-lg font-bold text-gray-900">Suppliers Invoices</h1>
            </div>

            <div class="flex gap-3">
              <button
                @click="exportInvoices"
                class="inline-flex items-center gap-2 bg-gray-500 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors duration-200"
                :disabled="isLoading"
              >
                <Download class="w-4 h-4 mr-2" />
                Export
              </button>
              <button
                @click="refreshInvoices"
                class="inline-flex items-center gap-2 bg-orange-500 hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors duration-200"
                :disabled="isLoading"
              >
                <RotateCw class="w-4 h-4 mr-2" />
                Refresh
              </button>
            </div>
          </div>
        </header>

        <!-- Statistics Section -->
        <section class="flex-shrink-0 px-6 py-8">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-6">Statistics</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatsCard
                  title="Total Bills"
                  :value="billsStore.billsCount"
                  icon="Receipt"
                  color="blue"
                />
                <StatsCard
                  title="Pending Bills"
                  :value="billsStore.pendingBills"
                  icon="AlertCircle"
                  color="orange"
                />
                <StatsCard
                  title="Total Purchase"
                  :value="formatPrice(billsStore.totalPurchase)"
                  icon="DollarSign"
                  color="green"
                />
                <StatsCard
                  title="Amount Due"
                  :value="formatPrice(billsStore.amountDue)"
                  icon="TrendingDown"
                  color="red"
                />
            </div>
          </div>
        </section>


        <!-- Filters Section -->
        <section class="flex-1 px-6 pb-6">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <!-- Search -->
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">Search Bills</label>
                <div class="relative">
                  <Search class="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <input
                    v-model="searchQuery"
                    type="text"
                    class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="Search by bill no, supplier, or items..."
                  />
                </div>
              </div>

              <!-- Date Range -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">From Date</label>
                <input
                  v-model="filters.startDate"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">To Date</label>
                <input
                  v-model="filters.endDate"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <!-- Status Filter -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  v-model="filters.status"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">All Status</option>
                  <option value="Paid">Paid</option>
                  <option value="Draft">Draft</option>
                  <option value="Unpaid">Unpaid</option>
                  <option value="Partly Paid">Partly Paid</option>
                  <option value="Cancelled">Cancelled</option>
                  <option value="Overdue">Overdue</option>
                </select>
              </div>

              <!-- Supplier Filter -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Supplier</label>
                <select
                  v-model="filters.supplier"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">All Suppliers</option>
                  <option v-for="supplier in uniqueSuppliers" :key="supplier.name" :value="supplier.name">
                    {{ supplier.name }}
                  </option>
                </select>
              </div>

              <!-- Clear Filters -->
              <div class="flex items-end">
                <button
                  @click="clearFilters"
                  class="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors duration-200"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Table Section-->
        <section class="ml-2 flex-1 px-4 sm:px-6 pb-4 sm:pb-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden">
              <div class="px-4 sm:px-6 py-4 border-b border-gray-200 flex-shrink-0">
                <div class="flex items-center justify-between">
                  <h3 class="text-lg font-medium text-gray-900 flex items-center gap-2">
                  <ShoppingCart class="w-6 h-6 text-gray-700" />
                  Supplier Bills ({{ filteredInvoices.length }})
                  <span v-if="isLoading" class="text-sm text-gray-500 ml-2">Loading...</span>
                  </h3>
                </div>
              </div>


              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Bill
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Supplier
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date & Time
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Items
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="bill in paginatedInvoices" :key="bill.name" class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                          <div class="flex-shrink-0">
                            <div class="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                              <Receipt class="w-5 h-5 text-orange-600" />
                            </div>
                          </div>
                          <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">{{ bill.name }}</div>
                            <div class="text-sm text-gray-500">{{ bill.name.slice(-8) }}</div>
                          </div>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                          <Building2 class="w-4 h-4 text-gray-400 mr-2" />
                          <span class="text-sm text-gray-900">{{ bill.supplier }}</span>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">{{ formatDate(bill.posting_date) }}</div>
                        <div class="text-sm text-gray-500">{{ formatTime(bill.posting_date) }}</div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">{{ bill.items_count || 0 }} items</div>
                        <div class="text-sm text-gray-500">
                          {{ bill.total_qty }} qty
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-semibold text-gray-900">
                          {{ formatPrice(bill.grand_total || 0) }}
                        </div>
                        <div class="text-xs text-gray-500">
                          Due: {{ formatPrice(bill.outstanding_amount || 0) }}
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full" :class="getStatusClass(bill.status)">
                          {{ bill.status || 'pending' }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div class="flex space-x-2">
                          <button
                            @click="viewBill(bill)"
                            class="text-orange-600 hover:text-orange-900 transition-colors duration-200"
                            title="View Details"
                          >
                            <Eye class="w-4 h-4"  />
                          </button>
                          <button
                            @click="printBill(bill)"
                            class="text-green-600 hover:text-green-900 transition-colors duration-200"
                            title="Print"
                          >
                            <Printer class="w-4 h-4" />
                          </button>
                          <button
                            v-if="bill.status !== 'cancelled'"
                            @click="deleteBill(bill)"
                            class="text-red-600 hover:text-red-900 transition-colors duration-200"
                            title="Delete"
                          >
                            <Trash2 class="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>


                  </tbody>
                </table>
              </div>
              <!-- Loading State -->
              <div v-if="isLoading === true"
                  class="flex flex-col items-center justify-center py-10 text-gray-500">
                <svg class="w-10 h-10 animate-spin text-orange-500 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <h2 class="text-lg font-medium text-gray-600">Bills Is Loading...</h2>
              </div>
              <!-- Empty State -->
              <div v-if="paginatedInvoices.length === 0 && !isLoading"
                class="flex flex-col items-center justify-center py-16 text-center text-gray-500">
                <div class="w-16 h-16 bg-gray-100 flex items-center justify-center rounded-full mb-4">
                  <ShoppingCart class="w-8 h-8 text-gray-400" />
                </div>
                  <h3 class="text-xl font-semibold text-gray-700">
                    {{ hasActiveFilters || searchQuery ? 'Bills Not Found' : 'No Bills Yet' }}
                  </h3>
                  <p class="text-gray-500 mt-1">
                    {{ emptyStateMessage }}
                  </p>
              </div>

              <!-- Pagination -->
              <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-200">
                <div class="flex items-center justify-between">
                  <div class="text-sm text-gray-700">
                    Showing {{ ((currentPage - 1) * itemsPerPage) + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredInvoices.length) }} of {{ filteredInvoices.length }} results
                  </div>
                  <div class="flex space-x-2">
                    <button
                      @click="currentPage = Math.max(1, currentPage - 1)"
                      :disabled="currentPage === 1"
                      class="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                    >
                      Previous
                    </button>

                    <button
                      v-for="page in visiblePages"
                      :key="page"
                      @click="currentPage = page"
                      class="px-3 py-1 border rounded text-sm transition-colors duration-200"
                      :class="{
                        'bg-orange-500 text-white border-orange-500': currentPage === page,
                        'border-gray-300 hover:bg-gray-50': currentPage !== page
                      }"
                    >
                      {{ page }}
                    </button>

                    <button
                      @click="currentPage = Math.min(totalPages, currentPage + 1)"
                      :disabled="currentPage === totalPages"
                      class="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                    >
                      Next
                    </button>
                  </div>
                </div>
              </div>

          </div>
        </section>

      </main>
    </div>

</template>
<script setup>

import { ref, toRaw, computed, onMounted, watch } from 'vue'
import { useShiftStore } from '@/stores/shift.js'
import { useSuppliersStore } from '@/stores/suppliers.js'
import { useBillsStore } from '@/stores/bills'
import { formatDate, formatPrice } from '../../utils/formatters'
import StatsCard from '../../layout/StatsCard.vue'
import Sidebar from '../../layout/Sidebar.vue'
import {
  Download,
  RotateCw,
  Search,
  ShoppingCart,
  Receipt,
  AlertCircle,
  DollarSign,
  TrendingDown,
  Eye,
  Printer,
  Trash2,
  Building2
} from 'lucide-vue-next'


    // Stores
    const shiftStore = useShiftStore()
    const pos_profile = computed(() => shiftStore.pos_profile || {})

    const SuppliersStore = useSuppliersStore()

    const billsStore = useBillsStore()
    const billStore = ref(null)

    // State
    const searchQuery = ref('')
    const isLoading = ref(false)
    const currentPage = ref(1)
    const itemsPerPage = ref(20)

    // Filters
    const filters = ref({
      startDate: '',
      endDate: '',
      status: '',
      supplier: ''
    })

    // Computed properties
    const uniqueSuppliers = computed(() => {
      return SuppliersStore.suppliers || []
    })
    console.log("uniqueSuppliers",uniqueSuppliers)
    const hasActiveFilters = computed(() => {
      return filters.value.startDate ||
             filters.value.endDate ||
             filters.value.status ||
             filters.value.supplier ||
             searchQuery.value
    })

    const filteredInvoices = computed(() => {
      let result = [...billsStore.bills]
      // Search filter
        if (searchQuery.value) {
          const q = searchQuery.value.toLowerCase()

          result = result.filter(bill => {
            const matchMain =
              bill.name?.toLowerCase().includes(q) ||
              bill.supplier?.toLowerCase().includes(q) ||
              bill.supplier_name?.toLowerCase().includes(q) ||
              bill.tax_id?.toLowerCase().includes(q)

            const matchItems = bill.items?.some(item =>
              item.item_code?.toLowerCase().includes(q) ||
              item.item_name?.toLowerCase().includes(q)
            )

            return matchMain || matchItems
          })
        }

      // Date range filter
      if (filters.value.startDate && filters.value.endDate) {
        result = result.filter(bill => {
          const billDate = new Date(bill.posting_date)
          const startDate = new Date(filters.value.startDate)
          const endDate = new Date(filters.value.endDate)
          endDate.setHours(23, 59, 59, 999)

          return billDate >= startDate && billDate <= endDate
        })
      }

      // Status filter
      if (filters.value.status) {
        result = result.filter(bill => bill.status === filters.value.status)
      }

      // Supplier filter
      if (filters.value.supplier) {
        result = result.filter(bill => bill.supplier === filters.value.supplier)
      }

      return result
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredInvoices.value.length / itemsPerPage.value)
    })

    const paginatedInvoices = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredInvoices.value.slice(start, end)
    })

    const visiblePages = computed(() => {
      const pages = []
      const totalPagesValue = totalPages.value
      const current = currentPage.value

      const start = Math.max(1, current - 2)
      const end = Math.min(totalPagesValue, current + 2)

      for (let i = start; i <= end; i++) {
        pages.push(i)
      }

      return pages
    })

    // Watch for filter changes and reset pagination
    watch([searchQuery, filters], () => {
      currentPage.value = 1
    }, { deep: true })

    const formatTime = (date) => {
      return new Date(date).toLocaleTimeString('id-ID', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getStatusClass = (status) => {
      const classes = {
        'Paid': 'bg-green-100 text-green-800',
        'Unpaid': 'bg-red-100 text-red-800',
        'Partly Paid': 'bg-yellow-100 text-yellow-800',
        'Overdue': 'bg-purple-100 text-purple-800',
        'Draft': 'bg-gray-100 text-gray-800',
        'Cancelled': 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }

    const viewBill = (bill) => {
      console.log('View bill:', bill)
      // Open bill detail modal or navigate to detail page
    }

    const printBill = (bill) => {
      const printWindow = window.open('', '_blank')
      const printContent = generatePrintContent(bill)

      printWindow.document.write(printContent)
      printWindow.document.close()
      printWindow.print()
      printWindow.close()
    }

    const generatePrintContent = (bill) => {
      return `
        <!DOCTYPE html>
        <html>
        <head>
          <title>Bill - ${bill.name}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }
            .header { text-align: center; margin-bottom: 20px; }
            .bill-info { margin-bottom: 15px; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 5px; text-align: left; }
            th { background-color: #f2f2f2; }
            .total-row { font-weight: bold; background-color: #f9f9f9; }
            .footer { margin-top: 20px; text-align: center; font-size: 10px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h2>{{ storeName || 'Retail Suite' }} - Supplier Bill</h2>
          </div>

          <div class="bill-info">
            <p><strong>Bill No:</strong> ${bill.name}</p>
            <p><strong>Supplier:</strong> ${bill.supplier_name}</p>
            <p><strong>Date:</strong> ${formatDate(bill.posting_date)} ${formatTime(bill.posting_date)}</p>
            <p><strong>Status:</strong> ${bill.status}</p>
          </div>

          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Item</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              ${bill.items?.map((item, index) => `
                <tr>
                  <td>${index + 1}</td>
                  <td>${item.item_name}</td>
                  <td>${item.qty}</td>
                  <td>${formatPrice(item.rate)}</td>
                  <td>${formatPrice(item.qty * item.rate)}</td>
                </tr>
              `).join('') || ''}
              <tr class="total-row">
                <td colspan="4">Total Amount</td>
                <td>${formatPrice(bill.total_amount || 0)}</td>
              </tr>
              <tr>
                <td colspan="4">Outstanding Amount</td>
                <td>${formatPrice(bill.outstanding_amount || 0)}</td>
              </tr>
            </tbody>
          </table>

          <div class="footer">
            <p>Thank you!</p>
            <p>Printed on ${new Date().toLocaleString('id-ID')}</p>
          </div>
        </body>
        </html>
      `
    }

    const deleteBill = async (bill) => {
      if (confirm(`Are you sure you want to delete bill ${bill.name}?`)) {
        try {
          await billsStore.deleteBill(bill.id)

          if (window.$toast) {
            window.$toast.success('Bill deleted successfully')
          }
        } catch (error) {
          console.error('Failed to delete bill:', error)
          if (window.$toast) {
            window.$toast.error('Failed to delete bill')
          }
        }
      }
    }

    const exportInvoices = async () => {
      try {
        const blob = new Blob([JSON.stringify(filteredInvoices.value, null, 2)], {
          type: 'application/json'
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `supplier_bills_${new Date().toISOString().slice(0, 10)}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

        if (window.$toast) {
          window.$toast.success('Bills exported successfully')
        }
      } catch (error) {
        console.error('Export failed:', error)
        if (window.$toast) {
          window.$toast.error('Failed to export bills')
        }
      }
    }

    const refreshInvoices = async () => {
      isLoading.value = true
      try {
        await billsStore.loadBills()
        if (window.$toast) {
          window.$toast.success('Bills refreshed')
        }
      } catch (error) {
        console.error('Refresh failed:', error)
        if (window.$toast) {
          window.$toast.error('Failed to refresh bills')
        }
      } finally {
        isLoading.value = false
      }
    }

    const clearFilters = () => {
      searchQuery.value = ''
      filters.value = {
        startDate: '',
        endDate: '',
        status: '',
        supplier: ''
      }
      currentPage.value = 1
    }
    const emptyStateMessage = computed(() => {
        return hasActiveFilters.value || searchQuery.value
            ? 'Try adjusting your search criteria'
            : "You haven't created any supplier bills yet"
        })


  const loadSuppliersFinancialData = async () => {
      try {
        console.log('toRaw(pos_profile.value) => ', toRaw(pos_profile.value))
        const response = await SuppliersStore.fetchSuppliersFinancialData(toRaw(pos_profile.value))
        console.log('response => ', response)
        // suppliers.value = response
      } catch (error) {
        console.error("Error loading suppliers financial data:", error)
      }
    }
    // Initialize
    onMounted(async () => {
      isLoading.value = true
      try {
        const isOpen = await shiftStore.checkActiveShift()
        console.log('isOpen => ', isOpen)
        await loadSuppliersFinancialData()
        await billsStore.loadBills({})
      } finally {
        isLoading.value = false
      }
    })

</script>

<style scoped>
.bg-gray-50 {
  background-color: #f8fafc;
}

/* Status badge colors */
.bg-green-100 { background-color: #dcfce7; }
.text-green-800 { color: #166534; }
.bg-red-100 { background-color: #fee2e2; }
.text-red-800 { color: #991b1b; }
.bg-yellow-100 { background-color: #fef3c7; }
.text-yellow-800 { color: #92400e; }
.bg-purple-100 { background-color: #f3e8ff; }
.text-purple-800 { color: #581c87; }

/* Hover effects */
.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}

.hover\:bg-gray-600:hover {
  background-color: #4b5563;
}

.hover\:bg-orange-600:hover {
  background-color: #ea580c;
}

/* Action button colors */
.text-orange-600 { color: #ea580c; }
.hover\:text-orange-900:hover { color: #7c2d12; }
.text-green-600 { color: #16a34a; }
.hover\:text-green-900:hover { color: #14532d; }
.text-red-600 { color: #dc2626; }
.hover\:text-red-900:hover { color: #7f1d1d; }

/* Focus states */
input:focus, select:focus {
  outline: none;
}

/* Disabled states */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Table hover */
tbody tr:hover {
  background-color: #f9fafb;
}

/* Pagination */
.bg-orange-500 { background-color: #f97316; }
.border-orange-500 { border-color: #f97316; }

</style>
