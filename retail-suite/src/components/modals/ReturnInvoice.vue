<template>
  <div class="bg-white rounded-3xl flex flex-col h-full shadow">
    <!-- Empty Return Cart -->
    <div
      v-if="returnItems.length === 0"
      class="flex-1 w-full p-4 opacity-25 select-none flex flex-col flex-wrap content-center justify-center"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 inline-block text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
      </svg>
      <p class="text-center text-lg font-medium mt-4">
        NO RETURNS YET
      </p>
      <p class="text-center text-sm text-gray-500 mt-2">
        Scan or select invoice to process returns
      </p>
    </div>

    <!-- Return Cart with Items -->
    <div v-else class="flex-1 flex flex-col overflow-auto">
      <!-- Return Cart Header -->
      <div class="h-16 text-center flex justify-between items-center border-b border-gray-100 px-4">
        <div class="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
          </svg>
          <span class="text-lg font-semibold">Return Items</span>
          <div
            v-if="returnItems.length > 0"
            class="bg-red-500 text-white w-5 h-5 text-xs flex items-center justify-center rounded-full"
          >
            {{ returnItems.length }}
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- Invoice Number Display -->
          <span v-if="invoiceNo" class="text-sm text-gray-600 font-medium">
            Invoice: {{ invoiceNo }}
          </span>

          <!-- Clear Button -->
          <button
            @click="handleClearReturn"
            class="text-blue-gray-300 hover:text-pink-500 focus:outline-none transition-colors duration-200 p-1 rounded"
            title="Clear return items"
            :disabled="isProcessing"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Return Items List -->
      <div class="flex-1 w-full px-4 overflow-auto">
        <transition-group name="return-item" tag="div">
          <div
            v-for="item in returnItems"
            :key="item.item_code"
            class="select-none mb-3 bg-white rounded-lg border border-gray-200 hover:border-red-300 transition-all duration-200"
          >
            <div class="flex items-center p-3">
              <!-- Product Image -->
              <div class="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                <img
                  v-if="item.image"
                  :src="item.image"
                  :alt="item.item_name"
                  class="w-full h-full object-cover"
                />
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>

              <!-- Product Info -->
              <div class="flex-1 ml-3">
                <h3 class="font-semibold text-gray-800 text-sm">{{ item.item_name }}</h3>
                <p class="text-xs text-gray-500">{{ formatPrice(item.rate) }} each</p>
                <p class="text-xs text-red-600 font-medium mt-1">
                  Returning: {{ item.returnQuantity }} / {{ item.originalQuantity }}
                </p>
              </div>

              <!-- Quantity Controls -->
              <div class="flex items-center gap-2">
                <button
                  @click="decreaseReturnQuantity(item.item_code)"
                  class="w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
                  :disabled="item.returnQuantity <= 1"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                  </svg>
                </button>

                <input
                  type="number"
                  :value="item.returnQuantity"
                  @input="updateReturnQuantity(item.item_code, $event.target.value)"
                  class="w-16 h-8 text-center border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  :max="item.originalQuantity"
                  min="1"
                />

                <button
                  @click="increaseReturnQuantity(item.item_code)"
                  class="w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
                  :disabled="item.returnQuantity >= item.originalQuantity"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </button>
              </div>

              <!-- Remove Button -->
              <button
                @click="removeReturnItem(item.item_code)"
                class="ml-3 text-red-500 hover:text-red-700 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Return Subtotal -->
            <div class="px-3 pb-3 flex justify-between text-sm">
              <span class="text-gray-600">Return Amount:</span>
              <span class="font-semibold text-red-600">{{ formatPrice(item.rate * item.returnQuantity) }}</span>
            </div>
          </div>
        </transition-group>
      </div>
    </div>

    <!-- Return Summary & Actions -->
    <div v-if="returnItems.length > 0" class="border-t border-gray-200 p-4">
      <!-- Return Summary -->
      <div class="space-y-2 mb-4">
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">Items to Return:</span>
          <span class="font-semibold">{{ totalReturnItems }}</span>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">Subtotal:</span>
          <span class="font-semibold">{{ formatPrice(returnSubtotal) }}</span>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">Tax ({{ taxRate }}%):</span>
          <span class="font-semibold">{{ formatPrice(returnTax) }}</span>
        </div>
        <div class="flex justify-between text-lg font-bold text-red-600 pt-2 border-t border-gray-200">
          <span>Total Refund:</span>
          <span>{{ formatPrice(totalRefund) }}</span>
        </div>
      </div>

      <!-- Return Reason -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Return Reason <span class="text-red-500">*</span>
        </label>
        <select
          v-model="returnReason"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
          required
        >
          <option value="">Select a reason</option>
          <option value="defective">Defective Product</option>
          <option value="wrong_item">Wrong Item</option>
          <option value="customer_request">Customer Request</option>
          <option value="damaged">Damaged</option>
          <option value="expired">Expired</option>
          <option value="other">Other</option>
        </select>
      </div>

      <!-- Notes -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Notes (Optional)
        </label>
        <textarea
          v-model="returnNotes"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
          rows="2"
          placeholder="Additional notes..."
        ></textarea>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-2">
        <button
          @click="handleCancelReturn"
          class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 rounded-xl transition-colors duration-200"
          :disabled="isProcessing"
        >
          Cancel
        </button>
        <button
          @click="handleProcessReturn"
          class="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-xl transition-colors duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
          :disabled="!canProcessReturn || isProcessing"
        >
          {{ isProcessing ? 'Processing...' : 'Process Return' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { formatPrice } from '../../utils/formatters';
import { useConfirm } from '@/composables/useConfirm'

const { confirm } = useConfirm()

const props = defineProps( {
    invoiceNo: {
      type: String,
      default: ''
    },
    taxRate: {
      type: Number,
      default: 10
    }
})
const emit = defineEmits(['return-processed', 'return-cancelled'])


const returnItems = ref([])
const returnReason = ref('')
const returnNotes = ref('')
const isProcessing = ref(false)

// Computed properties
const totalReturnItems = computed(() => {
  return returnItems.value.reduce((sum, item) => sum + item.returnQuantity, 0)
})

const returnSubtotal = computed(() => {
  return returnItems.value.reduce((sum, item) => sum + (item.rate * item.returnQuantity), 0)
})

const returnTax = computed(() => {
  return returnSubtotal.value * (props.taxRate / 100)
})

const totalRefund = computed(() => {
  return returnSubtotal.value + returnTax.value
})

const canProcessReturn = computed(() => {
  return returnItems.value.length > 0 && returnReason.value !== '' && !isProcessing.value
})

// Methods
const addReturnItem = (item) => {
  const existingItem = returnItems.value.find(i => i.item_code === item.item_code)
  if (existingItem) {
    if (existingItem.returnQuantity < existingItem.originalQuantity) {
      existingItem.returnQuantity++
    }
  } else {
    returnItems.value.push({
      ...item,
      returnQuantity: 1,
      originalQuantity: item.quantity
    })
  }
}

const removeReturnItem = (item_code) => {
  returnItems.value = returnItems.value.filter(item => item.item_code !== item_code)
}

const updateReturnQuantity = (item_code, quantity) => {
  const item = returnItems.value.find(i => i.item_code === item_code)
  if (item) {
    const newQty = parseInt(quantity) || 1
    item.returnQuantity = Math.max(1, Math.min(newQty, item.originalQuantity))
  }
}

const increaseReturnQuantity = (item_code) => {
  const item = returnItems.value.find(i => i.item_code === item_code)
  if (item && item.returnQuantity < item.originalQuantity) {
    item.returnQuantity++
  }
}

const decreaseReturnQuantity = (item_code) => {
  const item = returnItems.value.find(i => i.item_code === item_code)
  if (item && item.returnQuantity > 1) {
    item.returnQuantity--
  }
}

const handleClearReturn = async () => {
    const confirmed = await confirm({
        type: 'delete',
        title: 'Clear Return Items',
        message: 'Are you sure you want to clear all return items?',
        confirmLabel: 'Clear',
      })
      if (!confirmed) return
    returnItems.value = []
    returnReason.value = ''
    returnNotes.value = ''

}

const handleCancelReturn = async () => {
  const confirmed = await confirm({
      type: 'delete',
      title: 'Cancel Return',
      message: 'Are you sure you want to cancel this return process?',
      confirmLabel: 'Cancel',
    })
    returnItems.value = []
    returnReason.value = ''
    returnNotes.value = ''
    emit('return-cancelled')

}

const handleProcessReturn = async () => {
  if (!canProcessReturn.value) return

  isProcessing.value = true

  try {
    const returnData = {
      invoiceNo: props.invoiceNo,
      items: returnItems.value.map(item => ({
        item_code: item.item_code,
        item_name: item.item_name,
        rate: item.rate,
        originalQuantity: item.originalQuantity,
        returnQuantity: item.returnQuantity,
        returnAmount: item.rate * item.returnQuantity
      })),
      reason: returnReason.value,
      notes: returnNotes.value,
      subtotal: returnSubtotal.value,
      tax: returnTax.value,
      totalRefund: totalRefund.value,
      processedAt: new Date().toISOString()
    }

    emit('return-processed', returnData)

    // Reset form
    returnItems.value = []
    returnReason.value = ''
    returnNotes.value = ''
  } catch (error) {
    console.error('Return processing failed:', error)
    window.$toast?.error('Failed to process return. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const loadInvoiceItems = (items) => {
  returnItems.value = items.map(item => ({
    ...item,
    returnQuantity: item.quantity,
    originalQuantity: item.quantity
  }))
}


</script>

<style scoped>
.return-item-enter-active,
.return-item-leave-active {
  transition: all 0.3s ease;
}

.return-item-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.return-item-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Hide spinner buttons on number input */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style>
