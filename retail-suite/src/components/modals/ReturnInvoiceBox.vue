<template>
  <!-- Modal Overlay -->
  <div
    class="fixed inset-0 flex items-center justify-center z-50 p-4"
    style="background: rgba(0,0,0,0.5)"
  >
    <div
      class="rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col"
      :style="{
        background: 'var(--card-bg)',
        border: '1px solid var(--card-border)',
        color: 'var(--text-main)'
      }"
    >
      <!-- Header -->
      <div
        class="flex items-center justify-between p-6"
        :style="{ borderBottom: '1px solid var(--card-border)' }"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-full flex items-center justify-center"
            :style="{
              background: 'var(--warning-bg)',
              border: '1px solid var(--warning-border)'
            }"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"
              :style="{ color: 'var(--warning-border)' }"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-bold" :style="{ color: 'var(--text-main)' }">
              Select Invoice for Return
            </h2>
            <p class="text-sm" :style="{ color: 'var(--text-muted)' }">
              Choose an invoice to process return
            </p>
          </div>
        </div>

        <button
          @click="handleCancel"
          class="transition-colors"
          :style="{ color: 'var(--text-muted)' }"
          @mouseover="$event.currentTarget.style.color = 'var(--text-main)'"
          @mouseleave="$event.currentTarget.style.color = 'var(--text-muted)'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Search Bar -->
      <div
        class="p-4"
        :style="{ borderBottom: '1px solid var(--card-border)' }"
      >
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by invoice number..."
            class="w-full px-4 py-3 pr-10 rounded-lg focus:outline-none transition-all"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              border: '1px solid var(--input-border)'
            }"
            @input="handleSearch"
          />
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute right-3 top-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"
            :style="{ color: 'var(--text-muted)' }"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      <!-- Invoice List -->
      <div class="flex-1 overflow-y-auto p-4">

        <!-- Loading -->
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div
            class="animate-spin rounded-full h-12 w-12"
            :style="{ borderBottom: '2px solid var(--warning-border)' }"
          />
        </div>

        <!-- Empty State -->
        <div
          v-else-if="filteredInvoices.length === 0"
          class="flex flex-col items-center justify-center py-12"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"
            :style="{ color: 'var(--text-muted)', opacity: 0.4 }"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="font-medium" :style="{ color: 'var(--text-sub)' }">No invoices found</p>
          <p class="text-sm mt-1" :style="{ color: 'var(--text-muted)' }">Try adjusting your search</p>
        </div>

        <!-- Invoice Cards -->
        <div v-else class="space-y-3">
          <div
            v-for="invoice in filteredInvoices"
            :key="invoice.name"
            @click="selectInvoice(invoice)"
            class="rounded-xl p-4 cursor-pointer transition-all duration-200"
            :style="selectedInvoiceId === invoice.name
              ? {
                  border: '1px solid var(--warning-border)',
                  background: 'var(--warning-bg)',
                  boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
                }
              : {
                  border: '1px solid var(--card-border)',
                  background: 'var(--card-bg)'
                }
            "
            @mouseover="e => { if (selectedInvoiceId !== invoice.name) e.currentTarget.style.borderColor = 'var(--warning-border)' }"
            @mouseleave="e => { if (selectedInvoiceId !== invoice.name) e.currentTarget.style.borderColor = 'var(--card-border)' }"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">

                <!-- Invoice Name + Selected Badge -->
                <div class="flex items-center gap-2 mb-2">
                  <h3 class="text-lg font-bold" :style="{ color: 'var(--text-main)' }">
                    {{ invoice.name }}
                  </h3>
                  <span
                    v-if="selectedInvoiceId === invoice.name"
                    class="px-2 py-0.5 text-white text-xs font-semibold rounded-full"
                    :style="{ background: 'var(--btn-danger)' }"
                  >
                    Selected
                  </span>
                </div>

                <!-- Date + Items Count -->
                <div class="flex items-center gap-4 text-sm mb-3" :style="{ color: 'var(--text-sub)' }">
                  <div class="flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span>{{ formatDate(invoice.posting_date) }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                    <span>{{ invoice.returnable_items?.length || 0 }} items</span>
                  </div>
                </div>

                <!-- Items Preview -->
                <div v-if="invoice.returnable_items?.length > 0" class="mb-3">
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="(item, idx) in invoice.returnable_items.slice(0, 3)"
                      :key="idx"
                      class="text-xs px-2 py-1 rounded"
                      :style="{
                        background: 'var(--item-bg)',
                        color: 'var(--text-sub)',
                        border: '1px solid var(--item-border)'
                      }"
                    >
                      {{ item.item_code }} ({{ item.returnable_qty }})
                    </span>
                    <span
                      v-if="invoice.returnable_items.length > 3"
                      class="text-xs px-2 py-1 rounded"
                      :style="{
                        background: 'var(--card-border)',
                        color: 'var(--text-muted)'
                      }"
                    >
                      +{{ invoice.returnable_items.length - 3 }} more
                    </span>
                  </div>
                </div>
              </div>

              <!-- Total Amount -->
              <div class="text-right ml-4">
                <p class="text-xs mb-1" :style="{ color: 'var(--text-muted)' }">Total</p>
                <p class="text-xl font-bold" :style="{ color: 'var(--text-main)' }">
                  {{ formatPrice(invoice.grand_total) }}
                </p>
              </div>
            </div>

            <!-- Radio Indicator -->
            <div class="flex items-center justify-end mt-2">
              <div
                class="w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all"
                :style="selectedInvoiceId === invoice.name
                  ? { borderColor: 'var(--warning-border)', background: 'var(--warning-border)' }
                  : { borderColor: 'var(--input-border)', background: 'transparent' }
                "
              >
                <div v-if="selectedInvoiceId === invoice.name" class="w-2 h-2 bg-white rounded-full" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div
        class="flex gap-3 p-4"
        :style="{
          borderTop: '1px solid var(--card-border)',
          background: 'var(--item-bg)'
        }"
      >
        <!-- Cancel -->
        <button
          @click="handleCancel"
          class="flex-1 px-6 py-3 font-semibold rounded-xl transition-colors"
          :style="{
            background: 'var(--card-bg)',
            color: 'var(--text-main)',
            border: '2px solid var(--card-border)'
          }"
          @mouseover="$event.currentTarget.style.background = 'var(--item-bg)'"
          @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
        >
          Cancel
        </button>

        <!-- Select Invoice -->
        <button
          @click="handleSelect"
          :disabled="!selectedInvoiceId"
          class="flex-1 px-6 py-3 font-semibold rounded-xl transition-colors"
          :style="selectedInvoiceId
            ? { background: 'var(--btn-danger)', color: '#fff', border: 'none' }
            : { background: 'var(--item-bg)', color: 'var(--text-muted)', border: '1px solid var(--card-border)', cursor: 'not-allowed' }
          "
        >
          Select Invoice
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useInvoicesStore } from '@/stores/invoices'
import { useShiftStore }            from '@/stores/shift'
import { useCartStore } from '../../stores/cart';
import { formatDate, formatPrice } from '../../utils/formatters';


