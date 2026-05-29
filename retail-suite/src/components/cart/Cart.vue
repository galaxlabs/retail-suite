<!-- Cart.vue -->
<template>
  <!-- wrapper section -->
  <div
    class="rounded-xl flex flex-col min-h-[70vh] shadow"
    :style="{
      backgroundColor: 'var(--cart-bg)',
      borderColor: 'var(--cart-border)',
      boxShadow: 'var(--cart-shadow)',
      color: 'var(--cart-text-primary)'
    }"
  >
    <!-- Selected Invoice Info (for returns) -->
    <div
      v-if="mode === 'return' && selectedInvoice"
      class="p-4"
      :style="{
        borderBottom: '1px solid var(--card-border)',
        background: 'var(--warning-bg)'
      }"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">

          <!-- Icon Circle -->
          <div
            class="w-10 h-10 rounded-full flex items-center justify-center"
            :style="{ background: 'var(--warning-bg)', border: '1px solid var(--warning-border)' }"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"
              :style="{ color: 'var(--warning-border)' }"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>

          <div>
            <p class="text-sm font-bold" :style="{ color: 'var(--text-main)' }">
              {{ selectedInvoice.name }}
            </p>
            <p class="text-xs" :style="{ color: 'var(--text-muted)' }">
              {{ formatDate(selectedInvoice.posting_date) }}
            </p>
          </div>
        </div>

        <button
          @click="clearSelectedInvoice"
          class="transition-colors"
          :style="{ color: 'var(--warning-border)' }"
          title="Clear selection"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Empty Cart -->
    <div
      v-if="cartStore.cart.length === 0"
      class="rounded-3xl flex-1 w-full p-4 select-none flex flex-col flex-wrap items-center justify-center"
      :style="{
        backgroundColor: 'var(--cart-bg-empty)',
        color: 'var(--cart-text-empty)'
      }"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor"
        :style="{ color: 'var(--text-muted)', opacity: 0.4 }"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      <p class="text-center text-lg font-medium mt-4">
        {{ mode === 'return' ? 'NO ITEMS SELECTED' : 'CART EMPTY' }}
      </p>
      <p class="text-center text-sm mt-2" :style="{ color: 'var(--text-muted)' }">
        {{ mode === 'return' ? 'Select an invoice and load items' : 'Add some products to get started' }}
      </p>
    </div>

    <!-- Cart with Items -->
    <div v-else class="flex-1 flex flex-col">

      <!-- Cart Header -->
      <div
        class="h-16 text-center flex justify-center"
        :style="{ borderBottom: '1px solid var(--card-border)' }"
      >
        <div class="pl-8 text-left text-lg py-4 relative">
          <CartIcon />
          <div
            v-if="cartStore.itemsCount > 0"
            :style="{
              backgroundColor: mode === 'return' ? 'var(--cart-badge-return)' : primaryColor
            }"
            class="text-center absolute text-white w-5 h-5 text-xs p-0 leading-5 rounded-full -right-2 top-3"
          >
            {{ cartStore.itemsCount }}
          </div>
        </div>

        <div class="flex-grow px-8 text-right text-lg py-4 relative">
          <!-- Clear Cart Button -->
          <button
            @click="handleClearCart"
            class="focus:outline-none transition-colors duration-200 p-1 rounded"
            :style="{ color: 'var(--text-muted)' }"
            title="Clear cart"
            :disabled="cartStore.isProcessing"
          >
            <TrashIcon />
          </button>
        </div>
      </div>

      <!-- Customer Selector -->
      <CustomerSection @customer-selected="handleCustomerSelected" />
      <div class="px-4 pt-2 text-xs" :style="{ color: 'var(--text-muted)' }">
        {{ salesChannel === 'wholesale' ? 'Wholesale: select customer before checkout' : 'Retail: customer optional for quick billing' }}
      </div>

      <!-- Cart Items List -->
      <div class="w-full px-4 pb-4">
        <transition-group name="cart-item" tag="div">
          <CartItem
            v-for="item in cartStore.cart"
            :key="item.item_code"
            :item="item"
            :mode="mode"
            @update-quantity="handleUpdateQuantity"
            @remove-item="handleRemoveItem"
          />
        </transition-group>
      </div>
    </div>

    <!-- Payment Section -->
    <PaymentSection
      v-if="cartStore.cart.length > 0 && !cartStore.isReturn"
      :mode="mode"
      :selected-invoice="selectedInvoice"
      @submit="handletransactionData"
      @cash-update="handleCashUpdate"
    />

    <!-- Return Section -->
    <ReturnSection v-else />
  </div>
