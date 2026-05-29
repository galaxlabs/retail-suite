<!-- ItemPrice.vue -->
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
              <Tag class="w-5 h-5" :style="{ color: 'var(--focus-ring)' }" />
              <div>
                <h1 class="text-sm font-bold" :style="{ color: 'var(--text-main)' }">Item Price</h1>
                <p class="text-xs" :style="{ color: 'var(--text-muted)' }">Manage pricing per price list</p>
              </div>
            </div>
            <button
              @click="openAddModal"
              class="inline-flex items-center gap-1.5 text-white px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
              :style="{ background: 'var(--focus-ring)' }"
            >
              <Plus class="w-3 h-3" /> Add Price
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
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
              <StatsCard title="Total Prices"  :value="itemPrices.length"       icon="Tag"        color="blue"   />
              <StatsCard title="Price Lists"   :value="priceLists.length"       icon="BarChart2"  color="green"  />
              <StatsCard title="Avg Price"     :value="formatPrice(avgPrice)"   icon="TrendingUp" color="purple" />
              <StatsCard title="Filtered"      :value="filteredPrices.length"   icon="Filter"     color="orange" />
            </div>
          </div>
        </section>

        <!-- ══════════════════ FILTERS ══════════════════ -->
        <section class="px-3 pt-3">
          <div
            class="rounded-lg shadow-sm p-3"
            :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
          >
            <div class="grid grid-cols-2 md:grid-cols-5 gap-2 mb-2">

              <!-- Search Item -->
              <div class="col-span-2">
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Search Item</label>
                <div class="relative">
                  <Search class="absolute left-2.5 top-2 w-3 h-3 pointer-events-none" :style="{ color: 'var(--text-muted)' }" />
                  <input
                    v-model="searchItem"
                    type="text"
                    placeholder="Item code or name..."
                    class="w-full pl-8 pr-3 py-1.5 rounded-md focus:outline-none text-xs transition-all"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                  />
                </div>
              </div>

              <!-- Price List -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Price List</label>
                <select
                  v-model="selectedPriceList"
                  @change="loadItemPrices"
                  class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
                  :style="{
                    background: 'var(--input-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--input-border)'
                  }"
                >
                  <option value="">All Price Lists</option>
                  <option v-for="pl in priceLists" :key="pl.name" :value="pl.name">
                    {{ pl.price_list_name || pl.name }}{{ pl.is_pos_price_list ? ' ⭐' : '' }}
                  </option>
                </select>
              </div>

              <!-- Currency -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Currency</label>
                <input
                  v-model="searchCurrency"
                  type="text"
                  placeholder="USD, SAR..."
                  class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
                  :style="{
                    background: 'var(--input-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--input-border)'
                  }"
                />
              </div>

              <!-- Count -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Count</label>
                <div
                  class="px-2 py-1.5 rounded-md font-semibold text-xs"
                  :style="{
                    background: 'var(--item-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--item-border)'
                  }"
                >
                  {{ filteredPrices.length }} prices
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between gap-2">
              <!-- POS Badge -->
              <div v-if="posPriceList" class="flex items-center gap-2">
                <span
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
                  :style="{ background: 'var(--warning-bg)', color: 'var(--warning-border)', border: '1px solid var(--warning-border)' }"
                >
                  <Star class="w-3 h-3" style="fill: currentColor;" />
                  POS Default: {{ posPriceList.price_list_name || posPriceList.name }}
                </span>
                <button
                  @click="selectedPriceList = posPriceList.name; loadItemPrices()"
                  class="text-xs font-medium"
                  :style="{ color: 'var(--focus-ring)' }"
                >
                  View POS Prices →
                </button>
              </div>
              <div v-else></div>

              <!-- Reset -->
              <button
                @click="resetFilters"
                class="px-3 py-1.5 rounded-md text-xs transition-colors"
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
              <Tag class="w-4 h-4" :style="{ color: 'var(--text-muted)' }" />
              <span class="text-xs font-semibold" :style="{ color: 'var(--text-sub)' }">All Prices</span>
              <span class="text-xs" :style="{ color: 'var(--text-muted)' }">({{ itemPrices.length }})</span>
              <span v-if="loading" class="text-xs ml-auto" :style="{ color: 'var(--text-muted)' }">Loading...</span>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto" style="scrollbar-width: thin;">
              <table class="w-full border-collapse" style="font-size: 12px; min-width: 700px;">
                <thead class="sticky top-0 z-10" :style="{ background: 'var(--item-bg)' }">
                  <tr>
                    <th
                      v-for="label in ['Item Code', 'Item Name', 'Price List', 'Rate', 'Currency', 'UOM', 'Valid From', 'Actions']"
                      :key="label"
                      class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide whitespace-nowrap"
                      :class="['Rate', 'Actions'].includes(label) ? 'text-center' : ''"
                      :style="{ color: 'var(--text-muted)', borderBottom: '1px solid var(--card-border)' }"
                    >
                      {{ label }}
                    </th>
                  </tr>
                </thead>

                <tbody>
                  <!-- Loading -->
                  <tr v-if="loading">
                    <td colspan="8" class="py-10 text-center">
                      <div class="flex items-center justify-center gap-2">
                        <svg class="w-5 h-5 animate-spin" :style="{ color: 'var(--focus-ring)' }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                        </svg>
                        <span class="text-xs" :style="{ color: 'var(--text-muted)' }">Loading prices...</span>
                      </div>
                    </td>
                  </tr>

                  <!-- Empty -->
                  <tr v-else-if="paginatedPrices.length === 0">
                    <td colspan="8" class="py-14 text-center">
                      <div class="flex flex-col items-center gap-2">
                        <div
                          class="w-10 h-10 flex items-center justify-center rounded-full mb-1"
                          :style="{ background: 'var(--item-bg)' }"
                        >
                          <Tag class="w-5 h-5" :style="{ color: 'var(--text-muted)', opacity: 0.5 }" />
                        </div>
                        <p class="text-xs font-medium" :style="{ color: 'var(--text-sub)' }">No Item Prices Found</p>
                        <p class="text-xs" :style="{ color: 'var(--text-muted)' }">Try adjusting your filters</p>
                      </div>
                    </td>
                  </tr>

                  <!-- Rows -->
                  <tr
                    v-else
                    v-for="price in paginatedPrices"
                    :key="price.name"
                    class="transition-colors"
                    :style="{ borderBottom: '1px solid var(--card-border)' }"
                    @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                    @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                  >
                    <!-- Item Code -->
                    <td class="px-3 py-2 whitespace-nowrap">
                      <span
                        class="font-mono text-xs px-2 py-0.5 rounded"
                        :style="{ background: 'var(--item-bg)', color: 'var(--text-sub)', border: '1px solid var(--item-border)' }"
                      >{{ price.item_code }}</span>
                    </td>

                    <!-- Item Name -->
                    <td class="px-3 py-2 whitespace-nowrap" :style="{ color: 'var(--text-sub)' }">
                      {{ price.item_name || '—' }}
                    </td>

                    <!-- Price List -->
                    <td class="px-3 py-2 whitespace-nowrap">
                      <span class="inline-flex items-center gap-1 text-xs" :style="{ color: 'var(--text-sub)' }">
                        <Star
                          v-if="isPOSPriceList(price.price_list)"
                          class="w-3 h-3"
                          style="fill: #f59e0b; color: #f59e0b;"
                        />
                        {{ price.price_list }}
                      </span>
                    </td>

                    <!-- Rate -->
                    <td class="px-3 py-2 whitespace-nowrap text-center font-semibold" :style="{ color: 'var(--focus-ring)' }">
                      {{ formatPrice(price.price_list_rate) }}
                    </td>

                    <!-- Currency -->
                    <td class="px-3 py-2 whitespace-nowrap text-xs" :style="{ color: 'var(--text-muted)' }">
                      {{ price.currency || '—' }}
                    </td>

                    <!-- UOM -->
                    <td class="px-3 py-2 whitespace-nowrap text-xs" :style="{ color: 'var(--text-muted)' }">
                      {{ price.uom || '—' }}
                    </td>

                    <!-- Valid From -->
                    <td class="px-3 py-2 whitespace-nowrap text-xs" :style="{ color: 'var(--text-muted)' }">
                      {{ formatDate(price.valid_from) }}
                    </td>

                    <!-- Actions -->
                    <td class="px-3 py-2 whitespace-nowrap">
                      <div class="flex items-center justify-center gap-1">
                        <button
                          @click="editPrice(price)"
                          class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                          :style="{ color: 'var(--focus-ring)' }"
                          @mouseover="$event.currentTarget.style.background = 'var(--info-bg)'"
                          @mouseleave="$event.currentTarget.style.background = 'transparent'"
                          title="Edit"
                        >
                          <Edit2 class="w-3.5 h-3.5" />
                        </button>
                        <button
                          @click="deletePrice(price)"
                          class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                          style="color: #ef4444;"
                          @mouseover="$event.currentTarget.style.background = '#fef2f2'"
                          @mouseleave="$event.currentTarget.style.background = 'transparent'"
                          title="Delete"
                        >
                          <Trash2 class="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div
              v-if="totalPages > 1"
              class="px-4 py-2.5"
              :style="{ borderTop: '1px solid var(--card-border)', background: 'var(--item-bg)' }"
            >
              <div class="flex items-center justify-between">
                <span class="text-xs" :style="{ color: 'var(--text-muted)' }">
                  Showing {{ ((currentPage - 1) * itemsPerPage) + 1 }}–{{ Math.min(currentPage * itemsPerPage, filteredPrices.length) }}
                  of {{ filteredPrices.length }}
                </span>
                <div class="flex items-center gap-1">
                  <button
                    @click="currentPage = Math.max(1, currentPage - 1)"
                    :disabled="currentPage === 1"
                    class="px-2 py-1 text-xs rounded disabled:opacity-40 transition-colors"
                    :style="{ border: '1px solid var(--card-border)', color: 'var(--text-sub)', background: 'var(--card-bg)' }"
                  >Prev</button>

                  <button
                    v-for="page in visiblePages"
                    :key="page"
                    @click="currentPage = page"
                    class="px-2 py-1 text-xs rounded transition-colors font-medium"
                    :style="currentPage === page
                      ? { background: 'var(--focus-ring)', color: '#fff', border: '1px solid var(--focus-ring)' }
                      : { background: 'var(--card-bg)', color: 'var(--text-sub)', border: '1px solid var(--card-border)' }"
                  >{{ page }}</button>

                  <button
                    @click="currentPage = Math.min(totalPages, currentPage + 1)"
                    :disabled="currentPage === totalPages"
                    class="px-2 py-1 text-xs rounded disabled:opacity-40 transition-colors"
                    :style="{ border: '1px solid var(--card-border)', color: 'var(--text-sub)', background: 'var(--card-bg)' }"
                  >Next</button>
                </div>
              </div>
            </div>

          </div>
        </section>

        <!-- ══════════════════ MODAL ══════════════════ -->
        <div
          v-if="showModal"
          class="fixed inset-0 flex items-center justify-center z-50 p-4"
          style="background: rgba(0,0,0,0.5);"
          @click.self="closeModal"
        >
          <div
            class="w-full max-w-lg rounded-xl shadow-2xl"
            :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
          >
            <!-- Modal Header -->
            <div
              class="flex items-center justify-between px-5 py-3"
              :style="{ borderBottom: '1px solid var(--card-border)' }"
            >
              <h3 class="text-sm font-semibold" :style="{ color: 'var(--text-main)' }">
                {{ isEditing ? 'Edit Item Price' : 'Add Item Price' }}
              </h3>
              <button
                @click="closeModal"
                class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                :style="{ color: 'var(--text-muted)' }"
                @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                @mouseleave="$event.currentTarget.style.background = 'transparent'"
              >
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- Modal Body -->
            <div class="p-5 space-y-3">

              <!-- Item Code -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Item Code *</label>
                <select
                  v-model="form.item_code"
                  @change="onItemChange"
                  :disabled="isEditing"
                  class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none disabled:opacity-60"
                  :style="{
                    background: isEditing ? 'var(--item-bg)' : 'var(--input-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--input-border)'
                  }"
                >
                  <option value="">Select Item</option>
                  <option v-for="item in inventoryItems" :key="item.item_code" :value="item.item_code">
                    {{ item.item_code }} — {{ item.item_name }}
                  </option>
                </select>
              </div>

              <!-- Price List -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Price List *</label>
                <select
                  v-model="form.price_list"
                  :disabled="isEditing"
                  class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none disabled:opacity-60"
                  :style="{
                    background: isEditing ? 'var(--item-bg)' : 'var(--input-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--input-border)'
                  }"
                >
                  <option value="">Select Price List</option>
                  <option v-for="pl in priceLists" :key="pl.name" :value="pl.name">
                    {{ pl.price_list_name || pl.name }}
                  </option>
                </select>
              </div>

              <!-- Rate + Currency -->
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Price (Rate) *</label>
                  <input
                    v-model.number="form.price_list_rate"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="0.00"
                    class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none text-right"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                  />
                </div>
                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Currency</label>
                  <input
                    v-model="form.currency"
                    type="text"
                    placeholder="SAR"
                    class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                  />
                </div>
              </div>

              <!-- UOM + Valid From -->
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">UOM</label>
                  <select
                    v-model="form.uom"
                    class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                  >
                    <option value="">Select UOM</option>
                    <option v-for="uom in uoms" :key="uom.name" :value="uom.name">{{ uom.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Valid From</label>
                  <input
                    v-model="form.valid_from"
                    type="date"
                    class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                  />
                </div>
              </div>

              <!-- Valid Upto -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Valid Upto</label>
                <input
                  v-model="form.valid_upto"
                  type="date"
                  class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
                  :style="{
                    background: 'var(--input-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--input-border)'
                  }"
                />
              </div>

              <!-- Error -->
              <div
                v-if="modalError"
                class="p-3 rounded-md text-xs"
                :style="{ background: 'var(--warning-bg)', color: 'var(--warning-border)', border: '1px solid var(--warning-border)' }"
              >
                {{ modalError }}
              </div>
            </div>

            <!-- Modal Footer -->
            <div
              class="flex justify-end gap-2 px-5 py-3"
              :style="{ borderTop: '1px solid var(--card-border)' }"
            >
              <button
                @click="closeModal"
                class="px-4 py-1.5 text-xs rounded-md transition-colors"
                :style="{
                  background: 'var(--item-bg)',
                  color: 'var(--text-sub)',
                  border: '1px solid var(--item-border)'
                }"
                @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                @mouseleave="$event.currentTarget.style.background = 'var(--item-bg)'"
              >
                Cancel
              </button>
              <button
                @click="savePrice"
                :disabled="isSaving"
                class="px-4 py-1.5 text-xs text-white rounded-md font-medium transition-colors disabled:opacity-50"
                :style="{ background: 'var(--focus-ring)' }"
              >
                {{ isSaving ? 'Saving...' : (isEditing ? 'Update' : 'Add') }} Price
              </button>
            </div>
          </div>
        </div>

      </main>
    </div>

