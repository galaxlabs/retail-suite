<!-- inventoryBalance.vue -->
<template>

     <div class="w-full flex min-h-screen" style="font-size: 13px;" :style="{ background: 'var(--item-bg)' }">
      <main class="flex flex-col flex-1">
        <!-- ══════════════════ HEADER ══════════════════ -->
        <header
          class="mx-3 mt-3 sticky top-0 z-10 rounded-lg shadow-sm"
          :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
        >
          <div class="px-4 py-2 flex justify-between items-center">
            <div class="flex items-center gap-2">
              <InventoryIcon class="text-cyan-600":style="{ color: 'var(--focus-ring)' }"/>
               <div>
                <h1 class="text-sm font-bold" :style="{ color: 'var(--text-main)' }">Inventory Balance</h1>
                <p class="text-xs" :style="{ color: 'var(--text-secondary)' }">Report stock balances across Warehouses</p>
              </div>
            </div>
            <button
              @click="loadInventory"
              :disabled="isLoading"
              class="inline-flex items-center gap-1.5 text-white px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
              :style="{ background: 'var(--focus-ring)' }"
            >
              <RefreshCcw class="w-4 h-4" :class="{ 'animate-spin': isLoading }" />
              {{ isLoading ? 'Loading…' : 'Refresh' }}
            </button>
          </div>
        </header>
        <!-- ══════════════════ STATISTICS ══════════════════ -->
        <section class="px-3 pt-3">
          <div
            class="rounded-lg shadow-sm p-3"
            :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
          >
            <h2 class="text-xs font-semibold uppercase tracking-wide mb-2" :style="{ color: 'var(--text-muted)' }">
              Statistics
            </h2>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-3">
            <StatsCard title="Total Products" :value="totalProducts" icon="BarChart3" color="blue" />
            <StatsCard title="Categories" :value="categories.length" icon="Tag" color="green" />
            <StatsCard title="Low Stock" :value="lowStockCount" icon="TrendingUp" color="yellow" />
            <StatsCard title="Total Value" :value="formatPrice(totalInventoryValue)" icon="DollarSign" color="purple" />
          </div>
        </section>

        <!-- ══════════════════ FILTERS ══════════════════ -->
        <section class="px-3 pt-3">
         <div
            class="rounded-lg shadow-sm p-3"
            :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
          >
            <div class="grid grid-cols-2 md:grid-cols-5 gap-2 mb-2">
              <!-- Search -->
             <div class="col-span-2">
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Search Products</label>
                <div class="relative">
                  <Search class="absolute left-2.5 top-2 w-3 h-3 pointer-events-none" :style="{ color: 'var(--text-muted)' }" />
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Search by name, category, warehouse…"
                     class="w-full pl-8 pr-3 py-1.5 rounded-md focus:outline-none text-xs transition-all"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                    />
                </div>
              </div>

              <!-- Category -->
              <div>
                 <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Category</label>
                <select
                  v-model="selectedCategory"
                  class="w-full pl-3 pr-3 py-1.5 rounded-md focus:outline-none text-xs transition-all"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                >
                  <option value="">All Categories</option>
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>

              <!-- Warehouse -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Warehouse</label>
                <select
                    v-model="selectedWarehouse"
                    class="w-full pl-3 pr-3 py-1.5 rounded-md focus:outline-none text-xs transition-all"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                >
                  <option value="">All Warehouses</option>
                  <option v-for="wh in warehouses" :key="wh" :value="wh">{{ wh }}</option>
                </select>
              </div>

              <!-- Sort -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Sort By</label>
                <select
                  v-model="sortBy"
                  class="w-full pl-3 pr-3 py-1.5 rounded-md focus:outline-none text-xs transition-all"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                >
                  <option value="name">Name</option>
                  <option value="price">Price</option>
                  <option value="category">Category</option>
                  <option value="stock">Stock</option>
                  <option value="warehouse">Warehouse</option>
                </select>
              </div>

              <!-- Clear Filters -->
              <button
                  @click="resetFilters"
                  class="w-full px-3 py-1.5 rounded-md text-xs transition-colors"
                  :style="{
                    background: 'var(--item-bg)',
                    color: 'var(--text-sub)',
                    border: '1px solid var(--item-border)'
                  }"
                  @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                  @mouseleave="$event.currentTarget.style.background = 'var(--item-bg)'"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </section>

        <!-- ══════════════════ TABLE ══════════════════ -->
         <section class="px-3 pt-3 pb-3">
          <div
            class="rounded-lg shadow-sm flex flex-col overflow-hidden"
            :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
          >
              <!-- Table Header Bar -->
              <div
                class="px-4 py-2 flex items-center gap-2"
                :style="{ borderBottom: '1px solid var(--card-border)' }"
              >
                <InventoryIcon class="w-5 sm:w-6 h-5 sm:h-6 text-gray-700" :style="{ color: 'var(--focus-ring)' }" />
                <span class="text-xs font-semibold" :style="{ color: 'var(--text-sub)' }">Products</span>
                <span class="text-xs" :style="{ color: 'var(--text-muted)' }"> ({{ filteredProducts.length }})</span>
                <span v-if="isLoading" class="text-xs text-cyan-600 animate-pulse font-medium">Loading…</span>
                <span v-if="loading" class="text-xs ml-auto" :style="{ color: 'var(--text-muted)' }">⚠ {{ errorMessage }}</span>
            </div>

            <!-- Skeleton loader -->
            <div v-if="isLoading" class="p-6 space-y-3">
              <div v-for="i in 6" :key="i" class="h-12 bg-gray-100 rounded-lg animate-pulse" />
            </div>

            <!-- Table -->
            <div class="overflow-x-auto" style="scrollbar-width: thin;">
              <table class="w-full border-collapse" style="font-size: 12px; min-width: 700px;">

                <thead class="sticky top-0 z-10" :style="{ background: 'var(--item-bg)' }">
                  <tr>
                    <th v-for="header in ['Product', 'Warehouse', 'Category', 'Price', 'Stock', 'Status']"
                        :key="header"
                        class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide whitespace-nowrap"
                        :class="['warehouse', 'Status', 'Actions'].includes(label) ? 'text-center' : ''"
                        :style="{ color: 'var(--text-muted)', borderBottom: '1px solid var(--card-border)' }"
                    >
                      {{ header }}
                    </th>
                  </tr>
                </thead>

                <tbody class="divide-y divide-gray-200">
                   <!-- loading -->
                    <tr v-if="loading">
                      <td colspan="7" class="py-10 text-center">
                        <div class="flex items-center justify-center gap-2">
                          <svg class="w-5 h-5 animate-spin" :style="{ color: 'var(--focus-ring)' }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                          </svg>
                          <span class="text-xs" :style="{ color: 'var(--text-muted)' }">Loading...</span>
                        </div>
                      </td>
                    </tr>

                     <!-- empty state -->
                    <tr v-else-if="!loading && paginatedProducts.length === 0">
                      <td colspan="7" class="py-10 text-center">
                        <div class="flex flex-col items-center gap-3">
                          <PackageIcon class="w-12 h-12 text-gray-300" />
                          <p class="text-gray-500 font-medium">No products found</p>
                          <p class="text-gray-400 text-sm">
                            {{ searchQuery || selectedCategory || selectedWarehouse
                                ? 'Try adjusting your filters'
                                : 'No stock data available' }}
                          </p>
                        </div>
                      </td>
                    </tr>

                    <!-- Table Rows -->
                    <tr
                      v-for="product in paginatedProducts"
                      :key="`${product.item_code}-${product.warehouse}`"
                      class="transition-colors"
                      :style="{ borderBottom: '1px solid var(--card-border)' }"
                      @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                      @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                    >
                      <!-- Product -->
                      <td class="px-3 py-2 whitespace-nowrap">
                        <div class="flex items-center gap-3">
                          <img
                            :src="product?.image? `${config.FRAPPE_URL}${product?.image}`: defaultImageSrc"
                            :alt="product.item_name"
                            class="w-10 h-10 object-cover rounded-md border"
                            :style="{ borderColor: 'var(--item-border)' }"
                            @error="handleImageError"
                          />
                          <div>
                            <!-- <span class="text-sm font-medium" :style="{ color: 'var(--text-primary)' }">
                              {{ product.item_name }}
                            </span>
                            <span class="block text-xs" :style="{ color: 'var(--text-muted)' }">
                              {{ product.description || product.item_code }}
                            </span> -->
                            <div  class="font-mono text-xs px-2 py-0.5 rounded font-medium"
                        :style="{ background: 'var(--item-bg)', color: 'var(--text-sub)', border: '1px solid var(--item-border)' }">
                              {{ product.item_name }}
                            </div>
                            <div class="text-xs truncate max-w-[200px]" :style="{ color: 'var(--text-muted)' }">
                              {{ product.description || product.item_code }}
                            </div>
                          </div>
                        </div>
                      </td>

                      <!-- Warehouse -->
                      <td class="px-3 py-2 whitespace-nowrap">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-100 text-cyan-800">
                          {{ product.warehouse || '—' }}
                        </span>
                      </td>

                      <!-- Category -->
                      <td class="px-3 py-2 whitespace-nowrap">
                        <span
                          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="getCategoryClass(product.item_group)"
                        >
                          {{ product.item_group || 'Uncategorized' }}
                        </span>
                      </td>

                      <!-- Price -->
                      <td class="px-3 py-2 whitespace-nowrap">
                        <span class="text-sm font-medium" :style="{  background: 'var(--item-bg)', color: 'var(--text-sub)'}">
                          {{ formatPrice(product.rate) }}
                        </span>
                      </td>

                      <!-- Stock -->
                      <td class="px-3 py-2 whitespace-nowrap text-sm">
                        <span :class="getStockClass(product.actual_qty)">
                          {{ product.actual_qty }} units
                        </span>
                      </td>

                      <!-- Status -->
                      <td class="px-3 py-2 whitespace-nowrap">
                        <span
                          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="getStatusClass(product.actual_qty)"
                        >
                          {{ getStatusText(product.actual_qty) }}
                        </span>
                      </td>
                    </tr>
                </tbody>
              </table>
            </div>
            <!-- Pagination -->
               <p
                v-if="itemsPerPage > paginatedProducts.length"
                class="text-xs text-muted px-4 py-2.5 m-0 text-center"
                :style="{ color: 'var(--text-muted)' }"
              >
                the pagination  whill appears if Rows Greater than {{ itemsPerPage }}
              </p>
              <!-- Pagination -->
              <div
                v-if="totalPages > 1"
                class="px-4 py-2.5"
                :style="{ borderTop: '1px solid var(--card-border)', background: 'var(--item-bg)' }"
               >
                <div class="flex items-center justify-between">
                <span class="text-xs" :style="{ color: 'var(--text-muted)' }">
                    Total Pages: {{totalPages}}
                   </span>
                    <div class="flex items-center gap-1">
                      <button
                        @click="currentPage = Math.max(1, currentPage - 1)"
                        :disabled="currentPage === 1"
                        class="px-2 py-1 text-xs rounded disabled:opacity-40 transition-colors"
                        :style="{ border: '1px solid var(--card-border)', color: 'var(--text-sub)', background: 'var(--card-bg)' }"
                        @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                        @mouseleave="$event.currentTarget.style.background = 'var(--item-bg)'"
                      >
                        Previous
                      </button>

                      <!-- Page numbers -->
                      <button
                        v-for="page in visiblePages"
                        :key="page"
                        @click="currentPage = page"
                        class="px-2 py-1 text-xs rounded transition-colors font-medium"
                        :style="currentPage === page
                        ? { background: 'var(--focus-ring)', color: '#fff', border: '1px solid var(--focus-ring)' }
                        : { background: 'var(--card-bg)', color: 'var(--text-sub)', border: '1px solid var(--card-border)' }"
                        >{{ page }}</button>

                      <!-- btn Next -->
                      <button
                        @click="currentPage = Math.min(totalPages, currentPage + 1)"
                        :disabled="currentPage === totalPages"
                        class="px-2 py-1 text-xs rounded disabled:opacity-40 transition-colors"
                        :style="{ border: '1px solid var(--card-border)', color: 'var(--text-sub)', background: 'var(--card-bg)' }"
                        @mouseleave="$event.currentTarget.style.background = 'var(--item-bg)'"
                        @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
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
import { ref, computed, onMounted } from 'vue'
import { RefreshCcw, Search as SearchIcon, Package as PackageIcon } from 'lucide-vue-next'
import config from '@/config/frappe'
import StatsCard    from '@/layout/StatsCard.vue'
import MainLayout   from '@/layout/MainLayout.vue'
import InventoryIcon from '@/components/icons/InventoryIcon2.svg'
import { formatPrice } from '@/utils/formatters'
import { getInventoryBalance } from '@/services/api'