</template>

<script setup>

import CartIcon from '@/components/icons/CartIcon.svg'
import TrashIcon from '@/components/icons/TrashIcon.svg'
import { ref, computed, nextTick, watch } from 'vue'
import CartItem from './CartItem.vue'
import PaymentSection from './PaymentSection.vue'
import ReturnSection from './ReturnSection.vue'
import { formatDate } from '../../utils/formatters'
import CustomerSection from './CustomerSection.vue'
import { useCartStore } from '@/stores/cart'
import { useShiftStore } from '@/stores/shift'
import { useSettingsStore } from '@/stores/settings'
import Swal from 'sweetalert2'

const props = defineProps({
  mode: {
    type: String,
    default: 'sale',
    validator: (value) => ['sale', 'return'].includes(value)
  },
  selectedInvoice: {
    type: Object,
    default: null
  },
  salesChannel: {
    type: String,
    default: 'retail'
  },
  customerRequired: {
    type: Boolean,
    default: false
  }
})
const emit = defineEmits(['submit', 'cart-cleared', 'item-removed', 'clear-invoice'])

const settingsStore = useSettingsStore()
const settings = computed(() => settingsStore.settings)
const primaryColor = computed(() => {
  return settings.value?.appearance?.primaryColor || '#06b6d4'
})

const cartStore = useCartStore()
const shiftStore = useShiftStore()
const showAddCustomerModal = ref(false)
const selectedCustomer = ref('')
const itemsCount = ref(0)
const handleCustomerSelected = (customerName) => {
  selectedCustomer.value = customerName
  shiftStore.setCustomer(customerName) // لو عندك method في store
}

const clearSelectedInvoice = () => {
  emit('clear-invoice')
  cartStore.clearCart()
}

// Handle quantity update
const handleUpdateQuantity = (item_code, newQuantity, mode) => {
  // In return mode, validate against original quantity
  console.log('handleUpdateQuantity')
  if (props.mode === 'return') {
      console.log('handleUpdateQuantity mode : return')
    const item = cartStore.cart.find(i => i.item_code === item_code)

    if (item && item.originalQuantity && newQuantity > item.originalQuantity) {
      if (window.$toast) {
        window.$toast.warning('Cannot return more than original quantity')
      }
      return
    }

  }
  const result = cartStore.updateQuantity(item_code, newQuantity, props.mode)
  console.log('handleUpdateQuantity result',result)
}

// Handle item removal
const handleRemoveItem = (item_code) => {
  cartStore.removeFromCart(item_code)
  emit('item-removed', item_code)
}

