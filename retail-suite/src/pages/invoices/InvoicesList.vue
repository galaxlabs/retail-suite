
<template>

    <div class="w-full flex min-h-screen bg-gray-50">

      <!-- Main Content -->
      <main class="w-full sm:w-[75%] md:w-[80%] lg:w-[90%] flex flex-col min-h-screen">

        <header class="ml-6 mr-6 sticky top-0 z-10 bg-white rounded-xl shadow-sm border-b border-gray-200">
          <div class="px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
              <InvoiceLogo class="w-8 h-8 text-cyan-600 mr-3" />
              <h1 class="text-lg font-bold text-gray-900">Customers Invoices</h1>
            </div>

            <div class="flex gap-3">
              <button
                @click="exportInvoices"
                class="inline-flex items-center gap-2 bg-gray-500 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors duration-200"
                :disabled="isLoading"
              >
                <ExportIcon class="w-4 h-4 mr-2" />
                Export
              </button>
              <button
                @click="refreshInvoices"
                class="inline-flex items-center gap-2 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors duration-200"
                :disabled="isLoading"
              >
                <RefreshIcon class="w-4 h-4 mr-2" />
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
                  title="Total Invoices"
                  :value="invoicesStore.invoicesCount"
                  icon="InvoiceLogo"
                  color="blue"
                />
                <StatsCard
                  title="Today's Invoices"
                  :value="invoicesStore.todaysInvoices.length"
                  icon="InvoiceLogo"
                  color="green"
                />
                <StatsCard
                  title="Total Sales"
                  :value="formatPrice(invoicesStore.totalSales)"
                  icon="DollarIcon"
                  color="purple"
                />
                <StatsCard
                  title="Today's Sales"
                  :value="formatPrice(invoicesStore.todaysSales)"
                  icon="TrendingUpIcon"
                  color="orange"
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
                <label class="block text-sm font-medium text-gray-700 mb-2">Search Invoices</label>
                <div class="relative">
                  <SearchIcon class="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <input
                    v-model="searchQuery"
                    type="text"
                    class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                    placeholder="Search by receipt no, cashier, or items..."
                  />
                </div>
              </div>

              <!-- Date Range -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">From Date</label>
                <input
                  v-model="filters.startDate"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">To Date</label>
                <input
                  v-model="filters.endDate"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <!-- Status Filter -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  v-model="filters.status"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                >
                  <option value="">All Status</option>
                  <option value="Paid">Paid</option>
                  <option  value="Draft">Draft</option>
                  <option  value="Return">Return</option>
                  <option  value="Partly Paid">Partly Paid</option>
                  <option  value="Unpaid">Unpaid</option>
                  <option value="Cancelled">Cancelled</option>
                  <option value="Overdue">Overdue</option>
                  <option value="Credit Note Issued">Credit Note Issued</option>
                </select>
              </div>

              <!-- Cashier Filter -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Cashier</label>
                <select
                  v-model="filters.cashier"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                >
                  <option value="">All Cashiers</option>
                  <option v-for="cashier in uniqueCashiers" :key="cashier" :value="cashier">
                    {{ cashier }}
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
                  <InvoiceLogo class="w-6 h-6 text-gray-700" />
                  Invoices ({{ filteredInvoices.length }})
                  <span v-if="isLoading" class="text-sm text-gray-500 ml-2">Loading...</span>
                  </h3>
                  <div class="search-box">
                    <i class="icon-search"></i>
                    <input
                    type="text"
                    v-model="searchQuery"
                    @input="searchInvoices"
                    placeholder="Search by number or name..."
                    />
                  </div>
                </div>
              </div>


              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Invoice
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date & Time
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Cashier
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
                    <tr v-for="invoice in paginatedInvoices" :key="invoice.name" class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                          <div class="flex-shrink-0">
                            <div class="w-10 h-10 bg-cyan-100 rounded-lg flex items-center justify-center">
                              <ReceiptIcon class="w-5 h-5 text-cyan-600" />
                            </div>
                          </div>
                          <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">{{ invoice.name }}</div>
                            <div class="text-sm text-gray-500">{{ invoice.name.slice(-8) }}</div>
                          </div>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">{{ formatDate(invoice.posting_date,{ locale: 'en-SA'}) }}</div>
                        <div class="text-sm text-gray-500">{{ formatTime(invoice.posting_date) }}</div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                          <UserIcon />
                          <span class="text-sm text-gray-900">{{ invoice.owner }}</span>
                        </div>
                        <div v-if="invoice.shiftId" class="text-xs text-gray-500">
                          Shift:  {{ invoice.shiftId.slice(0,9) }} </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">{{ invoice.items_count || 0 }} items</div>
                        <div class="text-sm text-gray-500">
                          {{ invoice.total_qty }} qty
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-semibold text-gray-900">
                          {{ formatPrice(invoice.grand_total || 0) }}
                        </div>
                        <div class="text-xs text-gray-500">
                          {{ invoice.paymentMethod || 'cash' }}
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full" :class="getStatusClass(invoice.status)">
                          {{ invoice.status || 'completed' }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div class="flex space-x-2">
                          <button
                            @click="viewInvoice(invoice)"
                            class="text-cyan-600 hover:text-cyan-900 transition-colors duration-200"
                            title="View Details"
                          >
                            <EyeIcon class="w-4 h-4"  />
                          </button>
                          <button
                            @click="printInvoice(invoice)"
                            class="text-green-600 hover:text-green-900 transition-colors duration-200"
                            title="Print"
                          >
                            <PrintIcon class="w-4 h-4" />
                          </button>
                          <button
                            v-if="invoice.status !== 'deleted'"
                            @click="deleteInvoice(invoice)"
                            class="text-red-600 hover:text-red-900 transition-colors duration-200"
                            title="Delete"
                          >
                            <DeleteIcon class="w-4 h-4" />
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
                <svg class="w-10 h-10 animate-spin text-cyan-500 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <h2 class="text-lg font-medium text-gray-600">Invoices Is Loading...</h2>
              </div>
              <!-- Empty State -->
              <div v-if="paginatedInvoices.length === 0 && !isLoading"
                class="flex flex-col items-center justify-center py-16 text-center text-gray-500">
                <div class="w-16 h-16 bg-gray-100 flex items-center justify-center rounded-full mb-4">
                  <svg
                    class="w-8 h-8 text-gray-400"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V7a2 2 0 00-2-2h-3.586a1 1 0 01-.707-.293l-1.414-1.414A2 2 0 0010.586 3H6a2 2 0 00-2 2v6m16 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2v-6m16 0H4" />
                  </svg>
                </div>
                  <h3 class="text-xl font-semibold text-gray-700">
                    {{ hasActiveFilters || searchQuery ? 'Invoices Not Found' : 'No Invoices Yet' }}
                  </h3>
                  <p
                  class="text-gray-500 mt-1">
                  {{
                    hasActiveFilters || searchQuery
                      ? 'Try adjusting your search criteria'
                      : 'You haven’t created any invoices yet'
                    }}
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
                        'bg-cyan-500 text-white border-cyan-500': currentPage === page,
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

          <!-- Invoice Detail Modal -->
          <InvoiceDetailModal
            v-if="showInvoiceDetail"
            :invoice="selectedInvoice"
            @close="closeInvoiceDetail"
            @print="printInvoice"
          />
        </section>

      </main>
    </div>

</template>
<script setup>

import { ref, defineComponent, computed, onMounted, watch } from 'vue'
import { useInvoicesStore } from '@/stores/invoices'
import { formatNumber,formatDate, formatPrice } from '../../utils/formatters';
import EyeIcon from '@/components/icons/EyeIcon.svg'
import UserIcon from '@/components/icons/UserIcon.svg'
import ReceiptIcon from '@/components/icons/ReceiptIcon.svg'
import ExportIcon from '@/components/icons/ExportIcon.svg'
import RefreshIcon from '@/components/icons/RefreshIcon.svg'
import SearchIcon from '@/components/icons/SearchIcon.svg'
import CloseIcon from '@/components/icons/CloseIcon.svg'
import TodayIcon from '@/components/icons/TodayIcon.svg'
import DollarIcon from '@/components/icons/DollarIcon.svg'
import TrendingUpIcon from '@/components/icons/TrendingUpIcon.svg'
import PrintIcon from '@/components/icons/PrintIcon.svg'
import DeleteIcon from '@/components/icons/DeleteIcon.svg'
import InvoiceLogo from '@/components/icons/InvoiceIcon.svg'
import InvoiceDetailModal from './InvoiceDetailModal.vue';
import StatsCard from '../../layout/StatsCard.vue'
import Sidebar from '../../layout/Sidebar.vue';
import { TrendingUp, Calendar, BarChart3, DollarSign } from 'lucide-vue-next'

    const invoicesStore = useInvoicesStore()

    // State
    const searchQuery = ref('')
    const isLoading = ref(false)
    const showInvoiceDetail = ref(false)
    const selectedInvoice = ref(null)
    const currentPage = ref(1)
    const itemsPerPage = ref(20)

    // Filters
    const filters = ref({
      startDate: '',
      endDate: '',
      status: '',
      cashier: ''
    })

    // Computed properties
    const uniqueCashiers = computed(() => {
        const cashiers = invoicesStore.cashiers
      return cashiers
    })

    const hasActiveFilters = computed(() => {
      return filters.value.startDate ||
             filters.value.endDate ||
             filters.value.status ||
             filters.value.cashier ||
             searchQuery.value
    })

    const filteredInvoices = computed(() => {
      let result = [...invoicesStore.invoices]

      // Search filter
      if (searchQuery.value) {
        result = invoicesStore.searchInvoices(searchQuery.value)
      }

      // Date range filter
      if (filters.value.startDate && filters.value.endDate) {
        result = result.filter(invoice => {
          const invoiceDate = new Date(invoice.posting_date)
          const startDate = new Date(filters.value.startDate)
          const endDate = new Date(filters.value.endDate)
          endDate.setHours(23, 59, 59, 999) // Include full end date

          return invoiceDate >= startDate && invoiceDate <= endDate
        })
      }

      // Status filter
      if (filters.value.status) {
        result = result.filter(invoice => invoice.status === filters.value.status)
      }

      // Cashier filter
      if (filters.value.cashier) {
        console.log('Cashier',filters.value.cashier)
        result = result.filter(invoice => invoice.owner === filters.value.cashier)
      }
      console.log('Result from Filters',result)
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

      // Show pages around current page
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

    // const getTotalQuantity = (items) => {
    //   return items?.reduce((total, item) => total + (item.qty || 0), 0) || 0
    // }

    const getStatusClass = (status) => {
      const classes = {
        completed: 'bg-green-100 text-green-800',
        deleted: 'bg-red-100 text-red-800',
        pending: 'bg-yellow-100 text-yellow-800'
      }
      return classes[status] || classes.completed
    }

    const viewInvoice = (invoice) => {
      selectedInvoice.value = {
        ...invoice,
        items: invoice.items || []
      }
      console.log('selectedInvoice',selectedInvoice.value)
      showInvoiceDetail.value = true
    }

    const closeInvoiceDetail = () => {
      showInvoiceDetail.value = false
      selectedInvoice.value = null
      console.log(showInvoiceDetail.value)
    }

    const printInvoice = (invoice) => {
      // Create a print window with the invoice data
      const printWindow = window.open('', '_blank')
      const printContent = generatePrintContent(invoice)

      printWindow.document.write(printContent)
      printWindow.document.close()
      printWindow.print()
      printWindow.close()
    }

    const generatePrintContent = (invoice) => {
      return `
        <!DOCTYPE html>
        <html>
        <head>
          <title>Invoice - ${invoice.name}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }
            .header { text-align: center; margin-bottom: 20px; }
            .invoice-info { margin-bottom: 15px; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 5px; text-align: left; }
            th { background-color: #f2f2f2; }
            .total-row { font-weight: bold; background-color: #f9f9f9; }
            .footer { margin-top: 20px; text-align: center; font-size: 10px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h2>TAILWIND POS</h2>
            <p>Invoice / Receipt</p>
          </div>

          <div class="invoice-info">
            <p><strong>Receipt No:</strong> ${invoice.name}</p>
            <p><strong>Date:</strong> ${formatDate(invoice.posting_date)} ${formatTime(invoice.posting_time)}</p>
            <p><strong>Cashier:</strong> ${invoice.owner}</p>
            <p><strong>Payment Method:</strong> ${invoice.paymentMethod || 'Cash'}</p>
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
              ${invoice.items?.map((item, index) => `
                <tr>
                  <td>${index + 1}</td>
                  <td>${item.item_name}</td>
                  <td>${item.qty}</td>
                  <td>${formatPrice(item.rate)}</td>
                  <td>${formatPrice(item.qty * item.rate)}</td>
                </tr>
              `).join('') || ''}
              <tr class="total-row">
                <td colspan="4">Total</td>
                <td>${formatPrice(invoice.grand_total || 0)}</td>
              </tr>
            </tbody>
          </table>

          <div class="footer">
            <p>Thank you for your business!</p>
            <p>Printed on ${new Date().toLocaleString('id-ID')}</p>
          </div>
        </body>
        </html>
      `
    }

    const deleteInvoice = async (invoice) => {
      if (confirm(`Are you sure you want to delete invoice ${invoice.name}?`)) {
        try {
          await invoicesStore.deleteInvoice(invoice.id)

          if (window.$toast) {
            window.$toast.success('Invoice deleted successfully')
          }
        } catch (error) {
          console.error('Failed to delete invoice:', error)
          if (window.$toast) {
            window.$toast.error('Failed to delete invoice')
          }
        }
      }
    }

    const exportInvoices = async () => {
      try {
        const exportData = await invoicesStore.exportInvoices({
          startDate: filters.value.startDate,
          endDate: filters.value.endDate,
          status: filters.value.status,
          cashier: filters.value.cashier
        })

        // Create and download file
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
          type: 'application/json'
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `invoices_export_${new Date().toISOString().slice(0, 10)}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

        if (window.$toast) {
          window.$toast.success('Invoices exported successfully')
        }
      } catch (error) {
        console.error('Export failed:', error)
        if (window.$toast) {
          window.$toast.error('Failed to export invoices')
        }
      }
    }

    const refreshInvoices = async () => {
      isLoading.value = true
      try {
        await invoicesStore.loadInvoices()
        if (window.$toast) {
          window.$toast.success('Invoices refreshed')
        }
      } catch (error) {
        console.error('Refresh failed:', error)
        if (window.$toast) {
          window.$toast.error('Failed to refresh invoices')
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
        cashier: ''
      }
      currentPage.value = 1
    }

    // Initialize
    onMounted(async () => {
      isLoading.value = true
      try {
        await invoicesStore.loadInvoices()
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

/* Stats card colors */
.bg-blue-100 { background-color: #dbeafe; }
.text-blue-600 { color: #2563eb; }
.bg-green-100 { background-color: #dcfce7; }
.text-green-600 { color: #16a34a; }
.bg-purple-100 { background-color: #f3e8ff; }
.text-purple-600 { color: #9333ea; }
.bg-orange-100 { background-color: #fed7aa; }
.text-orange-600 { color: #ea580c; }

/* Hover effects */
.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}

.hover\:bg-gray-600:hover {
  background-color: #4b5563;
}

.hover\:bg-cyan-600:hover {
  background-color: #0891b2;
}

.hover\:bg-cyan-700:hover {
  background-color: #0e7490;
}

/* Action button colors */
.text-cyan-600 { color: #0891b2; }
.hover\:text-cyan-900:hover { color: #164e63; }
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
.bg-cyan-500 { background-color: #06b6d4; }
.border-cyan-500 { border-color: #06b6d4; }

/* Responsive adjustments */
@media (max-width: 768px) {
  .grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .md\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }

  .md\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .overflow-x-auto {
    overflow-x: auto;
  }

  table {
    min-width: 800px;
  }
}

/* Loading state */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-box i {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-box input {
  width: 100%;
  padding: 0.625rem 1rem 0.625rem 2.5rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

</style>