const emit = defineEmits(['select', 'cancel'])

const invoicesStore = useInvoicesStore()

const searchQuery = ref('')
const selectedInvoiceId = ref(null)
const allInvoices = ref([])
const loading = ref(true)
// ─── Store ────────────────────────────────────────────────────────
const shiftStore      = useShiftStore()
const cartStore = useCartStore()
// ─── Computed ─────────────────────────────────────────────────────

const pos_opening_shift = computed(() => shiftStore.pos_opening_shift?.name || "")

const filteredInvoices = computed(() => {
  // Only show invoices with returnable items
  let list = allInvoices.value.filter(inv =>
    inv.returnable_items?.length > 0 && (inv.total_returnable_qty > 0)
  )
  if (!searchQuery.value) {
    return list
  }
  return list.filter(invoice =>
    invoice.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const selectedInvoice = computed(() => {
  return allInvoices.value.find(inv => inv.name === selectedInvoiceId.value)
})

const loadInvoices = async () => {
  loading.value = true
  try {
    allInvoices.value = await invoicesStore.allReturnableInvoices()
    // Sort by date descending
    console.log("All invs",allInvoices.value)
    // allInvoices.value.sort((a, b) => new Date(b.receiptDate) - new Date(a.receiptDate))
  } catch (error) {
    console.error('Error loading invoices:', error)
    allInvoices.value = []
  } finally {
    loading.value = false
  }
}

const selectInvoice = (invoice) => {
  selectedInvoiceId.value = invoice.name
}

const handleSearch = () => {
  // Search is handled by computed property
}

const handleSelect = () => {
if (selectedInvoice.value) {
  const plainInvoice = JSON.parse(JSON.stringify(selectedInvoice.value))
  const pos_profile_name = pos_opening_shift.value
  cartStore.setReturnAgainst(plainInvoice, pos_profile_name)
  invoicesStore.setReturnInvoice(plainInvoice)
  console.log('✅ Return selected Invoice:', plainInvoice)
  emit('select', plainInvoice)
}
}

const handleCancel = () => {
  emit('cancel')
}

// Load invoices on mount
onMounted(() => {
  loadInvoices()
})

</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