const defaultImage = '/img/default-product.jpg'
const defaultImageSrc = `${config.FRAPPE_URL}${defaultImage}`

// ============================================================
// STATE
// ============================================================
const products        = ref([])   // raw data from API
const isLoading       = ref(false)
const errorMessage    = ref('')

const searchQuery      = ref('')
const selectedCategory = ref('')
const selectedWarehouse = ref('')
const sortBy           = ref('name')

// pagination
const currentPage      = ref(1)
const itemsPerPage     = ref(8)

const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredProducts.value.slice(start, start + itemsPerPage.value)
})

const totalPages = computed(() => {
  return Math.ceil(filteredProducts.value.length / itemsPerPage.value)
})
const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end   = Math.min(totalPages.value, start + maxVisible - 1)
  if (end - start < maxVisible - 1) start = Math.max(1, end - maxVisible + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})
// ============================================================
// DERIVED LISTS (for filter dropdowns)
// ============================================================
const categories = computed(() => {
  const set = new Set(products.value.map(p => p.item_group).filter(Boolean))
  return Array.from(set).sort()
})

const warehouses = computed(() => {
  const set = new Set(products.value.map(p => p.warehouse).filter(Boolean))
  return Array.from(set).sort()
})

// ============================================================
// STATS
// ============================================================
const totalProducts = computed(() => {
  // unique item_codes
  return new Set(products.value.map(p => p.item_code)).size
})

