<!-- CustomerList.vue -->
<template>

    <div class="w-full flex min-h-screen bg-gray-50">
      <!-- Main Content -->
      <main class="flex flex-col flex-1">
        <!-- Header -->
        <header class="mx-3 mt-3 sticky top-0 z-10 bg-white rounded-xl shadow-sm border-b border-gray-200">
          <div class="px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
              <Users class="w-8 h-8 text-cyan-600" />
              <div>
               <h1 class="text-lg font-bold text-gray-900">Customer Management</h1>
               <p class="text-sm text-gray-600 mt-1">{{ customers.length }} registered customers</p>
              </div>
            </div>
            <button
              @click="openCreateModal"
              class="flex items-center gap-2 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition font-medium"
            >
              <Plus class="w-5 h-5" />
              New Customer
            </button>
          </div>
        </header>

        <!-- Filters and Search -->
        <section class="px-6 py-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <!-- Search -->
              <div>
                <label class="text-sm font-semibold text-gray-700 block mb-2">Search</label>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search by name or customer number..."
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                />
              </div>

              <!-- Status Filter -->
              <div>
                <label class="text-sm font-semibold text-gray-700 block mb-2">Status</label>
                <select
                  v-model="statusFilter"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent bg-white"
                >
                  <option disabled value="">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="blocked">Blocked</option>
                </select>
              </div>

              <!-- Sort -->
              <div>
                <label class="text-sm font-semibold text-gray-700 block mb-2">Sort By</label>
                <select
                  v-model="sortBy"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent bg-white"
                >
                  <option value="recent">Most Recent</option>
                  <option value="name">Name (A-Z)</option>
                  <option value="purchase">Highest Purchases</option>
                  <option value="debt">Highest Debt</option>
                </select>
              </div>

              <!-- Export -->
              <div class="flex items-end">
                <button
                  @click="exportCustomers"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium flex items-center justify-center gap-2"
                >
                  <Download class="w-4 h-4" />
                  Export
                </button>
              </div>

            </div>
          </div>
        </section>

        <!-- Customers Table -->
        <section class="px-6 pb-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <!-- Table Header with Count -->
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <p class="text-sm font-semibold text-gray-700">
                Showing {{ filteredCustomers.length }} of {{ customers.length }} customers
              </p>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-50 border-b border-gray-200">
                  <tr>
                      <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Customer Name</th>
                      <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Phone</th>
                      <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Email</th>
                      <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Debt</th>
                      <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Total Purchases</th>
                      <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                      <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="customer in filteredCustomers" :key="customer.name"   @click="goToCustomer(customer)" class="hover:bg-blue-50 transition">
                    <td class="px-6 py-4 text-sm font-semibold text-gray-900">{{ customer.name }}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">{{ customer.contacts.length > 0 ? customer.contacts[0].phone || customer.contacts[0].mobile_no : '-' }}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">{{customer.contacts.length > 0 ? customer.contacts[0].email_id : '-'}}</td>
                    <td class="px-6 py-4 text-sm font-semibold">
                      <span :class="customer.debt > 0 ? 'text-red-600' : 'text-green-600'">
                        {{ formatCurrency(customer.debt, currencyCode, locale) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm font-semibold text-gray-900">{{ formatCurrency(customer.totalPurchases, currencyCode, locale)}}</td>
                    <td class="px-6 py-4 text-sm">
                      <span :class="getStatusClass(customer.status)" class="px-3 py-1 rounded-full text-xs font-semibold">
                        {{ getStatusLabel(customer.disabled == 0 ? 'Active' : 'Inactive') }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm">
                      <div class="flex items-center gap-3">
                        <button
                          @click="viewCustomer(customer)"
                          class="text-cyan-600 hover:text-cyan-900 transition font-medium text-sm"
                          title="View Profile"
                        >
                          <Eye class="w-4 h-4" />
                        </button>
                        <button
                          @click="editCustomer(customer)"
                          class="text-orange-600 hover:text-orange-900 transition font-medium text-sm"
                          title="Edit"
                        >
                          <Edit2 class="w-4 h-4" />
                        </button>
                        <button
                          @click="deleteCustomer(customer.name)"
                          class="text-red-600 hover:text-red-900 transition font-medium text-sm"
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

            <!-- Empty State -->
            <div v-if="filteredCustomers.length === 0" class="text-center py-12">
              <p class="text-gray-500">No customers match the search</p>
            </div>
          </div>
        </section>

        <!-- Pagination -->
        <section class="flex-shrink-0 px-6 pb-6">
        <div class="flex items-center justify-between">
          <p class="text-sm text-gray-600 font-medium">
            Total: <span class="font-semibold">{{ customers.length }}</span> customers
          </p>
          <div class="flex items-center gap-2">
            <button class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium text-sm disabled:opacity-50">
              ← Previous
            </button>
            <div class="flex items-center gap-1">
              <button class="px-3 py-2 bg-cyan-600 text-white rounded-lg font-medium text-sm">1</button>
            </div>
            <button class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium text-sm disabled:opacity-50">
              Next →
            </button>
          </div>
        </div>
        </section>
      </main>
    </div>

    <!-- Create/Edit Modal -->
    <CustomerModal
      v-if="showModal"
      :customer="editingCustomer"
      @save="saveCustomer"
      @close="showModal = false"
    />

    <!-- View Profile Modal -->
    <CustomerProfileModal
      v-if="showProfileModal"
      :customer="selectedCustomer"
      @close="showProfileModal = false"
    />

</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted, watch, toRaw } from 'vue'

import CustomerModal from '@/components/modals/CustomerModal.vue'
import CustomerProfileModal from '@/components/modals/CustomerProfileModal.vue'
import { Users, Plus, Download, Edit2, Eye, Trash2 } from 'lucide-vue-next'
import {formatCurrency} from '@/utils/formatters.js'
import { useSettingsStore } from "@/stores/settings";
import { useShiftStore } from '@/stores/shift.js'
import { useCustomersStore } from '@/stores/customers.js'
import CustomerProfile from './CustomerProfile.vue'


    //  Router
    const router = useRouter()
    // store
    const settingsStore = useSettingsStore();
    const currencyCode = settingsStore?.settings?.store?.currencyCode || "USD";
    const locale = settingsStore?.settings?.store?.local || "en-US";

    const shiftStore = useShiftStore()
    const pos_profile = computed(() => shiftStore.pos_profile || {})

    const CustomersStore =useCustomersStore()
    const customers = ref([])
    const searchQuery = ref('')
    const statusFilter = ref('')
    const sortBy = ref('recent')
    const showModal = ref(false)
    const showProfileModal = ref(false)
    const editingCustomer = ref(null)
    const selectedCustomer = ref(null)

    const goToCustomer = (customer) => {
      router.push({
        name: 'CustomerProfile',
        params: { customer_name: customer.name }
      })
    }

const filteredCustomers = computed(() => {
  let filtered = customers.value.filter(c => {
    const contactPhones = c.contacts.map(ct => ct.phone || ct.mobile_no || '').join(' ')
    const contactEmails = c.contacts.map(ct => ct.email_id || '').join(' ')
    const matchSearch = !searchQuery.value ||
      c.customer_name.includes(searchQuery.value) ||
      contactPhones.includes(searchQuery.value) ||
      contactEmails.includes(searchQuery.value)

    const matchStatus = !statusFilter.value || c.status === statusFilter.value

    return matchSearch && matchStatus
  })

  // Sort logic stays the same
  if (sortBy.value === 'name') {
    filtered.sort((a, b) => a.customer_name.localeCompare(b.customer_name, 'ar'))
  } else if (sortBy.value === 'purchase') {
    filtered.sort((a, b) => b.total_purchases - a.total_purchases)
  } else if (sortBy.value === 'debt') {
    filtered.sort((a, b) => b.debt - a.debt)
  } else {
    filtered.sort((a, b) => new Date(b.creation) - new Date(a.creation))
  }

  return filtered
})


    const getStatusClass = (status) => {
      const classes = {
        active: 'bg-green-100 text-green-800',
        inactive: 'bg-gray-100 text-gray-800',
        blocked: 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }

    const getStatusLabel = (status) => {
      const labels = {
          active: 'Active',
          inactive: 'Inactive',
          blocked: 'Blocked'
        }
      return labels[status] || status
    }

    const openCreateModal = () => {
      editingCustomer.value = null
      showModal.value = true
    }

    const editCustomer = (customer) => {
      editingCustomer.value = { ...customer }
      showModal.value = true
    }

    const viewCustomer = (customer) => {
      selectedCustomer.value = customer
      showProfileModal.value = true
    }

    const deleteCustomer = async (id) => {
      if (confirm('Delete this customer?')) {
        customers.value = customers.value.filter(c => c.id !== id)
      }
    }

    const saveCustomer = (customer) => {
      if (customer.name) {
        // Update existing
        const index = customers.value.findIndex(c => c.name === customer.name)
        if (index >= 0) {
          customers.value[index] = customer
        }
      } else {
        // Create new
        customer.name = Math.max(...customers.value.map(c => c.id), 0) + 1
        customer.createdAt = new Date().toISOString().split('T')[0]
        customers.value.push(customer)
      }
      showModal.value = false
    }
const exportCustomers = () => {
  const csv = [
    ['Customer Name', 'Phone', 'Email', 'Address', 'Debt', 'Total Purchases', 'Status'],
    ...filteredCustomers.value.map(c => [
      c.customer_name,
      c.contacts.length > 0 ? c.contacts[0].phone || c.contacts[0].mobile : '-',
      c.contacts.length > 0 ? c.contacts[0].email : '-',
      c.addresses.length > 0 ? c.addresses[0].address_line1 + ', ' + c.addresses[0].city : '-',
      c.debt,
      c.total_purchases,
      getStatusLabel(c.status)
    ])
  ]
  const csvContent = csv.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `customers-${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// const exportCustomers = () => {
//   const csv = [
//     ['Customer Name', 'Phone', 'Email', 'Address', 'Debt', 'Total Purchases', 'Status'],
//     ...filteredCustomers.value.map(c => [
//       c.name,
//       c.phone,
//       c.email,
//       c.address,
//       c.debt,
//       c.totalPurchases,
//       getStatusLabel(c.status)
//     ])
//   ]
//   const csvContent = csv.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')
//   const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
//   const link = document.createElement('a')
//   const url = URL.createObjectURL(blob)
//   link.setAttribute('href', url)
//   link.setAttribute('download', `customers-${new Date().toISOString().split('T')[0]}.csv`)
//   link.style.visibility = 'hidden'
//   document.body.appendChild(link)
//   link.click()
//   document.body.removeChild(link)
// }

const loadCustomersFinancialData = async ()=>{
    try{
        console.log('pos_profile.value',toRaw(pos_profile.value))
        const response = await CustomersStore.fetchCustomersFinancialData(toRaw(pos_profile.value))
        console.log('response => ',response)
        customers.value = response

    }catch(error){
      console.error("Error In load Customers Financial Data")
    }
}
onMounted(async ()=>{
  await shiftStore.checkActiveShift()
  await loadCustomersFinancialData()
})

</script>

<style scoped>
table {
border-collapse: collapse;
}
</style>
