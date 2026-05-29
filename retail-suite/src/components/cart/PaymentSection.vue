<!-- Payment Section -->
<template>
  <div
    class="select-none h-auto w-full text-center pt-3 pb-4 px-4 rounded-lg"
    :style="{
      backgroundColor: 'var(--card-bg)',
      borderTop: '1px solid var(--card-border)',
      color: 'var(--text-main)'
    }"
  >
    <!-- Order Summary -->
    <div class="mb-4">

      <!-- Subtotal -->
      <div
        v-if="showDetailedSummary"
        class="flex mb-2 text-sm"
        :style="{ color: 'var(--text-sub)' }"
      >
        <div>Subtotal</div>
        <div class="text-right w-full">{{ formatPrice(cartStore.subtotal) }}</div>
      </div>

      <!-- Tax -->
      <div
        v-if="cartStore.taxAmount > 0"
        class="flex mb-2 text-sm"
        :style="{ color: 'var(--text-sub)' }"
      >
        <div>Tax ({{ cartStore.taxRate }}%)</div>
        <div class="text-right w-full">{{ formatPrice(cartStore.taxAmount) }}</div>
      </div>

      <!-- Discount -->
      <div
        v-if="cartStore.discountAmount > 0"
        class="flex mb-2 text-sm"
        :style="{ color: 'var(--icon-color-green)' }"
      >
        <div>Discount ({{ cartStore.discountRate }}%)</div>
        <div class="text-right w-full">-{{ formatPrice(cartStore.discountAmount) }}</div>
      </div>

      <!-- Total -->
      <div
        class="flex mb-3 text-lg font-semibold pt-2"
        :style="{
          color: 'var(--text-main)',
          borderTop: '1px solid var(--card-border)'
        }"
      >
        <div>TOTAL</div>
        <div class="text-right w-full">{{ formatPrice(cartStore.totalPrice) }}</div>
      </div>
    </div>

    <!-- Cash Payment Section -->
    <div
      class="mb-3 px-3 pt-2 pb-3 rounded-lg"
      :style="{
        backgroundColor: 'var(--item-bg)',
        border: '1px solid var(--item-border)'
      }"
    >
      <!-- Cash Input -->
      <div class="flex text-lg font-semibold mb-3">
        <div class="flex-grow text-left" :style="{ color: 'var(--text-main)' }">
          {{ selectedPaymentMethod }}
        </div>
        <div class="flex text-right">
          <div class="mr-2" :style="{ color: 'var(--text-sub)' }">{{ currency }}</div>
          <input
            ref="cashInput"
            :value="formatCashInput(cashAmount)"
            @input="handleCashInput"
            @focus="handleCashFocus"
            @blur="handleCashBlur"
            @keyup.enter="handleQuickSubmit"
            @keyup.escape="resetCash"
            type="text"
            inputmode="numeric"
            class="w-28 text-right rounded-lg px-2 transition-all duration-200"
            :style="{
              backgroundColor: 'var(--input-bg)',
              color: 'var(--text-main)',
              border: hasPaymentError
                ? '1px solid var(--warning-border)'
                : isExactAmount
                ? '1px solid var(--icon-color-green)'
                : '1px solid var(--input-border)'
            }"
            placeholder="0"
            :disabled="cartStore.isProcessing"
          >
        </div>
      </div>

      <!-- Payment Error -->
      <div
        v-if="hasPaymentError"
        class="text-sm mb-2 text-left"
        :style="{ color: 'var(--warning-border)' }"
      >
        {{ paymentErrorMessage }}
      </div>

      <!-- Divider -->
      <hr :style="{ borderColor: 'var(--card-border)' }" class="my-2">

      <!-- Quick Cash Buttons -->
      <div class="grid grid-cols-3 gap-2 mt-2">
        <button
          v-for="money in quickCashAmounts"
          :key="money"
          @click="addCashAmount(money)"
          class="rounded-lg shadow hover:shadow-lg focus:outline-none text-sm px-2 py-1 transition-all duration-200 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          :style="{
            background: 'var(--card-bg)',
            color: 'var(--text-main)',
            border: '1px solid var(--card-border)'
          }"
          :disabled="cartStore.isProcessing"
          :title="`Add ${formatPrice(money)}`"
        >
          +{{ formatShortPrice(money) }}
        </button>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-2 gap-2 mt-2">

        <!-- Exact Button -->
        <button
          @click="setExactAmount"
          class="rounded-lg shadow focus:outline-none px-2 py-1 text-xs transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          :style="{
            background: 'var(--info-bg)',
            color: 'var(--focus-ring)',
            border: '1px solid var(--info-border)'
          }"
          :disabled="cartStore.isProcessing"
        >
          <ExactIcon class="w-3 h-3 inline mr-1" />
          Exact
        </button>

        <!-- Clear Button -->
        <button
          @click="clearCash"
          class="rounded-lg shadow focus:outline-none px-2 py-1 text-xs transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          :style="{
            background: 'var(--item-bg)',
            color: 'var(--text-muted)',
            border: '1px solid var(--item-border)'
          }"
          :disabled="cartStore.isProcessing"
        >
          <ClearIcon class="w-3 h-3 inline mr-1" />
          Clear
        </button>
      </div>
    </div>

    <!-- Change Display -->
    <div class="mb-3">

      <!-- Positive Change -->
      <div
        v-if="changeAmount > 0"
        class="flex text-lg font-semibold rounded-lg py-2 px-3"
        :style="{
          backgroundColor: 'var(--info-bg)',
          color: 'var(--focus-ring)',
          border: '1px solid var(--info-border)'
        }"
      >
        <div class="flex items-center" :style="{ color: 'var(--focus-ring)' }">
          <ChangeIcon class="w-5 h-5 mr-2" />
          CHANGE
        </div>
        <div class="text-right flex-grow">
          {{ formatPrice(changeAmount) }}
        </div>
      </div>

      <!-- Negative Change (Insufficient) -->
      <div
        v-else-if="changeAmount < 0"
        class="flex text-lg font-semibold rounded-lg py-2 px-3"
        :style="{
          backgroundColor: 'var(--warning-bg)',
          color: 'var(--warning-border)',
          border: '1px solid var(--warning-border)'
        }"
      >
        <div v-if="!showPartialOption" class="flex items-center justify-between w-full">
          <div
            role="button"
            tabindex="0"
            @click="showPartialOption = true"
            @keydown.enter="showPartialOption = true"
            @keydown.space.prevent="showPartialOption = true"
            class="flex items-center cursor-pointer select-none hover:opacity-90 active:scale-95 transition-transform duration-150"
            :style="{ color: 'var(--warning-border)' }"
            aria-label="Show partial option"
          >
            <WarningIcon class="w-5 h-5 mr-2" />
            INSUFFICIENT
          </div>
          <div>{{ formatPrice(Math.abs(changeAmount)) }} needed</div>
        </div>

        <div v-else class="flex items-center justify-between w-full">
          <div class="flex items-center gap-2 flex-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"
              :style="{ color: 'var(--warning-border)' }"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span class="text-sm font-semibold" :style="{ color: 'var(--warning-border)' }">
              Partial Payment
            </span>
          </div>

          <div class="flex gap-1">
            <!-- Confirm -->
            <button
              class="p-1.5 text-white rounded-lg transition-all duration-200"
              :style="{ background: 'var(--icon-color-green)' }"
              @click="enablePartialPayment(true)"
              title="Confirm partial payment"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </button>

            <!-- Cancel -->
            <button
              class="p-1.5 text-white rounded-lg transition-all duration-200"
              :style="{ background: 'var(--text-muted)' }"
              @click="enablePartialPayment(false)"
              title="Cancel"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Exact Amount -->
      <div
        v-else-if="changeAmount === 0 && cashAmount > 0"
        class="flex justify-center text-lg font-semibold rounded-lg py-2 px-3"
        :style="{
          background: 'var(--info-bg)',
          color: 'var(--focus-ring)',
          border: '1px solid var(--info-border)'
        }"
      >
        <ThumbsUpIcon class="w-6 h-6 inline-block mr-2" />
        EXACT AMOUNT
      </div>
    </div>

    <!-- Payment Method Selection -->
    <div v-if="showPaymentMethods" class="mb-3">
      <div
        class="text-sm mb-2"
        :style="{ color: 'var(--text-muted)' }"
      >
        Payment Method
      </div>
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="method in paymentMethods"
          :key="method"
          @click="selectPaymentMethod(method.name)"
          class="px-3 py-2 text-xs rounded-lg transition-all duration-200"
          :style="selectedPaymentMethod === method.name
            ? { background: primaryColor, color: '#fff', border: '1px solid transparent' }
            : { background: 'var(--card-bg)', color: 'var(--text-main)', border: '1px solid var(--card-border)' }
          "
          :disabled="cartStore.isProcessing"
        >
          <component :is="method.icon" class="w-4 h-4 inline mr-1" />
          {{ method.name }}
        </button>
      </div>
    </div>

    <!-- Submit Button -->
    <button
      :style="{ background: primaryColor }"
      class="text-white rounded-2xl text-lg w-full py-3 focus:outline-none transition-all duration-200 transform disabled:transform-none relative overflow-hidden"
      :class="submitButtonClass"
      :disabled="!canSubmit"
      @click="handleSubmit"
    >
      <div class="relative z-10 flex items-center justify-center">
        <component :is="submitButtonIcon" class="w-6 h-6 mr-2" />
        {{ submitButtonText }}
      </div>

      <!-- Loading Animation -->
      <div
        v-if="cartStore.isProcessing"
        class="absolute inset-0 flex items-center justify-center"
        :style="{ background: primaryColor }"
      >
        <LoadingSpinner class="w-6 h-6" />
      </div>

      <!-- Success Animation -->
      <div
        v-if="showSuccessAnimation"
        class="absolute inset-0 flex items-center justify-center animate-pulse"
        :style="{ background: 'var(--icon-color-green)' }"
      >
        <CheckIcon class="w-6 h-6" />
      </div>
    </button>

    <!-- Additional Info -->
    <div class="mt-2 text-xs" :style="{ color: 'var(--text-muted)' }">
      <div v-if="cartStore.itemsCount > 0">
        {{ cartStore.itemsCount }} {{ cartStore.itemsCount === 1 ? 'item' : 'items' }} in cart
      </div>
      <div v-if="lastTransactionId" class="mt-1">
        Last transaction: #{{ lastTransactionId }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useShiftStore } from '@/stores/shift'
