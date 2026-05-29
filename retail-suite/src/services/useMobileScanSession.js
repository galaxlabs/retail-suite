import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'

const SESSION_KEY = 'retail_mobile_scan_session'

function createSessionId() {
  return `${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`
}

function getStoredSessionId() {
  const existing = localStorage.getItem(SESSION_KEY)
  if (existing) return existing

  const generated = createSessionId()
  localStorage.setItem(SESSION_KEY, generated)
  return generated
}

const stableSessionId = ref(getStoredSessionId())

export function useMobileScanSession() {
  const isListening = ref(false)
  const lastScanned = ref(null)
  const pairingConfirmed = ref(false)

  const cartStore = useCartStore()
  const productsStore = useProductsStore()

  const getEventName = () => `barcode_scan_${stableSessionId.value}`

  const refreshSession = () => {
    const next = createSessionId()
    stableSessionId.value = next
    localStorage.setItem(SESSION_KEY, next)
    return next
  }

  const onBarcodeReceived = (data) => {
    const payload = data?.message || data
    if (!payload || !payload.barcode) return

    pairingConfirmed.value = true

    if (!payload.found) {
      window.$toast?.error(`Item ${payload.barcode} not found in database`)
      return
    }

    const product = productsStore.products.find((p) => {
      const matchCode = p.item_code === payload.item_code
      const matchBarcode =
        p.barcode === payload.barcode ||
        p.item_barcode?.some((b) => b.barcode === payload.barcode) ||
        p.barcodes?.some((b) => b.barcode === payload.barcode)

      return matchCode || matchBarcode
    })

    if (product) {
      cartStore.addToCart(product)
      lastScanned.value = { barcode: payload.barcode, productName: product.item_name }
      window.$toast?.success(`Added ${product.item_name} via mobile scanner`)
    } else {
      window.$toast?.warning('Product not found in current POS profile')
    }
  }

  const startListening = () => {
    if (!window.frappe?.realtime) {
      console.error('Frappe realtime not initialized')
      return
    }

    const eventName = getEventName()
    window.frappe.realtime.off(eventName)
    window.frappe.realtime.on(eventName, onBarcodeReceived)
    isListening.value = true
  }

  const stopListening = () => {
    if (!window.frappe?.realtime) return

    const eventName = getEventName()
    window.frappe.realtime.off(eventName)
    isListening.value = false
  }

  return {
    sessionId: stableSessionId,
    isListening,
    lastScanned,
    pairingConfirmed,
    startListening,
    stopListening,
    refreshSession,
    getScannerUrl: () => `${window.location.origin}/mobile-scan?session=${stableSessionId.value}`,
  }
}
