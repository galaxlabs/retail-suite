import { defineStore } from 'pinia'
import { ref, computed, toRaw } from 'vue'
import { createSalesReturn, createSalesOrder } from '@/composables/pos'

export const useCartStore = defineStore('cart', () => {

  /* ============================================================
     STATE
  ============================================================ */
  const cart = ref([])
  const cash = ref(0)
  const taxRate = ref(0)
  const discountRate = ref(0)
  const isProcessing = ref(false)

  // Modes
  const isReturnMode = ref(false)
  const isDraftMode = ref(false)

  // References
  const returnAgainst = ref(null)
  const currentDraftName = ref(null)   // اسم الدرافت المفتوح حالياً
  const currentCustomer = ref(null)
  const pos_profile_name = ref(null)
  const returndoc = ref(null)

  const moneys = [2000, 5000, 10000, 20000, 50000, 100000]

  /* ============================================================
     GETTERS
  ============================================================ */
  const itemsCount = computed(() =>
    cart.value.reduce((total, item) => total + item.qty, 0)
  )

  const subtotal = computed(() =>
    cart.value.reduce((total, item) => total + item.rate * item.qty, 0)
  )

  const taxAmount = computed(() =>
    Math.round(subtotal.value * (taxRate.value / 100))
  )

  const discountAmount = computed(() =>
    Math.round(subtotal.value * (discountRate.value / 100))
  )

  const totalPrice = computed(() =>
    subtotal.value + taxAmount.value - discountAmount.value
  )

  const changeAmount = computed(() =>
    cash.value - totalPrice.value
  )

  const canSubmit = computed(() =>
    cart.value.length > 0 &&
    cash.value >= totalPrice.value &&
    !isProcessing.value
  )

  const cartSummary = computed(() => ({
    itemsCount: itemsCount.value,
    subtotal: subtotal.value,
    tax: taxAmount.value,
    discount: discountAmount.value,
    total: totalPrice.value,
    cash: cash.value,
    change: changeAmount.value
  }))

  const isEmpty = computed(() => cart.value.length === 0)

  const hasDiscount = computed(() => discountRate.value > 0)

  const hasTax = computed(() => taxRate.value > 0)

  /* ============================================================
     CART ACTIONS
  ============================================================ */
  const addToCart = (product, barcode = null) => {
    const existing = cart.value.find(i => i.item_code === product.item_code)
    const qtyToAdd = product.qty || 1

    if (existing) {
      existing.qty += qtyToAdd
    } else {
      cart.value.push({
        item_code: product.item_code,
        item_name: product.item_name,
        rate: product.rate,
        image: product.image || '',
        barcode: barcode?.code || '',
        category: product.item_group || '',
        qty: qtyToAdd,
        addedAt: new Date().toISOString()
      })
    }
    _updateChange()
  }

  const removeFromCart = (item_code) => {
    const index = cart.value.findIndex(i => i.item_code === item_code)
    if (index !== -1) {
      cart.value.splice(index, 1)
      _updateChange()
    }
  }

  const updateQuantity = (item_code, newQty, mode) => {
    const item = cart.value.find(i => i.item_code === item_code)
    if (!item) return

    if (mode === 'return') {
      if (newQty > 0) newQty = -Math.abs(newQty)
      if (item.originalQuantity && Math.abs(newQty) > item.originalQuantity) {
        window.$toast?.warning('Cannot return more than original quantity')
        return
      }
      item.qty = newQty
    } else {
      if (newQty <= 0) {
        removeFromCart(item_code)
        return
      }
      item.qty = newQty
    }
    _updateChange()
  }

  const addQuantity = (item_code, amount) => {
    const item = cart.value.find(i => i.item_code === item_code)
    if (!item) return
    const newQty = item.qty + amount
    newQty <= 0 ? removeFromCart(item_code) : (item.qty = newQty, _updateChange())
  }

  const getCartItem = (item_code) =>
    cart.value.find(i => i.item_code === item_code)

  const isInCart = (item_code) =>
    cart.value.some(i => i.item_code === item_code)

  const getProductQuantity = (item_code) =>
    cart.value.find(i => i.item_code === item_code)?.qty ?? 0

  /* ============================================================
     CASH ACTIONS
  ============================================================ */
  const setCash = (amount) => {
    cash.value = Math.max(0, amount)
    _updateChange()
  }

  const addCash = (amount) => {
    cash.value += amount
    _updateChange()
  }

  const updateCashFromString = (str) => {
    const amount = parseFloat(str.replace(/[^\d.]/g, '')) || 0
    setCash(amount)
  }

  /* ============================================================
     PRICING ACTIONS
  ============================================================ */
  const setTaxRate = (rate) => {
    taxRate.value = Math.max(0, Math.min(100, rate))
    _updateChange()
  }

  const setDiscountRate = (rate) => {
    discountRate.value = Math.max(0, Math.min(100, rate))
    _updateChange()
  }

  const applyDiscountAmount = (amount) => {
    if (subtotal.value > 0) {
      setDiscountRate(Math.min(100, (amount / subtotal.value) * 100))
    }
  }

  /* ============================================================
     DRAFT INVOICE ACTIONS
  ============================================================ */
  const loadDraftInvoice = (invoice) => {
    clearCart()

    isDraftMode.value = true
    currentDraftName.value = invoice.name
    currentCustomer.value = invoice.customer || null

    invoice.items?.forEach(item => {
      cart.value.push({
        item_code: item.item_code,
        item_name: item.item_name,
        rate: item.rate,
        image: item.image || '',
        category: item.item_group || '',
        qty: item.qty,
        addedAt: new Date().toISOString()
      })
    })

    if (invoice.discount_amount) {
      applyDiscountAmount(invoice.discount_amount)
    }

    _updateChange()
  }

  const clearDraftMode = () => {
    isDraftMode.value = false
    currentDraftName.value = null
    currentCustomer.value = null
  }

  /* ============================================================
     RETURN ACTIONS
  ============================================================ */
  const setReturnAgainst = (invoice, profile) => {
    returnAgainst.value = invoice
    pos_profile_name.value = profile
  }

  const loadReturnItems = (items = []) => {
    clearCart()
    isReturnMode.value = true

    items.forEach(it => {
      cart.value.push({
        item_code: it.item_code || it.id,
        item_name: it.item_name || it.name,
        rate: it.rate || it.price || 0,
        image: it.image || '',
        category: it.category || '',
        qty: -it.qty,
        originalQuantity: it.qty || it.quantity || 1,
        isReturn: true
      })
    })
    _updateChange()
  }

  const handleReturnSubmit = async () => {
    try {
      await processReturnTransaction({
        is_return: 1,
        pos_profile_name: pos_profile_name.value,
        return_against: returnAgainst.value?.name,
        customer: returnAgainst.value?.customer,
        items: cart.value.map(item => ({ ...item, qty: Math.abs(item.qty) }))
      })
      window.$toast?.success('Return processed successfully!')
    } catch (error) {
      console.error('Return failed:', error)
      window.$toast?.error('Failed to process return.')
    }
  }

  const processReturnTransaction = async (returnDoc) => {
    if (!returnDoc?.items) {
      console.error('❌ Invalid returnDoc:', returnDoc)
      return
    }
    isReturnMode.value = true
    clearCart()

    returnDoc.items.forEach(it => {
      cart.value.push({
        item_code: it.item_code || it.id,
        item_name: it.item_name || it.name,
        rate: it.rate || it.price || 0,
        image: it.image || '',
        qty: it.qty,
        originalQuantity: it.qty,
        isReturn: true
      })
    })

    if (returnDoc.discount_amount) {
      discountRate.value = Math.abs(returnDoc.discount_amount)
    }

    _updateChange()

    const returnResponse = await createSalesReturn(
      returnAgainst.value?.name,
      returnDoc.items,
      pos_profile_name.value
    )

    if (returnResponse) clearCart()
    return returnResponse
  }

  /* ============================================================
     TRANSACTION ACTIONS
  ============================================================ */
  const processTransaction = async (mode, originalInvoice = null) => {
    isProcessing.value = true
    try {
      const transactionData = {
        draftName: isDraftMode.value ? currentDraftName.value : undefined,   /* # if you send draft invoice #*/
        items: toRaw(cart.value),
        summary: cartSummary.value,
        timestamp: new Date().toISOString(),
        transactionId: _generateTransactionId(),
        customer: currentCustomer.value,
        mode,
        originalInvoice
      }
      await _saveTransaction(transactionData)
      return transactionData
    } catch (error) {
      console.error('Transaction failed:', error)
      throw error
    } finally {
      isProcessing.value = false
    }
  }

  const processTransactionCreateOrder = async (customer, transactionData) => {
    try {
      return await createSalesOrder(customer, transactionData)
    } catch (error) {
      console.error('Order creation failed:', error)
      throw error
    }
  }

  /* ============================================================
     CLEAR & RESET
  ============================================================ */
  const clearCart = () => {
    cart.value = []
    cash.value = 0
    taxRate.value = 0
    discountRate.value = 0
    isProcessing.value = false
    isReturnMode.value = false
    clearDraftMode()
  }

  const resetCart = () => {
    clearCart()
    returnAgainst.value = null
    pos_profile_name.value = null
    returndoc.value = null
  }

  /* ============================================================
     UTILITIES
  ============================================================ */
  const getChangeBreakdown = () => {
    let remaining = changeAmount.value
    const denominations = [100000, 50000, 20000, 10000, 5000, 2000, 1000, 500, 100, 50, 25, 10, 5, 1]
    const breakdown = []
    for (const denom of denominations) {
      if (remaining >= denom) {
        const count = Math.floor(remaining / denom)
        breakdown.push({ denomination: denom, count })
        remaining -= count * denom
      }
    }
    return breakdown
  }

  /* ============================================================
     PRIVATE HELPERS
  ============================================================ */
  const _updateChange = () => {
    // computed handles it, just trigger reactivity log
  }

  const _generateTransactionId = () => {
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
    return `TXN${Date.now()}${random}`
  }

  const _saveTransaction = async (transactionData) => {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(transactionData)
      }, 500)
    })
  }

  /* ============================================================
     EXPOSE
  ============================================================ */
  return {
    // State
    cart,
    cash,
    taxRate,
    discountRate,
    isProcessing,
    isReturnMode,
    isDraftMode,
    currentDraftName,
    currentCustomer,
    returnAgainst,
    pos_profile_name,
    returndoc,
    moneys,

    // Getters
    itemsCount,
    subtotal,
    taxAmount,
    discountAmount,
    totalPrice,
    changeAmount,
    canSubmit,
    cartSummary,
    isEmpty,
    hasDiscount,
    hasTax,

    // Cart
    addToCart,
    removeFromCart,
    updateQuantity,
    addQuantity,
    getCartItem,
    isInCart,
    getProductQuantity,

    // Cash
    setCash,
    addCash,
    updateCashFromString,

    // Pricing
    setTaxRate,
    setDiscountRate,
    applyDiscountAmount,

    // Draft
    loadDraftInvoice,
    clearDraftMode,

    // Return
    setReturnAgainst,
    loadReturnItems,
    handleReturnSubmit,
    processReturnTransaction,

    // Transaction
    processTransaction,
    processTransactionCreateOrder,

    // Clear
    clearCart,
    resetCart,

    // Utilities
    getChangeBreakdown,
  }
})