import { formatPrice } from '../../utils/formatters'
import ExactIcon from '@/components/icons/ExactIcon.svg'
import ClearIcon from '@/components/icons/ClearIcon.svg'
import ChangeIcon from '@/components/icons/ChangeIcon.svg'
import WarningIcon from '@/components/icons/WarningIcon.svg'
import ThumbsUpIcon from '@/components/icons/ThumbsUpIcon.svg'
import CheckIcon from '@/components/icons/CheckIcon.svg'
import LockIcon from '@/components/icons/LockIcon.svg'
import LoadingSpinner from '@/components/icons/LoadingSpinner.vue'
import CashIcon from '@/components/icons/CashIcon.svg'
import CardIcon from '@/components/icons/CardIcon.svg'
import PhoneIcon from '@/components/icons/PhoneIcon.svg'
import { useSettingsStore } from '@/stores/settings'

const props = defineProps({
  mode: {
  type: String,
  default: 'sale', // 'sale' or 'return'
  validator: (value) => ['sale', 'return'].includes(value)
},
selectedInvoice: {
  type: Object,
  default: null
},
showDetailedSummary: {
  type: Boolean,
  default: true
},
showPaymentMethods: {
  type: Boolean,
  default: true
},
autoFocusCash: {
  type: Boolean,
  default: true
}
})
const emit = defineEmits(['submit', 'cash-update', 'payment-error', 'payment-success'])

