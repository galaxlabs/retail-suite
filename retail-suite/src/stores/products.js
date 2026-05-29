import { defineStore } from 'pinia'
import { toRaw } from 'vue'
import { getPriceLists, getWarehouses, createSampleItems, deleteSampleItems } from '../services/api'
import { useShiftStore } from './shift'
import { getItemsFromFrappeDB} from '@/composables/pos'
export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [],
    isLoading: false,
    searchKeyword: '',

    // Filters
    selectedPriceList: '',
    selectedWarehouse: '',

    // Options lists
    priceLists: [],
    warehouses: [],

    db: null,
    error: null
  }),

  getters: {
    filteredProducts: (state) => {
      if (!state.searchKeyword) {
        return state.products
      }

      const keyword = state.searchKeyword.toLowerCase().trim()
      return state.products.filter(product =>
        (product.item_name || product.name || '').toLowerCase().includes(keyword) ||
        (product.item_code || '').toLowerCase().includes(keyword) ||
        (product.item_group || product.category || '').toLowerCase().includes(keyword) ||
        (product.description || '').toLowerCase().includes(keyword)
      )
    },

    productsCount: (state) => state.products.length,

    filteredProductsCount: (state) => {
      if (!state.searchKeyword) {
        return state.products.length
      }

      const keyword = state.searchKeyword.toLowerCase().trim()
      return state.products.filter(product =>
        (product.item_name || product.name || '').toLowerCase().includes(keyword) ||
        (product.item_code || '').toLowerCase().includes(keyword) ||
        (product.item_group || product.category || '').toLowerCase().includes(keyword) ||
        (product.description || '').toLowerCase().includes(keyword)
      ).length
    },

    categorizedProducts: (state) => {
      const categories = {}
      state.products.forEach(product => {
        const category = product.item_group || 'Other'
        if (!categories[category]) {
          categories[category] = []
        }
        categories[category].push(product)
      })
      return categories
    }
  },

  actions: {
        // ─── Load pricelist + warehouse options ───────────────────────────
    async loadFilterOptions() {
      try {
        const [pl, wh] = await Promise.all([getPriceLists(), getWarehouses()])
                // console.log('➡️ POS Profile :', posProfileName)
        console.log('➡️ **Price List**  :', pl)
        console.log('➡️ **warehouses**    :', wh)
        this.priceLists = pl || []
        this.warehouses = wh || []
      } catch (e) {
        console.error('❌ loadFilterOptions:', e)
      }
    },

    // ─── Main load ────────────────────────────────────────────────────
    async loadProductsFromFrappeDB() {
      try {
        console.log('========== Load Products ==========')
        const shiftStore = useShiftStore()
        const hasLocalShift = Boolean(shiftStore.pos_profile && shiftStore.pos_opening_shift)
        const hasActiveShift = hasLocalShift ? true : await shiftStore.checkActiveShift()

        if (!hasActiveShift) {
          console.warn('⚠️ No active shift / POS Profile')
          return []
        }

        const currentPOSProfile = shiftStore.pos_profile || {}
        const posProfileName    = currentPOSProfile.name
        const currentPriceList  =
          this.selectedPriceList ||
          currentPOSProfile.selling_price_list ||
          "Standard Selling"
        const currentCustomer = currentPOSProfile.customer || ''
        const selectedWarehouse = this.selectedWarehouse || null  // null → backend uses pos_profile default

        console.log('➡️ POS Profile :', posProfileName)
        console.log('➡️ Price List  :', currentPriceList)
        console.log('➡️ Customer    :', currentCustomer)
        console.log('➡️ Warehouse   :', selectedWarehouse)

        if (!posProfileName || !currentPriceList) {
          console.warn('⚠️ Missing required profile details!')
          return []
        }

        this.isLoading = true
        const products = await getItemsFromFrappeDB(
          currentPOSProfile,
          currentPriceList,
          currentCustomer,
          this.searchKeyword,
          selectedWarehouse
        )

        console.log("AFTER API CALL", products)
        console.log('✅ Products loaded:', products?.length)
        this.products = products || []

        // حفظ الـ defaults أول مرة
        if (!this.selectedPriceList) this.selectedPriceList = currentPriceList

        return this.products
      } catch (error) {
        console.error('❌ Error loading products:', error)
        return []
      } finally {
        this.isLoading = false
      }
    },

    // ─── Set search keyword ────────────────────────────────────────────
    setSearchKeyword(kw) {
      this.searchKeyword = kw
    },

    // ─── Change pricelist → reload ────────────────────────────────────
    async changePriceList(priceList) {
      this.selectedPriceList = priceList
      await this.loadProductsFromFrappeDB()
    },

    // ─── Change warehouse → reload ────────────────────────────────────
    async changeWarehouse(warehouse) {
      this.selectedWarehouse = warehouse
      await this.loadProductsFromFrappeDB()
    },
    async createSampleData() {
      const sample_products = [
        {
          item_code: "SAMPLE-ITEM-001",
          item_name: "Beef Burger",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/beef-burger.png"
        },
        {
          item_code: "SAMPLE-ITEM-002",
          item_name: "Sandwich",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/sandwich.png"
        },
        {
          item_code: "SAMPLE-ITEM-003",
          item_name: "Shawarma",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/sawarma.png"
        },
        {
          item_code: "SAMPLE-ITEM-004",
          item_name: "Croissant",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/croissant.png"
        },
        {
          item_code: "SAMPLE-ITEM-005",
          item_name: "Cinnamon Roll",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/cinnamon-roll.png"
        },
        {
          item_code: "SAMPLE-ITEM-006",
          item_name: "Choco Donut Peanut",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/choco-glaze-donut-peanut.png"
        },
        {
          item_code: "SAMPLE-ITEM-007",
          item_name: "Choco Glazed",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/choco-glaze-donut.png"
        },
        {
          item_code: "SAMPLE-ITEM-008",
          item_name: "Red Glazed",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/red-glaze-donut.png"
        },
        {
          item_code: "SAMPLE-ITEM-009",
          item_name: "Iced Coffee",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/coffee-latte.png"
        },
        {
          item_code: "SAMPLE-ITEM-010",
          item_name: "Iced Chocolate",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/ice-chocolate.png"
        },
        {
          item_code: "SAMPLE-ITEM-011",
          item_name: "Iced Tea",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/ice-tea.png"
        },
        {
          item_code: "SAMPLE-ITEM-012",
          item_name: "Iced Latte",
          item_group: "POS ITEM",
          stock_uom: "Unit",
          standard_rate: 100,
          image: "/files/matcha-latte.png"
        }
      ]
      try {
        const Response = await createSampleItems(sample_products)
        console.log("response createSampleItems", Response)
        window.$toast.success("✅ Sample items created successfully")
      } catch (error) {
        console.error("error", error)
        window.$toast.error("❌ Failed to create sample items")
      }
    },

    async deleteSampleData() {
      try {
        const response = await deleteSampleItems()
        window.$toast.success("Delete sample items Successfully")
        console.log("response deleteSampleItems", response)
      } catch (error) {
        window.$toast.error("❌ Failed to Delete sample items")
        console.error("error deleting sample data", error)
      }
    },

    // Add new product
    async addProduct(product) {
      try {
        const newProduct = {
          ...product,
          id: Date.now(), // Simple ID generation
          createdAt: new Date().toISOString()
        }

        this.products.push(newProduct)
        await this.saveProductsToDB()

        return newProduct
      } catch (error) {
        console.error('Failed to add product:', error)
        this.error = 'Failed to add product'
        throw error
      }
    },

    // Update product
    async updateProduct(id, updates) {
      try {
        const index = this.products.findIndex(p => p.id === id)
        if (index !== -1) {
          this.products[index] = {
            ...this.products[index],
            ...updates,
            updatedAt: new Date().toISOString()
          }

          await this.saveProductsToDB()
          return this.products[index]
        }
        throw new Error('Product not found')
      } catch (error) {
        console.error('Failed to update product:', error)
        this.error = 'Failed to update product'
        throw error
      }
    },

    // Delete product
    async deleteProduct(id) {
      try {
        const index = this.products.findIndex(p => p.id === id)
        if (index !== -1) {
          this.products.splice(index, 1)
          await this.saveProductsToDB()
          return true
        }
        throw new Error('Product not found')
      } catch (error) {
        console.error('Failed to delete product:', error)
        this.error = 'Failed to delete product'
        throw error
      }
    },

    // Search products
    setSearchKeyword(keyword) {
      this.searchKeyword = keyword
    },

    // Clear search
    clearSearch() {
      this.searchKeyword = ''
    },

    // Get product by ID
    getProductById(id) {
      return this.products.find(p => p.id === id)
    },

    // Get products by category
    getProductsByCategory(category) {
      return this.products.filter(p => p.category === category)
    },

    // Clear all products
    async clearAllProducts() {
      try {
        this.products = []
        await this.saveProductsToDB()
      } catch (error) {
        console.error('Failed to clear products:', error)
        this.error = 'Failed to clear products'
        throw error
      }
    },

    // Clear error
    clearError() {
      this.error = null
    }
  }
})
