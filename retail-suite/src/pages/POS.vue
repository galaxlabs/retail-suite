<!-- POS.vue -->
<template>
  <div :class="isDark ? 'theme-dark' : 'theme-light'">
    <!-- Shift Control Bar -->
    <ShiftControl
      @shift-opened="handleShiftOpened"
      @shift-closed="handleShiftClosed"
      @shift-error="handleShiftError"
    />

    <div class="hide-print flex flex-row min-h-screen overflow-y-auto antialiased"
        :style="{
        background: isDark ? 'var(--bg)' : 'var(--card-bg)',
        color: 'var(--text-main)'
      }">

      <!-- Left Sidebar -->
      <Sidebar
        :active-menu="activeMenu"
        @menu-change="handleMenuChange"
      />

      <!-- Main Content -->
      <div class="flex-grow grid grid-cols-12 gap-4 px-4 mt-2 items-start">

        <!-- Products Section -->
        <div
          class="col-span-12 xl:col-span-8 flex flex-col min-h-[70vh] py-4 px-4 rounded-xl"
          :style="{
            background: 'var(--content-panel-bg)',
            border: '1px solid var(--content-panel-border)',
            boxShadow: 'var(--content-panel-shadow)'
          }"
        >
          <div class="mb-4 space-y-3">
            <div class="inline-flex rounded-lg p-1" style="background: var(--item-bg); border: 1px solid var(--item-border);">
              <button
                @click="switchSalesChannel('retail')"
                class="px-4 py-2 text-sm font-medium rounded-md transition"
                :style="salesChannel === 'retail' ? `background: ${primaryColor}; color: #fff;` : 'color: var(--text-main);'"
              >
                Retail
              </button>
              <button
                @click="switchSalesChannel('retail')"
                class="px-4 py-2 text-sm font-medium rounded-md transition"
                :style="salesChannel === 'retail' ? `background: ${primaryColor}; color: #fff;` : 'color: var(--text-main);'"
              >
                Retail
              </button>
              <button
                @click="switchSalesChannel('wholesale')"
                class="px-4 py-2 text-sm font-medium rounded-md transition"
                :style="salesChannel === 'wholesale' ? `background: ${primaryColor}; color: #fff;` : 'color: var(--text-main);'"
              >
                Wholesale
              </button>
              <button
                @click="switchSalesChannel('purchase')"
                class="px-4 py-2 text-sm font-medium rounded-md transition"
                :style="salesChannel === 'purchase' ? `background: ${primaryColor}; color: #fff;` : 'color: var(--text-main);'"
              >
                Purchase
              </button>
            </div>
            <button @click="handleSignOut" class="px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1 transition hover:opacity-80"
              :style="{ background: 'var(--warning-bg)', color: 'var(--warning-border)', border: '1px solid var(--warning-border)' }">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
              Sign Out
            </button>
          </div>
          <input
              v-model="searchKeyword"
              @keydown.enter.prevent="handleScannerEnter"
              type="text"
              class="w-full h-12 rounded-xl px-4 text-base"
              style="background: var(--input-bg); color: var(--input-text); border: 1px solid var(--input-border);"
              placeholder="Search item by name, code, or category"
            />
          </div>

          <div class="flex-1 overflow-y-auto">
            <ProductGrid :search-keyword="searchKeyword" :simple-mode="true" />
          </div>
        </div>

        <!-- Cart Section -->
        <div
          class="col-span-12 xl:col-span-4 flex flex-col py-4 px-3 rounded-xl self-start"
          :style="{
            background: 'var(--sidebar-panel-bg)',
            border: '1px solid var(--sidebar-panel-border)',
            boxShadow: 'var(--sidebar-panel-shadow)'
          }"
        >
          <Cart
            :mode="activeMenu === 'return' ? 'return' : 'sale'"
            :selected-invoice="selectedInvoice"
            :sales-channel="salesChannel"
            :purchase-mode="salesChannel === 'purchase'"
            :customer-required="salesChannel === 'wholesale'"
            @submit="handleCartSubmit"
            @clear-invoice="handleClearInvoice"
          />
        </div>

      </div>


      <!-- First Time Modal -->
      <FirstTimeModal
        v-if="showFirstTimeModal"
        @start-blank="startBlank"
      />

      <!-- Receipt Modal -->
      <ReceiptModal
        v-if="showReceiptModal"
        :receipt-data="receiptData"
        :store-name="settingsStore.settings?.store?.name || shiftStore.pos_profile?.company || 'Store'"
        :store-address="settingsStore.settings?.store?.address || shiftStore.pos_profile?.warehouse || ''"
        :store-logo="settingsStore.settings?.store?.logoUrl || shiftStore.pos_profile?.company_logo || ''"
        @close="closeReceiptModal"
        @proceed="handleReceiptPrinted"
        @save="handleReceiptSaved"
      />

      <!-- Return Invoice Component -->
      <ReturnInvoiceBox
        v-if="showReturnInvoiceBox"
        @select="handleInvoiceSelected"
        @cancel="handleReturnCancel"
      />
    </div>

    <!-- No Shift Warning Overlay -->
    <div
      v-if="!isShiftOpen && !showFirstTimeModal && !isCheckingShift"
      class="fixed inset-0 flex items-center justify-center z-40"
      :style="{ background: 'rgba(0,0,0,0.5)' }"
    >
      <div
        class="rounded-lg shadow-xl max-w-md w-full mx-4 p-6 text-center"
        :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
      >
        <div class="text-center mb-4">

          <!-- Warning Icon Circle -->
          <div
            class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
            :style="{ background: 'var(--warning-bg)', border: '1px solid var(--warning-border)' }"
          >
            <WarningIcon
              class="w-8 h-8"
              :style="{ color: 'var(--warning-border)' }"
            />
          </div>

          <p
            class="w-full flex justify-center"
            :style="{ color: 'var(--text-muted)' }"
          >
            <span class="text-center">
              Please open a shift before starting sales transactions.
            </span>
          </p>
        </div>

        <!-- Open Shift Button -->
        <div class="flex justify-center space-x-4 mt-6">
          <div class="flex items-center justify-center">
            <button
              v-if="!shiftStore.isShiftOpen"
              @click="showOpenShiftModal = true"
              :style="{ color: hover ? primaryColor : 'var(--text-muted)' }"
              @mouseover="hover = true"
              @mouseleave="hover = false"
              class="w-8 h-8 flex items-center justify-center cursor-pointer transition-all duration-200 hover:scale-110"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                <path d="M18.36 6.64a9 9 0 1 1-12.73 0" />
                <line x1="12" y1="2" x2="12" y2="12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Open Shift Modal -->
    <OpenShiftModal
      v-if="showOpenShiftModal"
      @close="showOpenShiftModal = false"
      @success="handleShiftOpened"
      @error="handleShiftError"
    />
  </div>

  <!-- Print Area -->
  <div id="print-area" class="print-area"></div>
