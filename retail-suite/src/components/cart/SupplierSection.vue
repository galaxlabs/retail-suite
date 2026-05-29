<!-- SupplierSection.vue -->
<template>
  <div
    class="p-4"
    :style="{ borderBottom: '1px solid var(--card-border)' }"
  >
    <div
      class="flex items-stretch rounded-lg overflow-hidden"
      :style="{
        border: '1px solid var(--input-border)',
        background: 'var(--input-bg)'
      }"
    >
      <select
        v-model="selectedSupplier"
        @change="handleSupplierChange"
        class="flex-grow p-2 px-3 outline-none cursor-pointer transition-all"
        :style="{
          background: 'var(--input-bg)',
          color: 'var(--text-main)',
          border: 'none'
        }"
      >
        <option value="">Select Supplier</option>
        <option
          v-for="sup in suppliers"
          :key="sup.name"
          :value="sup.name"
        >
          {{ sup.supplier_name || sup.name }}
        </option>
      </select>
      <p v-if="loadError" class="text-xs mt-1" style="color: var(--warning-border);">{{ loadError }}</p>

      <button
        @click="showAddSupplierModal = true"
        class="flex items-center gap-2 px-3 py-2 font-bold text-white focus:outline-none transition-all whitespace-nowrap shadow-sm"
        :style="{
          background: primaryColor,
          color: '#fff',
          borderLeft: '1px solid var(--card-border)'
        }"
        title="Add New Supplier"
      >
        <svg class="w-5 h-5 font-bold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" />
        </svg>
        <span class="font-semibold text-sm">Supplier</span>
      </button>
    </div>

    <div
      v-if="selectedSupplier"
      class="mt-3 p-3 rounded text-sm"
      :style="{
        background: 'var(--info-bg)',
        color: 'var(--focus-ring)',
        border: '1px solid var(--info-border)'
      }"
    >
      Supplier: <strong>{{ selectedSupplierName }}</strong>
    </div>
  </div>

  <div class="mb-8">
    <SupplierModal
      v-show="showAddSupplierModal"
      :model-value="showAddSupplierModal"
      @close="showAddSupplierModal = false"
      @supplier-added="handleSupplierAdded"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getSuppliers } from '@/services/api'
import { useShiftStore } from '@/stores/shift'
import { useSettingsStore } from '@/stores/settings'
import SupplierModal from '@/components/modals/SupplierModal.vue'

const emit = defineEmits(['supplier-selected'])

const settingsStore = useSettingsStore()
const settings = computed(() => settingsStore.settings)
const primaryColor = computed(() => settings.value?.appearance?.primaryColor || '#06b6d4')

const selectedSupplier = ref('')
const suppliers = ref([])
const showAddSupplierModal = ref(false)
const loadError = ref('')
const shiftStore = useShiftStore()

const selectedSupplierName = computed(() => {
  const sup = suppliers.value.find(s => s.name === selectedSupplier.value)
  return sup?.supplier_name || sup?.name || selectedSupplier.value
})

const loadSuppliers = async () => {
  try {
    const res = await getSuppliers()
    const supplierList = res?.data || []
    if (supplierList.length === 0) {
      console.warn('SupplierSection: No suppliers returned. Raw response:', JSON.stringify(res))
    } else {
      console.log('SupplierSection: Loaded', supplierList.length, 'suppliers:', supplierList.map(s=>s.name))
    }
    suppliers.value = supplierList.map(s => ({
      name: s.name,
      supplier_name: s.supplier_name || s.name,
    }))
  } catch (e) {
    console.error('Failed to load suppliers:', e)
    loadError.value = 'Failed to load suppliers: ' + (e?.message || 'Unknown error')
  }
}

const handleSupplierChange = () => {
  const sup = suppliers.value.find(s => s.name === selectedSupplier.value)
  if (sup) {
    shiftStore.setCustomer(sup)
    emit('supplier-selected', sup)
  }
}

const handleSupplierAdded = async (newSupplier) => {
  showAddSupplierModal.value = false
  await loadSuppliers()
  if (newSupplier?.name) {
    selectedSupplier.value = newSupplier.name
    const sup = suppliers.value.find(s => s.name === newSupplier.name)
    if (sup) {
      shiftStore.setCustomer(sup)
      emit('supplier-selected', sup)
    }
  }
}

onMounted(async () => {
  await loadSuppliers()
  if (suppliers.value.length === 0 && !loadError.value) {
    loadError.value = 'No suppliers found. Create suppliers in ERPNext first.'
  }
})
</script>