const settingsStore = useSettingsStore()
const settings = computed(() => settingsStore.settings)
const primaryColor = computed(() => {
  return settings.value?.appearance?.primaryColor || '#06b6d4'
})

const cartStore = useCartStore()
const cashInput = ref(null)
const cashAmount = ref(0)
const hasPaymentError = ref(false)
const paymentErrorMessage = ref('')
const showSuccessAnimation = ref(false)

const lastTransactionId = ref('')
const isFocused = ref(false)
const shiftStore = useShiftStore()
// Quick cash amounts
const quickCashAmounts = computed(() => cartStore.moneys || [2000, 5000, 10000, 20000, 50000, 100000])
// Initialize currency from store or default
const showPartialOption = ref(false)
const allowPartialPayment = ref(false)
const enablePartialPayment = (val) => {
    allowPartialPayment.value = val

    if (allowPartialPayment.value) {
      window.$toast.info('Partial payment activated ✔')
    }else{
      showPartialOption.value = false
      window.$toast.warning('Partial payment stopped ✔')
    }
  }
const currency = computed(() => shiftStore.pos_profile.currency || 'SAR')
const paymentMethods = computed(() => {

  return (shiftStore.payment_methods || []).map(pm => {
    return {
      id: pm.row_id,
      name: pm.mode_of_payment,
      icon: mapIcon(pm.mode_of_payment),
      default:pm.default
    }
  })
})
const selectedPaymentMethod = ref(
  paymentMethods.value.find(pm => pm.default)?.name || null
)

