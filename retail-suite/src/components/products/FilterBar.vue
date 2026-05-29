<!-- FilterBar.vue -->
<template>
  <div
    class="flex flex-wrap items-center gap-3 px-3 py-2 rounded-2xl"
    :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
  >
    <!-- Price List -->
    <div class="flex items-center gap-2 flex-1 min-w-0">
      <span class="text-xs font-semibold whitespace-nowrap" :style="{ color: 'var(--text-muted)' }">
        Price List
      </span>
      <select
        :value="selectedPriceList"
        class="flex-1 text-sm rounded-xl px-3 py-1.5 outline-none min-w-0 transition-all"
        :style="selectStyle"
        @change="emit('update:selectedPriceList', $event.target.value)"
      >
        <option
          v-for="pl in priceLists"
          :key="pl.name"
          :value="pl.name"
        >
          {{ pl.name }}
        </option>
      </select>
    </div>

    <!-- Divider -->
    <div class="w-px h-6" :style="{ background: 'var(--card-border)' }" />

    <!-- Warehouse -->
    <div class="flex items-center gap-2 flex-1 min-w-0">
      <span class="text-xs font-semibold whitespace-nowrap" :style="{ color: 'var(--text-muted)' }">
        Warehouse
      </span>
      <select
        :value="selectedWarehouse"
        class="flex-1 text-sm rounded-xl px-3 py-1.5 outline-none min-w-0 transition-all"
        :style="selectStyle"
        @change="emit('update:selectedWarehouse', $event.target.value)"
      >
        <option value="">پہلے سے طے شدہ</option>
        <option
          v-for="wh in warehouses"
          :key="wh.name"
          :value="wh.name"
        >
          {{ wh.name }}
        </option>
      </select>
    </div>

    <!-- Reload Button -->
    <button
      class="flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all active:scale-95"
      :style="{ background: primaryColor, color: '#fff', border: '1px solid var(--card-border)' }"
      :disabled="isLoading"
      @click="emit('reload')"
    >
      <span v-if="isLoading" class="inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
      <span v-else>↻</span>
      <span>Reload</span>
    </button>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useProductsStore } from '@/stores/products'
import { storeToRefs } from 'pinia'
import { useSettingsStore } from '@/stores/settings'
const settingsStore = useSettingsStore()
const settings = computed(() => settingsStore.settings)
const primaryColor = computed(() => {
  return settings.value?.appearance?.primaryColor || '#06b6d4'
})

defineProps({
  selectedPriceList: { type: String, default: '' },
  selectedWarehouse: { type: String, default: '' },
  priceLists: { type: Array, default: () => [] },
  warehouses: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
})

const emit = defineEmits([
  'update:selectedPriceList',
  'update:selectedWarehouse',
  'reload'
])

const selectStyle = {
  background: 'var(--item-bg)',
  color: 'var(--text-main)',
  border: '1px solid var(--card-border)',
  cursor: 'pointer'
}
</script>
