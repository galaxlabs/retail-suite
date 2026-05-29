<!-- CategoryFilter.vue -->
<template>
  <div class="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide">
    <!-- All button -->
    <button
      class="flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-semibold transition-all duration-200"
      :style="modelValue === '' ? activeStyle : inactiveStyle"
      @click="emit('update:modelValue', '')"
    >
      All Categories
    </button>

    <!-- Category buttons -->
    <button
      v-for="cat in categories"
      :key="cat"
      class="flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 whitespace-nowrap"
      :style="modelValue === cat ? activeStyle : inactiveStyle"
      @click="emit('update:modelValue', cat)"
    >
      {{ cat }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useProductsStore } from '@/stores/products'
import { useSettingsStore } from '@/stores/settings'
const settingsStore = useSettingsStore()
const settings = computed(() => settingsStore.settings)
const primaryColor = computed(() => {
  return settings.value?.appearance?.primaryColor || '#06b6d4'
})

defineProps({
  modelValue: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])
const productsStore = useProductsStore()

// استخرج الـ categories الفريدة سے الـ products
const categories = computed(() => {
  const cats = productsStore.products
    .map(p => p.item_group)
    .filter(Boolean)
  return [...new Set(cats)].sort()
})

const activeStyle = {
  background: primaryColor.value,
  color: '#fff',
  boxShadow: '0 2px 8px rgba(6,182,212,0.3)'
}

const inactiveStyle = {
  background: 'var(--item-bg)',
  color: 'var(--text-muted)',
  border: '1px solid var(--card-border)'
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