function mapIcon(name) {
  switch(name.toLowerCase()) {
    case 'cash': return 'CashIcon'
    case 'credit card': return 'CardIcon'
    case 'digital': return 'PhoneIcon'
    default: return 'CashIcon'
  }
}
// Computed properties
const changeAmount = computed(() => {
  return cashAmount.value - cartStore.totalPrice
})

const isExactAmount = computed(() => {
  return changeAmount.value === 0 && cashAmount.value > 0
})

const canSubmit = computed(() => {
  const hasEnoughCash = cashAmount.value >= cartStore.totalPrice
  const canPayPartially = allowPartialPayment.value && cashAmount.value < cartStore.totalPrice
  return cartStore.cart.length > 0 &&
      !cartStore.isProcessing &&
      !hasPaymentError.value &&
      (hasEnoughCash || canPayPartially)

})

const submitButtonClass = computed(() => {
  if (cartStore.isProcessing) {
    return 'bg-cyan-400 cursor-wait'
  } else if (canSubmit.value) {
    return 'bg-cyan-500 hover:bg-cyan-600 hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl'
  } else {
    return 'bg-gray-200 cursor-not-allowed'
  }
})

const submitButtonText = computed(() => {
  if (cartStore.isProcessing) {
    return 'PROCESSING...'
  } else if (cartStore.cart.length === 0) {
    return 'ADD ITEMS TO CART'
  } else if (cashAmount.value < cartStore.totalPrice) {
    return `NEED ${formatPrice(cartStore.totalPrice - cashAmount.value)} MORE`
  } else {
    return 'COMPLETE SALE'
  }
})

const submitButtonIcon = computed(() => {
  if (cartStore.isProcessing) {
    return 'LoadingSpinner'
  } else if (canSubmit.value) {
    return 'CheckIcon'
  } else {
    return 'LockIcon'
  }
})