// Handle clear cart
const handleClearCart = async () => {
  if (cartStore.isProcessing) return


const message = props.mode === 'return'
  ? 'Are you sure you want to clear return items?'
  : 'Are you sure you want to clear the cart?'


const confirmed = await Swal.fire({
  title: `<strong>${message}</strong>`,
  width: 800,
  padding: "3em",
  color: "#fff",
  background: "#0e7490 url('/images/trees.png') no-repeat right top",
  backdrop: `
    rgba(0,0,0,0.4)
    url("/images/nyan-cat.gif")
    left top
    no-repeat
  `,
  icon: "question",
  showCancelButton: true,
  confirmButtonColor: "#28a745",
  cancelButtonColor: "#dc3545",
  confirmButtonText: `<i style="color:#fff" class="fa fa-thumbs-up"></i> Yes, clear it!`,
  cancelButtonText: `<i style="color:#fff" class="fa fa-thumbs-down"></i> Cancel`,
  cancelButtonAriaLabel: "Cancel",
  footer: '<a href="#" style="color:#fff;text-decoration:underline;">Why do I see this?</a>',
  allowOutsideClick: false,
  allowEscapeKey: false
})

// إذا ضغط Cancel، لا تفعل شيء
if (confirmed.isDismissed) return

// إذا ضغط Yes فقط، نفذ الحذف مباشرة بدون رسالة تأكيد ثانية
if (confirmed.isConfirmed) {
  cartStore.clearCart()

  if (props.mode === 'return') {
    emit('clear-invoice')
  }
  emit('cart-cleared')

  // رسالة نجاح سريعة (تختفي تلقائياً بعد ثانيتين)
  await Swal.fire({
    title: "Done! ✓",
    icon: "success",
    timer: 1000,
    timerProgressBar: true,
    showConfirmButton: false
  })
}

  // if (!confirmed.isConfirmed) return

  cartStore.clearCart()
  if (props.mode === 'return') {
    emit('clear-invoice')
  }
  emit('cart-cleared')
}

// Handle cash update
const handleCashUpdate = (amount) => {
  cartStore.setCash(amount)
}

// Handle transaction submit

const handletransactionData = async (paymentData) => {
  console.log("7️⃣ Cart: handletransactionData called")
  console.log("   Received:", paymentData)


  if (props.customerRequired && !shiftStore.$state.currentCustomer) {
    if (window.$toast) {
      window.$toast.warning("Please select a customer for wholesale invoice")
    }
    return
  }

  try {
    console.log("8️⃣ Cart: Building full data")

    let originalInvoice = null

    if (props.mode === 'return' && props.selectedInvoice) {
      originalInvoice = {
        id: props.selectedInvoice.id,
        receiptNo: props.selectedInvoice.name,
        receiptDate: props.selectedInvoice.posting_date
      }
    }

    const fullData = {
      ...paymentData,  // ✅ يحتوي على transactionData من PaymentSection
      mode: props.mode,
      transactionType: props.mode === 'return' ? 'return' : 'sale'
    }

    console.log("9️⃣ Cart: Full data ready")
    console.log("   Full data:", fullData)

    // ✅ أطلع emit
    console.log("🔟 Cart: Emitting to POS...")
    emit('submit', fullData)

    console.log("1️⃣1️⃣ Cart: Emit done!")

  } catch (error) {
    console.error('❌ Cart Error:', error)
    if (window.$toast) {
      window.$toast.error('Transaction failed')
    }
  }
}

watch(
  () => cartStore.cart,
  (newCart) => {
    console.log('🟢 Cart updated - Cart.vue detected change')
    console.log('   Cart items:', newCart)
    console.log('   Cart length:', newCart.length)

    itemsCount.value = newCart.length

    // إعادة تصيير العنصر
    nextTick(() => {
      scrollToBottom()
    })
  },
  {
    deep: true,
    immediate: true  // ✅ مهم: تشغيل الـ watcher فوراً عند التجميع
  }
)
// 🔍 مراقب أخرى للتأكد
watch(
  () => cartStore.itemsCount,
  (newCount) => {
    console.log('🔔 Items count changed:', newCount)
  }
)

// 🔍 مراقب الخصائص
watch(
  () => props.mode,
  (newMode) => {
    console.log('📌 Mode changed:', newMode)
  }
)

// Scroll to bottom when new item added
const scrollToBottom = () => {
  nextTick(() => {
    const cartItemsList = document.querySelector('.overflow-auto')
    if (cartItemsList) {
      cartItemsList.scrollTop = cartItemsList.scrollHeight
    }
  })
}

</script>

<style scoped>
.cart-item-enter-active,
.cart-item-leave-active {
  transition: all 0.3s ease;
}

.cart-item-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.cart-item-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