</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useConfirm } from '@/composables/useConfirm'
import StatsCard from '@/layout/StatsCard.vue'
import { useInventoryStore } from '@/stores/inventory'
import { formatPrice } from '@/utils/formatters'
import { Tag, Plus, Edit2, Trash2, Star, X, Search } from 'lucide-vue-next'
import {
  getPOSPriceList,
  getAllPriceLists,
  getItemPrices,
  createItemPrice,
  updateItemPrice,
  deleteItemPrice,
} from '@/services/api'

// ─── State ────────────────────────────────────────────
const inventoryStore    = useInventoryStore()
const { confirm }       = useConfirm()
const loading           = ref(false)
const itemPrices        = ref([])
const priceLists        = ref([])
const posPriceList      = ref(null)
const uoms              = ref([])

const selectedPriceList = ref('')
const searchItem        = ref('')
const searchCurrency    = ref('')

// Pagination
const currentPage  = ref(1)
const itemsPerPage = ref(20)

const showModal   = ref(false)
const isEditing   = ref(false)
const isSaving    = ref(false)
const modalError  = ref('')
const editingName = ref(null)
const form        = ref(getDefaultForm())

function getDefaultForm() {
  return {
    item_code:       '',
    item_name:       '',
    price_list:      '',
    price_list_rate: 0,
    currency:        'SAR',
    uom:             '',
    valid_from:      '',
    valid_upto:      '',
  }
}

