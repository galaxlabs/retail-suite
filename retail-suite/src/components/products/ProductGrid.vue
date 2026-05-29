<!-- ProductGrid.vue -->
<template>
  <div class="h-full flex flex-col overflow-hidden gap-3 mt-3">
    <FilterBar
      v-if="!simpleMode"
      v-model:selectedPriceList="productsStore.selectedPriceList"
      v-model:selectedWarehouse="productsStore.selectedWarehouse"
      :price-lists="productsStore.priceLists"
      :warehouses="productsStore.warehouses"
      :is-loading="productsStore.isLoading"
      @reload="productsStore.loadProductsFromFrappeDB()"
    />

    <CategoryFilter v-if="!simpleMode" v-model="selectedCategory" />

    <div class="flex-1 overflow-y-auto px-1">
      <div
        v-if="productsStore.error && productsStore.products.length === 0"
        class="select-none rounded-3xl flex flex-wrap content-center justify-center h-full"
        :style="{ background: 'var(--warning-bg)', color: 'var(--warning-border)' }"
      >
        <div class="w-full text-center px-4">
          <WarningIcon class="w-12 h-12 mx-auto mb-2" />
          <p class="text-lg font-semibold">Failed to load items</p>
          <p class="text-sm mt-1 opacity-75">{{ productsStore.error }}</p>
          <button
            @click="productsStore.loadProductsFromFrappeDB()"
            class="mt-4 px-4 py-2 rounded-lg text-white text-sm font-medium"
            :style="{ background: 'var(--focus-ring)' }"
          >Retry</button>
        </div>
      </div>

      <div
        v-else-if="productsStore.products.length === 0 && !productsStore.isLoading"
        class="select-none rounded-3xl flex flex-wrap content-center justify-center h-full opacity-25"
        :style="{ background: 'var(--item-bg)', color: 'var(--text-main)' }"
      >
        <div class="w-full text-center">
          <EmptyDatabaseIcon />
          <p class="text-xl mt-2">No items found</p>
        </div>
      </div>

      <div
        v-else-if="productsStore.isLoading"
        class="select-none flex flex-wrap content-center justify-center h-full opacity-40"
        :style="{ color: 'var(--text-main)' }"
      >
        <div class="w-full text-center">
          <LoadingSpinner />
          <p class="text-xl mt-4">Loading items...</p>
        </div>
      </div>

      <div
        v-else-if="filteredProducts.length === 0 && (searchKeyword || selectedCategory)"
        class="select-none flex flex-wrap content-center justify-center h-full opacity-25"
        :style="{ color: 'var(--text-main)' }"
      >
        <div class="w-full text-center">
          <EmptySearchIcon />
          <p class="text-xl mt-2">No matching items</p>
          <p class="text-sm mt-1" :style="{ color: 'var(--text-muted)' }">
            "{{ searchKeyword || selectedCategory }}"
          </p>
        </div>
      </div>

      <div
        v-else
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 pb-4"
      >
        <ProductCard
          v-for="product in filteredProducts"
          :key="product.item_code"
          :product="product"
          :is-in-cart="cartStore.isInCart(product.item_code)"
          :cart-quantity="cartStore.getProductQuantity(product.item_code)"
          @add-to-cart="handleAddToCart"
          @remove-from-cart="handleRemoveFromCart"
          @view-details="handleViewDetails"
        />
      </div>

      <div
        v-if="productsStore.hasMore && !simpleMode && !searchKeyword"
        class="flex justify-center py-3"
      >
        <button
          @click="productsStore.loadMoreProducts()"
          :disabled="productsStore.isLoading"
          class="px-6 py-2 rounded-lg text-sm font-medium transition disabled:opacity-50"
          :style="{ background: 'var(--item-bg)', color: 'var(--focus-ring)', border: '1px solid var(--focus-ring)' }"
        >
          {{ productsStore.isLoading ? 'Loading...' : 'Load More' }}
        </button>
      </div>

      <div
        v-if="(searchKeyword || selectedCategory) && filteredProducts.length > 0"
        class="text-center text-xs mt-2 pb-2"
        :style="{ color: 'var(--text-muted)' }"
      >
        {{ filteredProducts.length }} items
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import ProductCard from './ProductCard.vue'
import CategoryFilter from './CategoryFilter.vue'
import FilterBar from './FilterBar.vue'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import EmptyDatabaseIcon from '@/components/icons/EmptyDatabaseIcon.svg'
import EmptySearchIcon from '@/components/icons/EmptySearchIcon.svg'
import WarningIcon from '@/components/icons/WarningIcon.svg'

const props = defineProps({
  searchKeyword: { type: String, default: '' },
  simpleMode: { type: Boolean, default: false },
})

const emit = defineEmits(['add-to-cart', 'remove-from-cart', 'view-details'])

const productsStore = useProductsStore()
const cartStore = useCartStore()
const selectedCategory = ref('')

let searchTimer = null

const normalizedKeyword = computed(() => props.searchKeyword.toLowerCase().trim())

const filteredProducts = computed(() => {
  let list = productsStore.products

  if (!props.simpleMode && selectedCategory.value) {
    list = list.filter((p) => p.item_group === selectedCategory.value)
  }

  const kw = normalizedKeyword.value
  if (kw) {
    list = list.filter((p) =>
      p.item_code?.toLowerCase().includes(kw) ||
      p.item_name?.toLowerCase().includes(kw) ||
      p.item_group?.toLowerCase().includes(kw) ||
      p.description?.toLowerCase().includes(kw) ||
      p.barcode?.toLowerCase().includes(kw) ||
      (Array.isArray(p.item_barcode) && p.item_barcode.some((b) => b?.barcode?.toLowerCase().includes(kw))) ||
      (Array.isArray(p.barcodes) && p.barcodes.some((b) => b?.barcode?.toLowerCase().includes(kw)))
    )
  }

  return list
})

watch(
  () => props.searchKeyword,
  (kw) => {
    productsStore.setSearchKeyword(kw)

    if (searchTimer) {
      clearTimeout(searchTimer)
    }

    searchTimer = setTimeout(async () => {
      if (!kw || kw.trim().length >= 2) {
        await productsStore.loadProductsFromFrappeDB()
      }
    }, 300)
  }
)

const handleAddToCart = (p) => {
  cartStore.addToCart(p)
  emit('add-to-cart', p)
}

const handleRemoveFromCart = (p) => {
  cartStore.removeFromCart(p.item_code)
  emit('remove-from-cart', p)
}

const handleViewDetails = (p) => emit('view-details', p)

const LoadingSpinner = {
  template: `
    <div style="
      display:inline-block; width:5rem; height:5rem;
      border-radius:9999px; border:3px solid transparent;
      border-bottom-color:var(--text-muted);
      animation:spin 1s linear infinite;
    "></div>
  `,
}

onMounted(async () => {
  await productsStore.loadFilterOptions()
})
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