const lowStockCount = computed(() =>
  products.value.filter(p => p.actual_qty > 0 && p.actual_qty < 10).length
)

const totalInventoryValue = computed(() =>
  products.value.reduce((sum, p) => sum + (p.rate * p.actual_qty), 0)
)

// ============================================================
// FILTERED + SORTED TABLE DATA
// ============================================================
const filteredProducts = computed(() => {
  let list = [...products.value]

  // search
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(p =>
      p.item_name?.toLowerCase().includes(q) ||
      p.item_code?.toLowerCase().includes(q) ||
      p.item_group?.toLowerCase().includes(q) ||
      p.warehouse?.toLowerCase().includes(q) ||
      p.description?.toLowerCase().includes(q)
    )
  }

  // category filter
  if (selectedCategory.value) {
    list = list.filter(p => p.item_group === selectedCategory.value)
  }

  // warehouse filter
  if (selectedWarehouse.value) {
    list = list.filter(p => p.warehouse === selectedWarehouse.value)
  }

  // sort
  switch (sortBy.value) {
    case 'name':
      list.sort((a, b) => (a.item_name || '').localeCompare(b.item_name || ''))
      break
    case 'price':
      list.sort((a, b) => (a.rate || 0) - (b.rate || 0))
      break
    case 'category':
      list.sort((a, b) => (a.item_group || '').localeCompare(b.item_group || ''))
      break
    case 'stock':
      list.sort((a, b) => (b.actual_qty || 0) - (a.actual_qty || 0))
      break
    case 'warehouse':
      list.sort((a, b) => (a.warehouse || '').localeCompare(b.warehouse || ''))
      break
  }

  return list
})

