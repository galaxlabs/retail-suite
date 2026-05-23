<!-- POS.vue -->
<template>
  <div :class="isDark ? 'theme-dark' : 'theme-light'">
    <!-- Shift Control Bar -->
    <ShiftControl
      @shift-opened="handleShiftOpened"
      @shift-closed="handleShiftClosed"
      @shift-error="handleShiftError"
    />

    <div class="hide-print flex flex-row h-screen antialiased"
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
      <div class="flex-grow flex gap-4 px-4 mt-2">

        <!-- Products Section -->
        <div
          class="w-8/12 flex flex-col h-full py-4 px-4 rounded-xl"
          :style="{
            background: 'var(--content-panel-bg)',
            border: '1px solid var(--content-panel-border)',
            boxShadow: 'var(--content-panel-shadow)'
          }"
        >
          <div class="mb-4">
            <SearchBar v-model="searchKeyword" />
          </div>

          <div class="flex-1 overflow-y-auto">
            <ProductGrid :search-keyword="searchKeyword" />
          </div>
        </div>

        <!-- Cart Section -->
        <div
          class="w-4/12 flex flex-col h-full py-4 px-3 rounded-xl"
          :style="{
            background: 'var(--sidebar-panel-bg)',
            border: '1px solid var(--sidebar-panel-border)',
            boxShadow: 'var(--sidebar-panel-shadow)'
          }"
        >
          <Cart
            :mode="activeMenu === 'return' ? 'return' : 'sale'"
            :selected-invoice="selectedInvoice"
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
import { storeToRefs } from 'pinia'
import ShiftControl from '@/components/shift/ShiftControl.vue'
import Sidebar from '@/layout/Sidebar.vue'
import SearchBar from '@/layout/SearchBar.vue'
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
        console.log('Invoice selected:', invoice)

      if (invoice.returnable_items && invoice.returnable_items.length) {

        const returnedItems = invoice.returnable_items.map(item => ({
          item_code: item.item_code,
          item_name: item.item_name,
          qty: Math.abs(item.returnable_qty), // الكمية سالبة للمرتجع
          rate: item.rate,
          amount: item.amount,
          originalQuantity: item.returnable_qty, // للتحقق من الحد الأقصى
          is_return: true
        }))
        // push returnItems to  cart [] in Cart.js
        cartStore.loadReturnItems(returnedItems)

        // نخلي selectedInvoice.value تحتوي على بيانات أساسية + عناصر للمرتجع فقط
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
          console.log('=== handleCartSubmit Called ===')
          console.log('Transaction Data from Cart:', transactionData)
          console.log('Mode:', transactionData.mode)

          // تحقق من نوع المعاملة
          const isReturn = transactionData.mode === 'return'

          if (isReturn) {
            console.log('🔄 Processing RETURN transaction...')
            await handleReturnTransaction(transactionData)
          } else {
            console.log('💰 Processing SALE transaction...')
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
        console.log('🔄 handleReturnTransaction: Starting...')
        console.log('Return data:', returnData)

        // معالجة خاصة للمرتجعات
        const returnTransaction = {
          ...returnData,
          type: 'return',
          total: -Math.abs(returnData.summary?.total || 0),
          originalInvoice: selectedInvoice.value,
          returnedAt: new Date().toISOString()
        }

        // هنا ممكن تستدعي دالة خاصة للمرتجعات
        // مثلاً: await invoicesStore.processReturn(returnTransaction)

        console.log('✅ Return processed successfully')

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
    // Proceed = Submit
    const handleReceiptPrinted = async (receiptDataParam) => {
          console.log('🔍 invoiceId:', receiptDataParam.invoiceId)
          console.log('🔍 isFastMode:', receiptDataParam.isFastMode)

      try {
        if (receiptDataParam.isFastMode) {
          // Fast Mode: الفاتورة اتسبمتت خلاص - مفيش حاجة
          if (window.$toast) window.$toast.success(`Invoice ${receiptDataParam.invoiceNo} completed!`)
        } else {
          // Normal Mode: submit دلوقتي
          await invoicesStore.proceedInvoice(receiptDataParam)
          if (window.$toast) window.$toast.success(`Invoice ${receiptDataParam.invoiceNo} submitted!`)
        }
      } catch (error) {
        if (window.$toast) window.$toast.error(error.message || 'Failed to submit invoice')
      } finally {
        cartStore.clearCart()
        selectedInvoice.value = null
        showReceiptModal.value = false
        activeMenu.value = 'pos'
      }
    }

    // Handle return processed
    const handleReturnProcessed = async (returnData) => {
    try {
      console.log('Processing return:', returnData)

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
      console.log('Return cancelled')
      cartStore.clearCart()
      selectedInvoice.value = null

      if (window.$toast) {
        window.$toast.info('Return process cancelled')
      }
    }

    // Handle shift events
    const handleShiftOpened = async (shift) => {
      // await shiftStore.checkActiveShift()
      showOpenShiftModal.value = false
    }

    const handleShiftClosed = async (shift) => {
      console.log('Shift closed:', shift)
      console.log('Open Closing Shift modal')
      console.log('shift user', shift.user)

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
      await productsStore.loadProductsFromFrappeDB()
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
      console.log('=== proceedAfterPrint Called ===')
      console.log('Receipt data:', receiptDataParam)

      try {
        // Save invoice to database
        const savedInvoice = await invoicesStore.saveInvoice(receiptDataParam)

        console.log('✅ Invoice saved successfully:', savedInvoice)

        if (savedInvoice) {
          console.log("✅ Saved invoice details:", {
            id: savedInvoice.id,
            receiptNo: savedInvoice.receiptNo,
            invoiceNo: receiptDataParam.invoiceNo
          })

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
      console.log('🎨 POS: Primary color is now:', color)
      // الـ component بتتحدث تلقائياً
    })

    // Initialize on mount
    onMounted(async () => {
        const currentUserInfo = await shiftStore.getCurrentUserInfo()
        const currentUser = currentUserInfo.user
        user.value = currentUser
        await shiftStore.loadShifts()
        await shiftStore.checkActiveShift()
        await loadProductsData()
        isCheckingShift.value = false
        settingsStore.loadSettings()
    })



        // ✅ Watch لمراقبة جميع تغييرات الإعدادات
    watch(
      () => settingsStore.settings,
      (newSettings) => {
        console.log('🎨 Settings changed:', newSettings)
        settingsStore.saveSettings()
      },
      { deep: true }
    )

    // ✅ Watch خاص باللون الأساسي
    watch(
      () => settingsStore.settings.appearance.primaryColor,
      (newColor) => {
        console.log('🎨 Primary color changed to:', newColor)
        // الـ Sidebar بتتحدث تلقائياً
      }
    )
    watch(showReturnInvoiceBox, (v) => {
      console.log('showReturnInvoiceBox:', v)
    })

    watch(isShiftOpen, (val) => {
      console.log('POS saw isShiftOpen change to:', val)
    })
    const settings = computed(() => settingsStore.settings)
    const primaryColor = computed(() => {
      return settings.value?.appearance?.primaryColor || '#06b6d4'
    })

</script>