</template>

<script setup>
import { ref, onMounted, watch, watchEffect, reactive, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { createPurchaseReceipt } from '@/services/api'
import { storeToRefs } from 'pinia'
import ShiftControl from '@/components/shift/ShiftControl.vue'
import Sidebar from '@/layout/Sidebar.vue'
import ProductGrid from '@/components/products/ProductGrid.vue'
import Cart from '@/components/cart/Cart.vue'
import FirstTimeModal from '@/components/modals/FirstTimeModal.vue'
import ReceiptModal from '@/components/modals/ReceiptModal.vue'
import ReturnInvoice from '@/components/modals/ReturnInvoice.vue'
import { useSettingsStore } from '../stores/settings'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import { useShiftStore } from '../stores/shift'
import OpenShiftModal from '@/components/modals/OpenShiftModal.vue'
import { useInvoicesStore } from '@/stores/invoices'
import ReturnInvoiceBox from '@/components/modals/ReturnInvoiceBox.vue'
import { formatPrice } from '../utils/formatters'
import { printReceipt } from '@/services/printer'
import { getCompanyBranding } from '@/services/api'
import WarningIcon from '@/components/icons/WarningIcon.svg'

const hover = ref(false)
const activeMenu = ref('pos')
const searchKeyword = ref('')
const showFirstTimeModal = ref(false)
const showReceiptModal = ref(false)
const showOpenShiftModal = ref(false)
const receiptData = ref(null)
const selectedInvoice = ref(null)
const user = ref(null)
const productsStore = useProductsStore()
const cartStore = useCartStore()
const shiftStore = useShiftStore()
const { isShiftOpen } = storeToRefs(shiftStore)
const isCheckingShift = ref(true)
const invoicesStore = useInvoicesStore()
const returnInvoice = ref(null)
const mode = ref('sale')
const showReturnInvoiceBox = ref(false)
const SALES_CHANNEL_KEY = "retail_sales_channel_mode"
const salesChannel = ref(localStorage.getItem(SALES_CHANNEL_KEY) || "retail")

const normalizeBarcode = (value) => String(value || "").trim().toLowerCase()

const extractBarcodes = (product) => {
  const direct = [product.barcode, product.item_code]
  const fromItemBarcode = Array.isArray(product.item_barcode)
    ? product.item_barcode.map((b) => b?.barcode)
    : []
  const fromBarcodes = Array.isArray(product.barcodes)
    ? product.barcodes.map((b) => b?.barcode)
    : []

  return [...direct, ...fromItemBarcode, ...fromBarcodes]
    .map((code) => normalizeBarcode(code))
    .filter(Boolean)
}

const handleScannerEnter = async () => {
  const query = normalizeBarcode(searchKeyword.value)
  if (!query) return

  const items = productsStore.products || []
  const exact = items.find((product) => extractBarcodes(product).includes(query))

  if (exact) {
    cartStore.addToCart(exact)
    searchKeyword.value = ""
    window.$toast?.success(`Added ${exact.item_name}`)
    return
  }

  if (query.length >= 2) {
    await loadProductsWithRetry()
    const refreshed = (productsStore.products || []).find((product) => extractBarcodes(product).includes(query))
    if (refreshed) {
      cartStore.addToCart(refreshed)
      searchKeyword.value = ""
      window.$toast?.success(`Added ${refreshed.item_name}`)
    } else {
      window.$toast?.warning("No product found for this barcode")
    }
  }
}


const RETAIL_PRICE_LIST_NAME = "Retail Selling"
const WHOLESALE_PRICE_LIST_NAME = "Wholesale Selling"

const resolvePriceListForChannel = (channel) => {
  const available = (productsStore.priceLists || []).map((p) =>
    typeof p === "string" ? p : (p.name || p.price_list_name || "")
  ).filter(Boolean)

  const fallback = shiftStore.pos_profile?.selling_price_list || productsStore.selectedPriceList || "Standard Selling"
  if (!available.length) {
    return fallback
  }

  if (channel === "wholesale") {
    return available.includes(WHOLESALE_PRICE_LIST_NAME)
      ? WHOLESALE_PRICE_LIST_NAME
      : fallback
  }

  return available.includes(RETAIL_PRICE_LIST_NAME)
    ? RETAIL_PRICE_LIST_NAME
    : fallback
}

const applySalesChannel = async (channel) => {
  salesChannel.value = channel
  localStorage.setItem(SALES_CHANNEL_KEY, channel)

  if (!productsStore.priceLists?.length) {
    await productsStore.loadFilterOptions()
  }

  const nextPriceList = resolvePriceListForChannel(channel)
  productsStore.selectedPriceList = nextPriceList

  if (channel === "wholesale") {
    shiftStore.setCustomer(null)
  } else {
    const defaultCustomer = shiftStore.pos_profile?.customer
    if (defaultCustomer) {
      shiftStore.setCustomer({ name: defaultCustomer })
    }
  }
  await loadProductsWithRetry()
}

const handleSignOut = async () => {
    const { session } = await import('@/services/auth')
    session.logout.submit()
  }

const switchSalesChannel = async (channel) => {
  if (salesChannel.value === channel) return
  await applySalesChannel(channel)
}

const loadProductsWithRetry = async () => {
  await productsStore.loadProductsFromFrappeDB()
  if (!(productsStore.products || []).length) {
    await new Promise((resolve) => setTimeout(resolve, 700))
    await productsStore.loadProductsFromFrappeDB()
  }
}

const settingsStore = useSettingsStore()
// Dark Mode from Settings Store
const isDark = computed(() => settingsStore.settings.appearance.theme === 'dark')

    // Handle menu change
    const handleMenuChange = (menu) => {
      if (menu === 'return') {
        mode.value = 'return'
        activeMenu.value = menu
        showReturnInvoiceBox.value = true
        cartStore.isReturn = 1
      } else if (menu === 'pos') {
        mode.value = 'sale'
        activeMenu.value = menu
        selectedInvoice.value = null
        cartStore.clearCart()
        cartStore.isReturn = 0
      }
    }

    const handleReturnCancel = () => {
          showReturnInvoiceBox.value = false
    }

    const handleClearInvoice = () => {
      selectedInvoice.value = null
      showReturnInvoiceBox.value = true
    }


    // Handle invoice selected (from Cart component)
      const handleInvoiceSelected = (invoice) => {
        cartStore.clearCart() // تبدأ سلة جديدة

        showReturnInvoiceBox.value = false

        // Auto-select customer from the returned invoice
        if (invoice.customer) {
          shiftStore.setCustomer({ name: invoice.customer, customer_name: invoice.customer_name || invoice.customer })
        }

      if (invoice.returnable_items && invoice.returnable_items.length) {

        const returnedItems = invoice.returnable_items.map(item => ({
          item_code: item.item_code,
          item_name: item.item_name,
          qty: Math.abs(item.returnable_qty), // الكمية سالبة للواپسی
          rate: item.rate,
          amount: item.amount,
          originalQuantity: item.returnable_qty, // للتحقق من الحد الأقصى
          is_return: true
        }))
        // push returnItems to  cart [] in Cart.js
        cartStore.loadReturnItems(returnedItems)

        // نخلي selectedInvoice.value تحتوي على بيانات أساسية + عناصر للواپسی فقط
        selectedInvoice.value = {
          name: invoice.name,
          customer: invoice.customer,
          grand_total: invoice.grand_total,
          total_returnable_qty: invoice.total_returnable_qty,
          items: returnedItems // العناصر اللي هترجع
        }

      }
    }

    const handleCartSubmit = async (transactionData) => {
        try {

          // تحقق من نوع المعاملة
          const isReturn = transactionData.mode === 'return'
          const isPurchase = salesChannel.value === 'purchase'

          if (isPurchase) {
            await handlePurchaseTransaction(transactionData)
          } else if (isReturn) {
            await handleReturnTransaction(transactionData)
          } else {
            await handleSaleTransaction(transactionData)
          }

        } catch (error) {
          console.error('❌ Error in handleCartSubmit:', error)
          if (window.$toast) {
            window.$toast.error(error.message || 'Failed to process transaction')
          }
        }
    }


    const handleSaleTransaction = async (transactionData) => {
      try {
        const isFastMode = shiftStore.pos_profile?.fast_mode

        if (isFastMode) {
          // Fast Mode: submit مباشرة
          const invoiceResponse = await invoicesStore.addTransaction(transactionData)

          receiptData.value = {
            ...transactionData,
            storeName: settingsStore.settings?.store?.name || shiftStore.pos_profile?.company || shiftStore.pos_profile?.company || "POS Store",
            storeAddress: settingsStore.settings?.store?.address || shiftStore.pos_profile?.warehouse || "",
            storeLogo: settingsStore.settings?.store?.logoUrl || "",
            footerMessage: settingsStore.settings?.receipt?.footerMessage || "",
            invoiceNo: invoiceResponse.invoiceNo,
            invoiceId: invoiceResponse.invoiceNo,
            isFastMode: true,
            isSaved: Boolean(invoiceResponse.status),
          }
        } else {
          // Normal Mode: save draft فقط
          const invoiceResponse = await invoicesStore.saveInvoice(transactionData)

          receiptData.value = {
            ...transactionData,
            storeName: settingsStore.settings?.store?.name || shiftStore.pos_profile?.company || shiftStore.pos_profile?.company || "POS Store",
            storeAddress: settingsStore.settings?.store?.address || shiftStore.pos_profile?.warehouse || "",
            storeLogo: settingsStore.settings?.store?.logoUrl || "",
            footerMessage: settingsStore.settings?.receipt?.footerMessage || "",
            invoiceNo: invoiceResponse.name || transactionData.invoiceNo,
            invoiceId: invoiceResponse.name || transactionData.invoiceNo,
            isFastMode: false,
            isSaved: true,
          }
        }

        showReceiptModal.value = true

        const printerSettings = settingsStore.settings?.printer || {}
        const shouldAutoPrint = printerSettings.autoPrint ?? printerSettings.autoprint ?? true
        if (shouldAutoPrint) {
          try {
            await printReceipt(receiptData.value)
            if (window.$toast) {
              window.$toast.success(`Receipt sent to ${printerSettings.name || printerSettings.host || 'printer'}`)
            }
          } catch (printError) {
            console.error('❌ Auto print failed:', printError)
            if (window.$toast) {
              window.$toast.warning(printError.message || 'Invoice saved, but auto print failed')
            }
          }
        }

      } catch (error) {
        console.error('❌ Error in handleSaleTransaction:', error)
        if (window.$toast) window.$toast.error(error.message || 'Failed to process transaction')
      }
    }

    const handleReturnTransaction = async (returnData) => {
      try {

        // معالجة خاصة للواپسیات
        const returnTransaction = {
          ...returnData,
          type: 'return',
          total: -Math.abs(returnData.summary?.total || 0),
          originalInvoice: selectedInvoice.value,
          returnedAt: new Date().toISOString()
        }

        // هنا ممكن تستدعي دالة خاصة للواپسیات
        // مثلاً: await invoicesStore.processReturn(returnTransaction)


        if (window.$toast) {
          window.$toast.success(
            `Return processed! Refund: ${formatPrice(Math.abs(returnData.summary?.total || 0))}`
          )
        }

        // نظّف الـ state
        cartStore.clearCart()
        selectedInvoice.value = null
        activeMenu.value = 'pos'

      } catch (error) {
        console.error('❌ Error in handleReturnTransaction:', error)
        throw error
      }
    }

    // Save Copy
    const handleReceiptSaved = async () => {
      if (window.$toast) {
        window.$toast.success('Receipt copy downloaded')
      }
    }
    // Proceed = keep as draft only
    const handleReceiptPrinted = async (receiptDataParam) => {
      try {
        if (window && window["$toast"]) {
          const name = receiptDataParam?.invoiceNo || "---"
          window["$toast"].success("انوائس " + name + " ڈرافٹ میں محفوظ ہو گئی")
        }
      } finally {
        cartStore.clearCart()
        selectedInvoice.value = null
        showReceiptModal.value = false
        activeMenu.value = "pos"
      }
    }

    // Handle return processed
    const handleReturnProcessed = async (returnData) => {
    try {

      // Add return transaction to shift
      const returnTransaction = {
        ...returnData,
        type: 'return',
        total: -Math.abs(returnData.total), // Negative amount for return
        originalInvoice: selectedInvoice.value
      }

      await invoicesStore.addTransaction(returnTransaction)

      // Save return invoice
      const returnInvoiceData = {
        ...returnData,
        receiptNo: generateReceiptNo('RT'), // RT prefix for returns
        receiptDate: new Date().toISOString(),
        transactionType: 'return',
        originalInvoiceNo: selectedInvoice.value?.receiptNo,
        shiftInfo: {
          cashier: shiftStore.currentShift?.userName,
          shiftId: shiftStore.currentShift?.id
        }
      }

      await invoicesStore.saveInvoice(returnInvoiceData)

      // Show success message
      if (window.$toast) {
        window.$toast.success(`Return processed successfully! Refund: ${formatPrice(Math.abs(returnData.total))}`)
      }

      // Clear cart and selected invoice
      cartStore.clearCart()
      selectedInvoice.value = null

      // Show receipt modal for return
      receiptData.value = returnInvoiceData
      showReceiptModal.value = true

    } catch (error) {
      console.error('Error processing return:', error)
      if (window.$toast) {
        window.$toast.error('Failed to process return')
      }
    }
    }

    // Handle return cancelled
    const handleReturnCancelled = () => {
      cartStore.clearCart()
      selectedInvoice.value = null

      if (window.$toast) {
        window.$toast.info('Return process cancelled')
      }
    }

    // Handle shift events
    const handleShiftOpened = async (shift) => {
      showOpenShiftModal.value = false
      await shiftStore.checkActiveShift()
      await loadProductsWithRetry()
    }

    const handleShiftClosed = async (shift) => {

      showOpenShiftModal.value = true
      // Clear current cart when shift closes
      cartStore.clearCart()
      selectedInvoice.value = null
    }

    const handleShiftError = (error) => {
      console.error('Shift error:', error)
    }

    // Load sample data
    const loadProductsData = async () => {
      await loadProductsWithRetry()
      showFirstTimeModal.value = false
    }

    // Start with blank data
    const startBlank = () => {
      showFirstTimeModal.value = false
    }

    // Close receipt modal
    const closeReceiptModal = () => {
      showReceiptModal.value = false
    }

    // Proceed after print - SAVE INVOICE HERE
    const proceedAfterPrint = async (receiptDataParam) => {

      try {
        // Save invoice to database
        const savedInvoice = await invoicesStore.saveInvoice(receiptDataParam)


        if (savedInvoice) {
          // ✅ استخدم البيانات الصحيحة
          if (window.$toast) {
            const displayName = receiptDataParam.invoiceNo || savedInvoice.receiptNo || savedInvoice.id
            window.$toast.success(`Invoice ${displayName} saved successfully!`)
          }

          // Clear cart and close modal
          cartStore.clearCart()
          selectedInvoice.value = null
          showReceiptModal.value = false
          activeMenu.value = 'pos'
        }

      } catch (error) {
        console.error('❌ Failed to save invoice:', error)

        // Show error message but still clear cart
        if (window.$toast) {
          window.$toast.error('Failed to save invoice, but transaction was completed')
        }

        cartStore.clearCart()
        selectedInvoice.value = null
        showReceiptModal.value = false
        activeMenu.value = 'pos'
      }
    }

    // Generate receipt number
    const generateReceiptNo = (prefix = 'TW') => {
      const now = new Date()
      const timestamp = now.getTime().toString().slice(-6)
      return `${prefix}${timestamp}`
    }

    // ✅ استخدم watchEffect - أقوى من watch
    watchEffect(() => {
      const color = settingsStore.settings.appearance.primaryColor
      // الـ component بتتحدث تلقائياً
    })

    // Initialize on mount
    onMounted(async () => {
        const currentUserInfo = await shiftStore.getCurrentUserInfo()
        const currentUser = currentUserInfo?.user || null
        user.value = currentUser
        settingsStore.loadSettings()
        await shiftStore.loadShifts()
        await shiftStore.checkActiveShift()
        settingsStore.syncStoreIdentityFromCompany({}, shiftStore.pos_profile || {})
        const companyName = shiftStore.pos_profile?.company
        if (companyName) {
          const branding = await getCompanyBranding(companyName)
          settingsStore.syncStoreIdentityFromCompany(branding, shiftStore.pos_profile || {})
        }
        await productsStore.loadFilterOptions()
        await applySalesChannel(salesChannel.value)
        isCheckingShift.value = false

        // Keyboard shortcuts
        document.addEventListener('keydown', handleKeyboardShortcuts)
    })

    const handleKeyboardShortcuts = (e) => {
      // Ctrl+F or / → focus search
      if ((e.ctrlKey && e.key === 'f') || (e.key === '/' && !e.ctrlKey && e.target.tagName !== 'INPUT')) {
        e.preventDefault()
        const searchInput = document.querySelector('input[placeholder*="Search"]')
        if (searchInput) searchInput.focus()
        return
      }
      // Escape → clear search
      if (e.key === 'Escape') {
        searchKeyword.value = ''
        return
      }
      // F8 → toggle Retail/Wholesale/Purchase
      if (e.key === 'F8' && !e.ctrlKey) {
        e.preventDefault()
        const channels = ['retail', 'wholesale', 'purchase']
        const current = channels.indexOf(salesChannel.value)
        const next = channels[(current + 1) % channels.length]
        switchSalesChannel(next)
      }
      // F5 → Refresh products
      if (e.key === 'F5' && !e.ctrlKey) {
        e.preventDefault()
        loadProductsWithRetry()
      }
    }



        // ✅ Watch لمراقبة جميع تغييرات الإعدادات
    watch(
      () => settingsStore.settings,
      (newSettings) => {
        settingsStore.saveSettings()
      },
      { deep: true }
    )

    // ✅ Watch خاص باللون الأساسي
    watch(
      () => settingsStore.settings.appearance.primaryColor,
      (newColor) => {
        // الـ Sidebar بتتحدث تلقائياً
      }
    )
    watch(showReturnInvoiceBox, (v) => {
    })

    watch(isShiftOpen, (val) => {
    })
    const settings = computed(() => settingsStore.settings)
    const primaryColor = computed(() => {
      return settings.value?.appearance?.primaryColor || '#06b6d4'
    })

</script>
