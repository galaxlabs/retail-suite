<!-- SuppliersList.vue -->
<template>

    <div class="w-full flex min-h-screen bg-gray-50">
      <!-- Main Content -->
      <main class="flex flex-col flex-1 min-h-screen">
        <!-- Header -->
        <header class="mx-3 mt-3 sticky top-0 z-10 bg-white rounded-xl shadow-sm border-b border-gray-200">
          <div class="px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
              <Truck class="w-8 h-8 text-blue-600" />
              <div>
                <h1 class="text-lg font-bold text-gray-900">Supplier Management</h1>
                <p class="text-sm text-gray-600 mt-1">{{ suppliers.length }} registered suppliers</p>
              </div>
            </div>
            <button
              @click="openCreateModal"
              class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
            >
              <Plus class="w-5 h-5" />
              New Supplier
            </button>
          </div>
        </header>

        <!-- Filters and Search -->
        <section class="flex-shrink-0 px-6 py-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

              <!-- Search -->
              <div>
                <label class="text-sm font-semibold text-gray-700 block mb-2">Search</label>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search by name or supplier number..."
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <!-- Status Filter -->
              <div>
                <label class="text-sm font-semibold text-gray-700 block mb-2">Status</label>
                <select
                  v-model="statusFilter"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
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
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                >
                  <option value="recent">Most Recent</option>
                  <option value="name">Name (A-Z)</option>
                  <option value="supply">Highest Supplies</option>
                  <option value="debt">Highest Debt</option>
                </select>
              </div>

              <!-- Export -->
              <div class="flex items-end">
                <button
                  @click="exportSuppliers"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium flex items-center justify-center gap-2"
                >
                  <Download class="w-4 h-4" />
                  Export
                </button>
              </div>

            </div>
          </div>
        </section>

        <!-- Suppliers Table -->
        <section class="flex-1 px-6 pb-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <!-- Table Header with Count -->
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <p class="text-sm font-semibold text-gray-700">
                Showing {{ filteredSuppliers.length }} of {{ suppliers.length }} suppliers
              </p>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Supplier Name</th>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Phone</th>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Email</th>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Due Amount</th>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Total Supplies</th>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">

                  <tr v-for="supplier in filteredSuppliers" :key="supplier.id" @click="goToSupplier(supplier)" class="hover:bg-blue-50 transition">
                    <td class="px-6 py-4 text-sm font-semibold text-gray-900">{{ supplier.name }}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">{{ supplier.contact_details[0]?.phone || 'no phone' }}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">{{ supplier.contact_details[0]?.email_id || 'no email' }}</td>
                    <td class="px-6 py-4 text-sm font-semibold">
                      <span :class="supplier.due_amount > 0 ? 'text-red-600' : 'text-green-600'">
                        {{ formatCurrency(supplier.due_amount, currencyCode, locale) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm font-semibold text-gray-900">{{ formatCurrency(supplier.totalSupplies, currencyCode, locale) }}</td>
                    <td class="px-6 py-4 text-sm">
                      <span :class="getStatusClass(supplier.status)" class="px-3 py-1 rounded-full text-xs font-semibold">
                        {{ getStatusLabel(supplier.status) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm">
                      <div class="flex items-center gap-3">
                        <button
                          @click="viewSupplier(supplier)"
                          class="text-blue-600 hover:text-blue-900 transition font-medium text-sm"
                          title="View Profile"
                        >
                          <Eye class="w-4 h-4" />
                        </button>
                        <button
                          @click="editSupplier(supplier)"
                          class="text-orange-600 hover:text-orange-900 transition font-medium text-sm"
                          title="Edit"
                        >
                          <Edit2 class="w-4 h-4" />
                        </button>
                        <button
                          @click="deleteSupplier(supplier.id)"
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
            <div v-if="filteredSuppliers.length === 0" class="text-center py-12">
              <p class="text-gray-500">No suppliers match the search</p>
            </div>
          </div>
        </section>

        <!-- Pagination -->
        <section class="flex-shrink-0 px-6 pb-6">
          <div class="flex items-center justify-between">
            <p class="text-sm text-gray-600 font-medium">
              Total: <span class="font-semibold">{{ suppliers.length }}</span> suppliers
            </p>
            <div class="flex items-center gap-2">
              <button class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium text-sm disabled:opacity-50">
                ← Previous
              </button>
              <div class="flex items-center gap-1">
                <button class="px-3 py-2 bg-blue-600 text-white rounded-lg font-medium text-sm">1</button>
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
    <SupplierModal
      v-if="showModal"
      :supplierGroups="supplierGroups"
      :supplier="editingSupplier"
      @save="saveSupplier"
      @close="showModal = false"
    />

    <!-- View Profile Modal -->
    <SupplierProfileModal
      v-if="showProfileModal"
      :supplier="selectedSupplier"
      @close="showProfileModal = false"
    />

</template>
<script setup>
import { ref, computed, onMounted, toRaw } from 'vue'
import { useRouter } from 'vue-router'


import SupplierModal from '@/components/modals/SupplierModal.vue'
import SupplierProfileModal from '@/components/modals/SupplierProfileModal.vue'

import { Truck, Plus, Download, Edit2, Eye, Trash2 } from 'lucide-vue-next'
import { formatCurrency } from '@/utils/formatters.js'

import { useSettingsStore } from '@/stores/settings'
import { useShiftStore } from '@/stores/shift.js'
import { useSuppliersStore } from '@/stores/suppliers.js'

/* =========================
   Router
========================= */
const router = useRouter()

/* =========================
   Stores
========================= */
const settingsStore = useSettingsStore()
const suppliersStore = useSuppliersStore()
const SuppliersStore = useSuppliersStore()
const shiftStore = useShiftStore()

const currencyCode =
  settingsStore?.settings?.store?.currencyCode || 'USD'
const locale =
  settingsStore?.settings?.store?.local || 'en-US'

const pos_profile = computed(() => shiftStore.pos_profile || {})

/* =========================
   State
========================= */
const suppliers = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const sortBy = ref('recent')

const showModal = ref(false)
const showProfileModal = ref(false)

const editingSupplier = ref(null)
const selectedSupplier = ref(null)

/* =========================
   Navigation
========================= */
const goToSupplier = (supplier) => {
  router.push({
    name: 'SupplierProfile',
    params: { supplier_name: supplier.name }
  })
}

/* =========================
   Computed
========================= */
const supplierGroups = computed(() => suppliersStore.supplierGroups)
console.log("supplierGroups in computed =>", supplierGroups)

const filteredSuppliers = computed(() => {
  let filtered = suppliers.value.filter(s => {
    const matchSearch =
      !searchQuery.value ||
      s.name?.includes(searchQuery.value) ||
      s.mobile_no?.includes(searchQuery.value)

    const matchStatus =
      !statusFilter.value || s.status === statusFilter.value

    return matchSearch && matchStatus
  })

  switch (sortBy.value) {
    case 'name':
      filtered.sort((a, b) => a.name.localeCompare(b.name, 'ar'))
      break
    case 'supply':
      filtered.sort((a, b) => b.totalSupplies - a.totalSupplies)
      break
    case 'debt':
      filtered.sort((a, b) => b.due_amount - a.due_amount)
      break
    default:
      filtered.sort(
        (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
      )
  }

  return filtered
})

/* =========================
   Helpers
========================= */
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

/* =========================
   Actions
========================= */
const openCreateModal = () => {
  editingSupplier.value = null
  showModal.value = true
}

const editSupplier = (supplier) => {
  editingSupplier.value = { ...supplier }
  showModal.value = true
}

const viewSupplier = (supplier) => {
  selectedSupplier.value = supplier
  showProfileModal.value = true
}

const deleteSupplier = async (id) => {
  if (confirm('Delete this supplier?')) {
    suppliers.value = suppliers.value.filter(s => s.id !== id)
  }
}

const saveSupplier = async (supplier) => {
  try {
    console.log("**supplier** payload is :", supplier)
    const response = await SuppliersStore.createSupplier(supplier)
    console.log("Response from createSupplier API:", response)
    if (response && response.status === 'success' && response.status_code === 201){
      console.log("Supplier saved successfully:", response)
      await loadSuppliersFinancialData()
      showModal.value = false
      window.$toast?.success?.(response.message || 'Supplier saved successfully')
    }
    if (response && response.status === 'error') {
      window.$toast?.error?.(response.message)
    }
  } catch (error) {
    console.error('Error saving supplier:', error)
  }
}

const exportSuppliers = () => {
  const csv = [
    ['Supplier Name', 'Phone', 'Email', 'Address', 'Due Amount', 'Total Purchases', 'Status'],
    ...filteredSuppliers.value.map(s => [
      s.name,
      s.mobile_no,
      s.email_contact,
      s.address,
      s.due_amount,
      s.totalSupplies,
      getStatusLabel(s.status)
    ])
  ]

  const csvContent = csv
    .map(row => row.map(cell => `"${cell}"`).join(','))
    .join('\n')

  const blob = new Blob([csvContent], {
    type: 'text/csv;charset=utf-8;'
  })

  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.href = url
  link.download = `suppliers-${new Date().toISOString().split('T')[0]}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/* =========================
   Data Loading
========================= */
const loadSuppliersFinancialData = async () => {
  try {
    const response =
      await SuppliersStore.fetchSuppliersFinancialData(
        toRaw(pos_profile.value)
      )
    console.log("Suppliers financial data loaded:", response)
    suppliers.value = response
  } catch (error) {
    console.error('Error loading suppliers financial data:', error)
  }
}

/* =========================
   Lifecycle
========================= */
onMounted(async () => {
  await shiftStore.checkActiveShift()
  await suppliersStore.loadSupplierGroups()
  await loadSuppliersFinancialData()
})
</script>

<style scoped>
table {
  border-collapse: collapse;
}
</style>