// Watch cash amount changes
watch(cashAmount, (newAmount) => {
  cartStore.setCash(newAmount)
  emit('cash-update', newAmount)

  // Clear errors when user types
  if (hasPaymentError.value && newAmount >= cartStore.totalPrice) {
    clearPaymentError()
  }
})
const formatShortPrice = (price) => {
  if (price >= 1000000) {
    return `${price / 1000000}M`
  } else if (price >= 1000) {
    return `${price / 1000}K`
  }
  return price.toString()
}

// Format cash input display
const formatCashInput = (amount) => {
  if (isFocused.value) {
    return amount.toString()
  }
  return new Intl.NumberFormat('en-SA').format(amount || 0)
}

// Handle cash input
const handleCashInput = (event) => {
  const value = event.target.value.replace(/[^\d]/g, '')
  const numericValue = parseInt(value) || 0

  // Validate maximum amount (prevent overflow)
  if (numericValue > 99999999) {
    setPaymentError('Amount too large')
    return
  }

  cashAmount.value = numericValue
  clearPaymentError()
}

// Handle cash input focus
const handleCashFocus = () => {
  isFocused.value = true
}

// Handle cash input blur
const handleCashBlur = () => {
  isFocused.value = false
}

// Add cash amount
const addCashAmount = (amount) => {
  const newAmount = cashAmount.value + amount
  if (newAmount > 99999999) {
    setPaymentError('Amount too large')
    return
  }
  cashAmount.value = newAmount
}

// Set exact amount
const setExactAmount = () => {
  cashAmount.value = cartStore.totalPrice
  clearPaymentError()
}

// Clear cash
const clearCash = () => {
  cashAmount.value = 0
  clearPaymentError()
}

// Reset cash to previous valid value
const resetCash = () => {
  cashAmount.value = cartStore.cash || 0
  clearPaymentError()
}

// Set payment error
const setPaymentError = (message) => {
  hasPaymentError.value = true
  paymentErrorMessage.value = message
  emit('payment-error', message)
}

// Clear payment error
const clearPaymentError = () => {
  hasPaymentError.value = false
  paymentErrorMessage.value = ''
}

// Select payment method -> return one string like "Cash"
const selectPaymentMethod = (methodName) => {
  if (selectedPaymentMethod.value === methodName) {
    // ده نفسه الديفولت أو نفس الزر الحالي → ما تعملش حاجة
    return
  }

  // لو المستخدم غير الاختيار → حدث القيمة
  selectedPaymentMethod.value = methodName
}


// Handle quick submit (Enter key)
const handleQuickSubmit = () => {
  if (canSubmit.value) {
    handleSubmit()
  }
}

// Handle submit
const handleSubmit = async () => {
  if (!canSubmit.value) return

  // Final validation
  // if (cashAmount.value < cartStore.totalPrice) {
  //   setPaymentError('Insufficient payment amount')
  //   return
  // }

  // clearPaymentError()

  try {
    // Show success animation briefly
    showSuccessAnimation.value = true

    const transactionData = await cartStore.processTransaction(props.mode)

    const fullData = {
        ...transactionData,
        cashAmount: cashAmount.value,
        change: changeAmount.value,
        paymentMethod: selectedPaymentMethod.value
      }
    // Emit success

    // ✅ أطلع emit
    emit('submit', fullData)


    // Reset form
    setTimeout(() => {
      resetPaymentForm()
    }, 1000)

  } catch (error) {
      console.error('❌ PaymentSection Error:', error)
      setPaymentError('Payment processing failed. Please try again.')
  } finally {
    showSuccessAnimation.value = false
  }
}

// Reset payment form
const resetPaymentForm = () => {
  cashAmount.value = 0
  clearPaymentError()
  selectedPaymentMethod.value = 'cash'
}

// Focus cash input
const focusCashInput = () => {
  nextTick(() => {
    if (cashInput.value) {
      cashInput.value.focus()
      cashInput.value.select()
    }
  })
}

// Initialize
if (props.autoFocusCash) {
  nextTick(() => {
    focusCashInput()
  })
}

</script>