// ─── Inventory Items ──────────────────────────────────
const inventoryItems = computed(() => inventoryStore.items || [])

// ─── Helpers ──────────────────────────────────────────
const unwrap = (res) => {
  const d = res?.data
  if (d && 'message' in d) return d.message
  return d ?? null
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '—'

const isPOSPriceList = (name) =>
  posPriceList.value && posPriceList.value.name === name

// ─── Computed ─────────────────────────────────────────
const filteredPrices = computed(() => {
  let data = [...itemPrices.value]
  if (searchItem.value) {
    const q = searchItem.value.toLowerCase()
    data = data.filter(p =>
      p.item_code?.toLowerCase().includes(q) ||
      p.item_name?.toLowerCase().includes(q)
    )
  }
  if (searchCurrency.value) {
    data = data.filter(p =>
      p.currency?.toLowerCase().includes(searchCurrency.value.toLowerCase())
    )
  }
  return data
})

const paginatedPrices = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredPrices.value.slice(start, start + itemsPerPage.value)
})

const totalPages = computed(() =>
  Math.ceil(filteredPrices.value.length / itemsPerPage.value)
)

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end   = Math.min(totalPages.value, start + maxVisible - 1)
  if (end - start < maxVisible - 1) start = Math.max(1, end - maxVisible + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const avgPrice = computed(() => {
  if (!itemPrices.value.length) return 0
  const sum = itemPrices.value.reduce((s, p) => s + (p.price_list_rate || 0), 0)
  return sum / itemPrices.value.length
})

// reset page when filters change
const resetPage = () => { currentPage.value = 1 }

// ─── Load ─────────────────────────────────────────────
const loadAll = async () => {
  loading.value = true
  try {
    const [plRes, posRes, priceRes] = await Promise.all([
      getAllPriceLists(),
      getPOSPriceList(),
      getItemPrices({item_code: form.value.item_code, price_list: selectedPriceList.value }),
    ])
    console.log("plRes",plRes)
    console.log("posPriceList",posRes)
    console.log("itemPrices",priceRes)
    console.log("itemPrices",unwrap(priceRes))
    priceLists.value   = plRes   || []
    posPriceList.value = posRes  || null
    itemPrices.value   = priceRes || []
  } catch (e) {
    console.error('Error loading item prices:', e)
  } finally {
    loading.value = false
  }
}

const loadItemPrices = async () => {
  loading.value = true
  resetPage()
  try {
    const res = await getItemPrices({item_code: form.value.item_code, price_list: selectedPriceList.value })
    console.log("item prices: ",res)
    itemPrices.value = res || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// ─── Modal ────────────────────────────────────────────
const openAddModal = () => {
  isEditing.value   = false
  editingName.value = null
  form.value        = getDefaultForm()
  if (selectedPriceList.value) form.value.price_list = selectedPriceList.value
  modalError.value  = ''
  showModal.value   = true
}

const editPrice = (price) => {
  isEditing.value   = true
  editingName.value = price.name
  form.value = {
    item_code:       price.item_code,
    item_name:       price.item_name || '',
    price_list:      price.price_list,
    price_list_rate: price.price_list_rate,
    currency:        price.currency || 'SAR',
    uom:             price.uom || '',
    valid_from:      price.valid_from || '',
    valid_upto:      price.valid_upto || '',
  }
  modalError.value = ''
  showModal.value  = true
}

const closeModal = () => { showModal.value = false; editingName.value = null }

const savePrice = async () => {
  modalError.value = ''
  if (!form.value.item_code)          { modalError.value = 'Item Code is required'; return }
  if (!form.value.price_list)         { modalError.value = 'Price List is required'; return }
  if (form.value.price_list_rate < 0) { modalError.value = 'Rate must be ≥ 0'; return }

  isSaving.value = true
  try {
    if (isEditing.value && editingName.value) {
      await updateItemPrice(editingName.value, form.value)
    } else {
      await createItemPrice(form.value)
    }
    await loadItemPrices()
    closeModal()
  } catch (e) {
    console.error(e)
    modalError.value = e?.response?.data?.message || 'Error saving price.'
  } finally {
    isSaving.value = false
  }
}

const deletePrice = async (price) => {

  const confirmed = await confirm({
    type: 'delete',
    title: 'Delete Price',
    message: `Delete price for "${price.item_code}" in "${price.price_list}"?`,
    confirmLabel: 'Delete',
  })
  if (!confirmed) return
  try {
    await deleteItemPrice(price.name)
    itemPrices.value = itemPrices.value.filter(p => p.name !== price.name)
  } catch (e) {
    console.error(e)
    window.$toast?.error('Error deleting price')
  }
}

const onItemChange = () => {
  const found = inventoryItems.value.find(i => i.item_code === form.value.item_code)
  if (found) {
    form.value.item_name = found.item_name
    form.value.uom       = found.stock_uom || ''
  }
}

const resetFilters = () => {
  selectedPriceList.value = ''
  searchItem.value        = ''
  searchCurrency.value    = ''
  resetPage()
  loadItemPrices()
}

// ─── Lifecycle ────────────────────────────────────────
onMounted(async () => {
  await loadAll()
  await inventoryStore.loadItems?.()
  const fetchedUoms = await inventoryStore.loadUOM()
  uoms.value = fetchedUoms || []
})
</script>
