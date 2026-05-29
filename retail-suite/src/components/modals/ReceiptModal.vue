<template>
  <div class="fixed w-full h-screen left-0 top-0 z-50 flex flex-wrap justify-center content-center p-4 md:p-24">
    <!-- Background Overlay -->
    <transition
      name="overlay"
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
    <div
      class="fixed w-full h-screen left-0 top-0 z-0 bg-opacity-50"
      @click="handleBackgroundClick"
      />
    </transition>

    <!-- Modal Content -->
    <transition
      name="modal"
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0 transform scale-90"
      enter-to-class="opacity-100 transform scale-100"
      leave-active-class="transition ease-in duration-300"
      leave-from-class="opacity-100 transform scale-100"
      leave-to-class="opacity-0 transform scale-90"
    >
      <div class="w-full max-w-md rounded-3xl bg-white shadow-2xl overflow-hidden z-10 mx-auto relative">
        <!-- Receipt Content -->
        <div
          id="receipt-content"
          ref="receiptContent"
          class="text-left w-full text-sm p-6 overflow-auto max-h-96"
        >
          <!-- Receipt Header -->
          <div class="text-center mb-4">
            <img
              :src="resolvedLogo"
              :alt="storeName"
              class="mb-3 w-8 h-8 inline-block"
              @error="handleLogoError"
            />
            <div v-if="logoError" class="mb-3 w-8 h-8 inline-block">
              <ReceiptLogoIcon class="w-8 h-8 text-cyan-600" />
            </div>
            <h2 class="text-xl font-semibold text-gray-800">{{ storeName }}</h2>
            <p class="text-gray-600 text-sm">{{ storeAddress }}</p>
          </div>

          <!-- Receipt Info -->
          <div class="flex mt-4 text-xs text-gray-600 border-b pb-2 mb-4">
            <div class="flex-grow">
              <!-- {{ receiptData }} -->
              <span class="font-semibold">No:</span> {{ receiptData?.invoiceNo || generateReceiptNo() }}
            </div>
            <div>{{ formatDate(receiptData?.timestamp) }}</div>
          </div>

          <!-- Items Table -->
          <div class="mb-4">
            <table class="w-full text-xs">
              <thead>
                <tr class="border-b">
                  <th class="py-1 w-1/12 text-center">#</th>
                  <th class="py-1 text-left">Item</th>
                  <th class="py-1 w-2/12 text-center">Qty</th>
                  <th class="py-1 w-3/12 text-right">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, index) in receiptData?.items || []"
                  :key="item.item_code"
                  class="border-b border-gray-100"
                >
                  <td class="py-2 text-center text-gray-500">{{ index + 1 }}</td>
                  <td class="py-2 text-left">
                    <div class="font-medium">{{ item.item_name }}</div>
                    <small class="text-gray-500">{{ formatPrice(item.rate) }}</small>
                  </td>
                  <td class="py-2 text-center">{{ item.qty }}</td>
                  <td class="py-2 text-right font-medium">{{ formatPrice(item.qty * item.rate) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Summary -->
          <div class="border-t pt-4">
            <div class="space-y-2">
              <!-- Subtotal -->
              <div class="flex justify-between text-sm">
                <span>Subtotal:</span>
                <span>{{ formatPrice(summary?.subtotal || 0) }}</span>
              </div>

              <!-- Tax (if applicable) -->
              <div v-if="summary?.tax > 0" class="flex justify-between text-sm">
                <span>Tax:</span>
                <span>{{ formatPrice(summary.tax) }}</span>
              </div>

              <!-- Discount (if applicable) -->
              <div v-if="summary?.discount > 0" class="flex justify-between text-sm text-green-600">
                <span>Discount:</span>
                <span>-{{ formatPrice(summary.discount) }}</span>
              </div>

              <!-- Total -->
              <div class="flex justify-between font-semibold text-base border-t pt-2">
                <span>TOTAL:</span>
                <span>{{ formatPrice(summary?.total || 0) }}</span>
              </div>

              <!-- Payment Info -->
              <div class="flex justify-between text-sm border-t pt-2">
                <span>Cash:</span>
                <span>{{ formatPrice(summary?.cash || 0) }}</span>
              </div>

              <div class="flex justify-between text-sm font-medium">
                <span>Change:</span>
                <span class="text-green-600">{{ formatPrice(summary?.change || 0) }}</span>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="text-center mt-6 pt-4 border-t text-xs text-gray-500">
            <p>Thank you for your visit!</p>
            <p class="mt-1">{{ getCurrentDateTime() }}</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="p-4 w-full bg-gray-50 border-t">
          <div class="flex space-x-3">
            <!-- Print Button -->
            <button
              class="flex-1 bg-cyan-500 text-white text-lg px-4 py-3 rounded-2xl focus:outline-none hover:bg-cyan-600 transition-colors duration-200 flex items-center justify-center"
              @click="handlePrint"
              :disabled="isProcessing"
            >
              <PrintIcon class="w-5 h-5 mr-2" />
              {{ isProcessing ? 'Printing...' : 'Print' }}
            </button>

            <!-- Proceed Button -->
            <button
              v-if="!props.receiptData?.isFastMode"
              class="flex-1 bg-green-500 text-white text-lg px-4 py-3 rounded-2xl focus:outline-none hover:bg-green-600 transition-colors duration-200 flex items-center justify-center"
              @click="handleProceed"
              :disabled="isProcessing"
            >
              <CheckIcon class="w-5 h-5 mr-2" />
              Proceed
            </button>
          </div>

          <!-- Alternative Actions -->
          <div class="flex justify-center mt-3 space-x-4">
            <button
              class="text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200"
              @click="handleEmailReceipt"
              :disabled="isProcessing"
            >
              Email Receipt
            </button>
            <button
              class="text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200"
              @click="handleSaveReceipt"
              :disabled="isProcessing"
            >
              Save Copy
            </button>
          </div>
        </div>

        <!-- Close Button -->
       <button
          class="absolute top-4 right-4 z-50 text-gray-400 hover:text-gray-600 focus:outline-none p-1 rounded-full hover:bg-gray-100 transition-colors duration-200"
          @click="handleClose"
          :disabled="isProcessing"
        >
          <CloseIcon class="w-5 h-5 text-black" />
        </button>

      </div>
    </transition>
  </div>

  <!-- Invoice Template -->
  <div class="hidden">
    <invoiceTemplate
    ref="invoiceTemplateRef"
    :invoiceNo="props.receiptData?.invoiceNo"
    :items="props.receiptData?.items"
    :summary="props.receiptData?.summary"
  />
  </div>
  <!-- Hidden Print Area -->
  <div id="print-area" class="print-area hidden">
    <div v-html="printContent"></div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { printReceipt } from '@/services/printer'
import { formatPrice } from '../../utils/formatters';
import ReceiptLogoIcon from '@/components/icons/ReceiptLogoIcon.svg'
import PrintIcon from '@/components/icons/PrintIcon.svg'
import CheckIcon from '@/components/icons/CheckIcon.svg'
import CloseIcon from '@/components/icons/CloseIcon.svg'
import invoiceTemplate from './invoiceTemplate.vue';
import config from '@/config/frappe'
import defaultLogo from '@/assets/img/receipt-logo.png';
const props = defineProps({
    receiptData: {
      type: Object,
      default: () => ({})
    },
    storeName: {
      type: String,
      default: ''
    },
    storeAddress: {
      type: String,
      default: ''
    },
    autoShow: {
      type: Boolean,
      default: true
    },
    storeLogo: {
      type: String,
      default: ""
    },
     isFastMode: {
      type: Boolean,
      default: false
    }
})
const emit = defineEmits(['close', 'proceed', 'print', 'email', 'save'])

const invoiceTemplateRef = ref(null)



const receiptContent = ref(null)
    const isProcessing = ref(false)
    const logoError = ref(false)

    // Computed properties
    const summary = computed(() => props.receiptData?.summary || {})

    // Resolve logo URL - prepend FRAPPE_URL for relative paths
    const resolvedLogo = computed(() => {
      const logo = props.storeLogo
      if (!logo) return defaultLogo
      if (logo.startsWith('http')) return logo
      if (logo.startsWith('/')) return config.FRAPPE_URL + logo
      return logo
    })

    const printContent = computed(() => {
      if (!receiptContent.value) return ''
      return receiptContent.value.innerHTML
    })
    // Format date
    const formatDate = (timestamp) => {
      if (!timestamp) return new Date().toLocaleString('id-ID')
      return new Date(timestamp).toLocaleString('id-ID')
    }

    // Get current date time
    const getCurrentDateTime = () => {
      return new Date().toLocaleString('id-ID')
    }

    // Generate receipt number
    const generateReceiptNo = () => {
      const now = new Date()
      const timestamp = now.getTime().toString().slice(-6)
      return `TW${timestamp}`
    }

    // Handle logo error
    const handleLogoError = () => {
      logoError.value = true
    }

    // Handle background click
    const handleBackgroundClick = () => {
      if (!isProcessing.value) {
        handleClose()
      }
    }

    // Handle close
    const handleClose = () => {
      if (isProcessing.value) return
      emit('close')
    }

    // Handle email receipt
    const handleEmailReceipt = () => {
      if (isProcessing.value) return

      // This would typically open an email dialog or send to server
      const emailBody = `Receipt from ${props.storeName}\n\nTotal: ${formatPrice(summary.value.total)}\nDate: ${formatDate(props.receiptData?.timestamp)}`
      const emailSubject = `Receipt #${props.receiptData?.receiptNo || generateReceiptNo()}`
      const mailtoLink = `mailto:?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`

      window.open(mailtoLink)
      emit('email', props.receiptData)
    }

    // Handle save receipt
    const isSaved = ref(false)  // هل اتمحفوظ کریںت في Frappe
    const savedInvoiceName = ref(null)  // الـ name بتاع الـ draft

      const handleSaveReceipt = async () => {
        if (isProcessing.value) return
        isProcessing.value = true
        try {
          const result = await emit('save', props.receiptData)
          isSaved.value = true
          savedInvoiceName.value = result?.name
          // تحميل نسخة نصية
          const receiptText = generateReceiptText()
          const blob = new Blob([receiptText], { type: 'text/plain' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `receipt_${props.receiptData?.invoiceNo || generateReceiptNo()}.txt`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
        } catch (error) {
          console.error('Save failed:', error)
          window.$toast?.error('Save failed. Please try again.')
        } finally {
          isProcessing.value = false
        }
      }

      const handlePrint = async () => {
        if (isProcessing.value) return

        if (!props.receiptData?.isSaved) {
          window.$toast?.warning('پرنٹ سے پہلے براہِ کرم انوائس محفوظ کریں۔')
          return
        }

        try {
          isProcessing.value = true
          await nextTick()

          const printResult = await printReceipt(props.receiptData, { force: false })
          if (printResult?.skipped) {
            await invoiceTemplateRef.value?.print()
          }
        } catch (error) {
          console.error('Print failed:', error)
          window.$toast?.error('پرنٹ ناکام ہوگیا۔ براہِ کرم دوبارہ کوشش کریں۔')
        } finally {
          setTimeout(() => {
            isProcessing.value = false
          }, 1000)
        }
      }

      const handleProceed = () => {
        if (isProcessing.value) return
        emit('proceed', { ...props.receiptData, savedInvoiceName: savedInvoiceName.value })
      }

    // Generate receipt text for saving
    const generateReceiptText = () => {
      const lines = []
      lines.push(`${props.storeName}`)
      lines.push(`${props.storeAddress}`)
      lines.push(``)
      lines.push(`Subtotal: ${formatPrice(summary.value.subtotal)}`)
      if (summary.value.tax > 0) {
        lines.push(`Tax: ${formatPrice(summary.value.tax)}`)
      }
      if (summary.value.discount > 0) {
        lines.push(`Discount: -${formatPrice(summary.value.discount)}`)
      }
      lines.push(`Total: ${formatPrice(summary.value.total)}`)
      lines.push(`Cash: ${formatPrice(summary.value.cash)}`)
      lines.push(`Change: ${formatPrice(summary.value.change)}`)
      lines.push(``)
      lines.push(`Thank you for your visit!`)

      return lines.join('\n')
    }

    // Handle escape key
    const handleEscape = (event) => {
      if (event.key === 'Escape' && !isProcessing.value) {
        handleClose()
      }
    }

    // Lifecycle
    onMounted(() => {
      document.addEventListener('keydown', handleEscape)
    })

</script>

<style scoped>

</style>
