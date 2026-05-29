<!-- inventoryBalance.vue -->
<template>
  <div class="w-full flex min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <aside class="sm:block sm:w-[25%] md:w-[20%] lg:w-[8%] h-[screen] bg-gray-50 ">
      <Sidebar  />
    </aside>

    <!-- Main Content -->
    <main class="w-full sm:w-[75%] md:w-[80%] lg:w-[90%] flex flex-col min-h-screen">
        <!-- Header -->
        <header class="ml-6 mr-6 sticky top-0 z-10 bg-white rounded-xl shadow-sm border-b border-gray-200">
          <div class="px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
              <InventoryIcon class="w-8 h-8 text-cyan-600" />
              <h1 class="text-lg font-bold text-gray-900">Inventory Management</h1>
              </div>

              <div class="flex gap-3">
                  <button
                    @click="showAddModal = true"
                  class="inline-flex items-center gap-2 bg-gray-500 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors duration-200"
                      >
                    <PlusIcon class="w-4 h-4 ml-2" />
                    Add Product
                  </button>
              </div>
          </div>

        </header>

        <!-- Stats Section -->
        <section class="flex-shrink-0 px-6 py-8">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-800 mb-6">Statistics</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatsCard title="Total Products" :value="productsStore.productsCount" icon="BarChart3" color="blue" />
            <StatsCard title="Categories" :value="Object.keys(productsStore.categorizedProducts).length" icon="DollarSign" color="green" />
            <StatsCard title="Low Stock" :value="lowStockCount" icon="TrendingUp" color="purple" />
            <StatsCard title="Total Value" :value="formatPrice(totalInventoryValue)" icon="DollarSign" color="purple" />
          </div>
        </div>
        </section>

        <!-- Filters Section -->

        <section class="flex-1 px-6 pb-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
             <!-- Search & Date Range -->
            <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">Search Products</label>
                <div class="relative">
                  <SearchIcon class="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <input
                    v-model="searchQuery"
                    type="text"
                    class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                    placeholder="Search by name, category, or description..."
                  />
                </div>
              </div>

              <!-- Category -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  v-model="selectedCategory"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                >
                  <option value="">All Categories</option>
                  <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
                </select>
              </div>

              <!-- Sort -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                <select
                  v-model="sortBy"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                >
                  <option value="name">Name</option>
                  <option value="price">Price</option>
                  <option value="category">Category</option>
                  <option value="stock">Stock</option>
                  <option value="created">Date Added</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        <!-- Products Table -->
        <section class="ml-2 flex-1 px-4 sm:px-6 pb-4 sm:pb-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden">
            <!-- Table Header -->
            <div class="px-4 sm:px-6 py-4 border-b border-gray-200 flex-shrink-0">
              <h3 class="text-base sm:text-lg font-semibold text-gray-900 flex items-center gap-2">
                <InventoryIcon class="w-5 sm:w-6 h-5 sm:h-6 text-gray-700" />
                <span class="text-gray-600 font-normal text-sm sm:text-base"> Products ({{ filteredProducts.length }})</span>
                <span v-if="isLoading" class="text-xs sm:text-sm text-gray-500 ml-auto">Loading...</span>
              </h3>
            </div>


            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Product
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stock
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
                  <tr v-for="product in filteredProducts" :key="product.item_code" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <img
                          :src="currentSrc"
                          :alt="product.name"
                          class="h-10 w-10 rounded-lg object-cover"
                          @error="handleImageError"
                        />
                        <div class="ml-4">
                          <div class="text-sm font-medium text-gray-900">{{ product.item_name }}</div>
                          <div class="text-sm text-gray-500">{{ product.description || 'No description' }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getCategoryClass(product.category)">
                        {{ product.item_group || 'Uncategorized' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ formatPrice(product.rate) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div class="flex items-center">
                        <span :class="getStockClass(product.actual_qty || 0)">
                          {{ product.actual_qty || 0 }} units
                        </span>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getStatusClass(product.actual_qty || 0)">
                        {{ getStatusText(product.actual_qty || 0) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex space-x-2">
                        <button
                          @click="editProduct(product)"
                          class="text-cyan-600 hover:text-cyan-900 transition-colors duration-200"
                          title="Edit"
                        >
                          <EditIcon class="w-4 h-4" />
                        </button>
                        <button
                          @click="duplicateProduct(product)"
                          class="text-green-600 hover:text-green-900 transition-colors duration-200"
                          title="Duplicate"
                        >
                          <CopyIcon class="w-4 h-4" />
                        </button>
                        <button
                          @click="deleteProduct(product)"
                          class="text-red-600 hover:text-red-900 transition-colors duration-200"
                          title="Delete"
                        >
                          <DeleteIcon class="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>

                  <!-- Empty State -->
                  <tr v-if="filteredProducts.length === 0">
                    <td colspan="6" class="px-6 py-12 text-center">
                      <div class="flex flex-col items-center">
                        <PackageIcon class="w-12 h-12 text-gray-400 mb-4" />
                        <h3 class="text-lg font-medium text-gray-900 mb-2">No products found</h3>
                        <p class="text-gray-500 mb-4">
                          {{ searchQuery ? 'Try adjusting your search criteria' : 'Get started by adding your first product' }}
                        </p>
                        <button
                          v-if="!searchQuery"
                          @click="showAddModal = true"
                          class="bg-cyan-500 hover:bg-cyan-600 text-white px-4 py-2 rounded-lg transition-colors duration-200"
                        >
                          Add Your First Product
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>


      <!-- Add/Edit Product Modal -->
      <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">
              {{ showEditModal ? 'Edit Product' : 'Add New Product' }}
            </h3>
          </div>

          <form @submit.prevent="saveProduct" class="px-6 py-4 space-y-4">
            <!-- Product Image -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Product Image</label>
              <input
                v-model="productForm.image"
                type="url"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                placeholder="https://example.com/image.jpg"
              />
            </div>

            <!-- Product Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Product Name *</label>
              <input
                v-model="productForm.name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                placeholder="Enter product name"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea
                v-model="productForm.description"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                rows="3"
                placeholder="Enter product description"
              ></textarea>
            </div>

            <!-- Price and Stock -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Price *</label>
                <input
                  v-model.number="productForm.rate"
                  type="number"
                  min="0"
                  step="100"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                  placeholder="0"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Stock</label>
                <input
                  v-model.number="productForm.stock"
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                  placeholder="0"
                />
              </div>
            </div>

            <!-- Category -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                v-model="productForm.category"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
              >
                <option value="">Select Category</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
                <option value="custom">+ Add New Category</option>
              </select>
            </div>

            <!-- Custom Category Input -->
            <div v-if="productForm.category === 'custom'">
              <label class="block text-sm font-medium text-gray-700 mb-2">New Category Name</label>
              <input
                v-model="newCategory"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                placeholder="Enter new category"
              />
            </div>

            <!-- Modal Actions -->
            <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isSaving"
                class="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors duration-200 disabled:opacity-50"
              >
                {{ isSaving ? 'Saving...' : (showEditModal ? 'Update' : 'Add') }} Product
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import Sidebar from '../layout/Sidebar.vue'
import StatsCard from '../layout/StatsCard.vue'
import { formatPrice } from '../utils/formatters'
import config from '@/config/frappe'
import { useProductsStore } from '@/stores/products'
import DeleteIcon from '@/components/icons/DeleteIcon.svg'
import  PlusIcon from '@/components/icons/PlusIcon.svg'
import InventoryIcon from '@/components/icons/InventoryIcon2.svg'
import  CopyIcon from '@/components/icons/CopyIcon.svg'
import  EditIcon from '@/components/icons/EditIcon.svg'
import { useConfirm } from '@/composables/useConfirm'
import { TrendingUp, Calendar, BarChart3, DollarSign } from 'lucide-vue-next'

const { confirm } = useConfirm()
const productsStore = useProductsStore()

// Reactive state
const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('name')
const showAddModal = ref(false)
const showEditModal = ref(false)
const isSaving = ref(false)
const editingProduct = ref(null)
const newCategory = ref('')


const defaultImage = '/img/default-product.jpg'
const defaultImageSrc = `${config.FRAPPE_URL}${defaultImage}`


const currentSrc = ref(
  product?.image
    ?  `${config.FRAPPE_URL}${product?.image}`
    : defaultImageSrc
)

// Product form
const productForm = reactive({
  name: '',
  description: '',
  price: 0,
  stock: 0,
  category: '',
  image: ''
})

// Computed properties
const categories = computed(() => {
  const cats = new Set()
  productsStore.products.forEach(product => {
    if (product.category) {
      cats.add(product.category)
    }
  })
  return Array.from(cats).sort()
})

const filteredProducts = computed(() => {
  let products = [...productsStore.products]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    products = products.filter(product =>
      product.name.toLowerCase().includes(query) ||
      (product.description || '').toLowerCase().includes(query) ||
      (product.category || '').toLowerCase().includes(query)
    )
  }

  // Category filter
  if (selectedCategory.value) {
    products = products.filter(product => product.category === selectedCategory.value)
  }
  return products
})

const lowStockCount = computed(() => {
  return productsStore.products.filter(product => (product.stock || 0) < 10).length
})

const totalInventoryValue = computed(() => {
  return productsStore.products.reduce((total, product) => {
    return total + (product.rate * (product.stock || 0))
  }, 0)
})

const getCategoryClass = (category) => {
  const classes = {
    'Coffee': 'bg-brown-100 text-brown-800',
    'Tea': 'bg-green-100 text-green-800',
    'Food': 'bg-yellow-100 text-yellow-800',
    'Pastry': 'bg-pink-100 text-pink-800',
    'Cold Drinks': 'bg-blue-100 text-blue-800',
    'Dessert': 'bg-purple-100 text-purple-800'
  }
  return classes[category] || 'bg-gray-100 text-gray-800'
}

const getStockClass = (stock) => {
  if (stock === 0) return 'text-red-600 font-medium'
  if (stock < 10) return 'text-yellow-600 font-medium'
  return 'text-green-600 font-medium'
}
const getStatusClass = (stock) => {
  if (stock === 0) return 'bg-red-100 text-red-800'
  if (stock < 10) return 'bg-yellow-100 text-yellow-800'
  return 'bg-green-100 text-green-800'
}
const getStatusText = (stock) => {
  if (stock === 0) return 'Out of Stock'
  if (stock < 10) return 'Low Stock'
  return 'In Stock'
}
const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/150?text=No+Image'
}
const resetForm = () => {
  productForm.name = ''
  productForm.description = ''
  productForm.rate = 0
  productForm.stock = 0
  productForm.category = ''
  productForm.image = ''
  newCategory.value = ''
  editingProduct.value = null
}
const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  isSaving.value = false
  resetForm()
}
const saveProduct = async () => {
    if (!productForm.name || productForm.rate <= 0) {
        return
        }
    isSaving.value = true
    // Handle new category
    if (productForm.category === 'custom' && newCategory.value.trim()) {
        productForm.category = newCategory.value.trim()
    } else if (productForm.category === 'custom') {
        isSaving.value = false
        return
    }
    try {
        if (showEditModal.value && editingProduct.value) {
            // Update existing product
            await productsStore.updateProduct(editingProduct.value.id, { ...productForm })
        } else {
            // Add new product
            await productsStore.addProduct({ ...productForm })
        }
        closeModal()
    } catch (error) {
        console.error('Error saving product:', error)
        isSaving.value = false
    }
}
const editProduct = (product) => {
    editingProduct.value = product
    productForm.name = product.name
    productForm.description = product.description || ''
    productForm.price = product.rate || 0
    productForm.stock = product.stock || 0
    productForm.category = product.category || ''
    productForm.image = product.image || ''
    newCategory.value = ''
    showEditModal.value = true
}
const duplicateProduct = async (product) => {
    const confirmed = confirm({
        type: 'info',
        title: 'Duplicate Product',
        message: `Are you sure you want to duplicate the product "${product.name}"?`,
        confirmLabel: 'Duplicate',
    })
    if (!confirmed) return
    try {
        const newProduct = { ...product }
        delete newProduct.item_code
        newProduct.name = `${newProduct.name} (Copy)`
        await productsStore.addProduct(newProduct)
    } catch (error) {
        console.error('Error duplicating product:', error)
    }
}
const deleteProduct = async (product) => {
    const confirmed = confirm({
        type: 'delete',
        title: 'Delete Product',
        message: `Are you sure you want to delete the product "${product.name}"? This action cannot be undone.`,
        confirmLabel: 'Delete',
    })
    if (!confirmed) return
    try {
        await productsStore.deleteProduct(product.item_code)
    } catch (error) {
        console.error('Error deleting product:', error)
    }
}
// Fetch products on mount
onMounted(() => {
    // productsStore.loadProductsFromIDB()
    productsStore.loadProductsFromFrappeDB()
})

</script>