// ============================================================
// DATA LOADING
// ============================================================
const loadInventory = async () => {
  isLoading.value    = true
  errorMessage.value = ''
  try {
    const response = await getInventoryBalance()
    if (response.status === 'success') {
      products.value = response.data
    } else {
      errorMessage.value = response.message || 'Failed to load inventory'
    }
  } catch (err) {
    console.error('loadInventory error:', err)
    errorMessage.value = 'Error loading inventory data'
  } finally {
    isLoading.value = false
  }
}

// ============================================================
// HELPERS
// ============================================================
// Dynamic color palette — cycles through a set of Tailwind pairs
const categoryColorPalette = [
  'bg-blue-100 text-blue-800',
  'bg-green-100 text-green-800',
  'bg-yellow-100 text-yellow-800',
  'bg-pink-100 text-pink-800',
  'bg-purple-100 text-purple-800',
  'bg-orange-100 text-orange-800',
  'bg-teal-100 text-teal-800',
  'bg-indigo-100 text-indigo-800',
]
const categoryColorMap = {}
let colorIndex = 0

const getCategoryClass = (category) => {
  if (!category) return 'bg-gray-100 text-gray-800'
  if (!categoryColorMap[category]) {
    categoryColorMap[category] = categoryColorPalette[colorIndex % categoryColorPalette.length]
    colorIndex++
  }
  return categoryColorMap[category]
}

const getStockClass = (qty) => {
  if (qty <= 0)  return 'text-red-600 font-semibold'
  if (qty < 10)  return 'text-yellow-600 font-semibold'
  return 'text-green-600 font-semibold'
}

const getStatusClass = (qty) => {
  if (qty <= 0)  return 'bg-red-100 text-red-800'
  if (qty < 10)  return 'bg-yellow-100 text-yellow-800'
  return 'bg-green-100 text-green-800'
}

const getStatusText = (qty) => {
  if (qty <= 0)  return 'Out of Stock'
  if (qty < 10)  return 'Low Stock'
  return 'In Stock'
}

const handleImageError = (e) => {
  e.target.src = ''
  e.target.classList.add('hidden')
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedWarehouse.value = ''
  sortBy.value = 'name'
  currentPage.value = 1
}
// ============================================================
// LIFECYCLE
// ============================================================
onMounted(() => {
  loadInventory()
})
</script>
