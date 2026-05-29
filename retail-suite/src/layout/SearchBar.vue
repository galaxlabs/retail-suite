<template>
  <div class="sticky top-0 z-10 flex px-2 flex-row gap-2">
    <!-- Status Display -->
    <div v-if="lastBarcode" class="barcode-display">
      <h3>Last Barcode:</h3>
      <p>{{ lastBarcode }}</p>
    </div>

    <!-- Mode Toggle Button -->
    <div
      @click="switchToBarcode()"
      class="absolute left-5 top-3 px-2 py-2 rounded-full text-white z-10 transition-colors duration-200 cursor-pointer"
      :class="{
        'animate-pulse': qrBot.isConnected.value,
        'bg-cyan-500': !qrBot.isConnected.value && !isScannerConnected,
        'bg-blue-500': isScannerConnected && !qrBot.isConnected.value,
        'bg-red-500': isLoading
      }"
      :style="qrBot.isConnected.value ? { backgroundColor: primaryColor } : {}"
      :title="getStatusTitle()"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </div>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="absolute right-5 top-3 px-2 py-2">
      <div class="animate-spin h-6 w-6 border-2 border-cyan-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- Results Count -->
    <div
      v-else-if="showResultsCount && modelValue && resultsCount !== null && !isBarcodeMode"
      class="absolute right-5 top-2 bg-cyan-100 text-cyan-800 text-xs px-2 py-1 rounded-full"
    >
      {{ resultsCount }} {{ resultsCount === 1 ? 'result' : 'results' }}
    </div>

    <!-- Barcode Mode Indicator -->
    <div
      v-else-if="isBarcodeMode"
      class="absolute right-5 top-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full flex items-center gap-1 animate-pulse"
    >
      <span class="w-2 h-2 bg-green-600 rounded-full"></span>
      Scanner Mode
    </div>

    <!-- Clear Button -->
    <button
      v-if="modelValue && modelValue.length > 0"
      class="absolute right-5 top-3 p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
      @click="clearSearch"
      type="button"
      title="Clear search"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>

    <!-- UNIFIED INPUT - يعمل في الـ mode پیر -->
    <input
      ref="mainInput"
      type="text"
      :value="modelValue"
      class="rounded-3xl shadow text-lg w-full h-16 py-4 pl-16 pr-12 transition-all duration-300 focus:outline-none"
      :style="{
        backgroundColor: 'var(--input-bg)',
        color: 'var(--input-text)',
        borderColor: 'var(--input-border)',
        boxShadow: 'var(--input-shadow)',
      }"
      autocomplete="off"
      :placeholder="currentPlaceholder"
      @input="handleInput"
      @keydown="handleKeydown"
      @focus="handleFocus"
      @blur="handleBlur"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { useShiftStore } from '../stores/shift'
import { useSettingsStore } from '../stores/settings'
import { useCartStore } from '@/stores/cart'
import { getItemsFromFrappeDB } from '@/composables/pos'
import qrBot from '@/services/qrBot.js'


  const props = defineProps( {
      modelValue: {
        type: String,
        default: ''
    },
    placeholder: {
      type: String,
      default: 'Search by product name or barcode...'
    },
    showResultsCount: {
      type: Boolean,
      default: false
    },
    resultsCount: {
      type: Number,
      default: null
    },
    autofocus: {
      type: Boolean,
      default: true
    }
  })
  const emit = defineEmits(['update:modelValue', 'search', 'clear', 'enter', 'barcode-detected'])

    // ==========================================
    // ✅ States
    // ==========================================
    const mainInput = ref(null)
    const lastBarcode = ref(null)
    const isLoading = ref(false)
    const isBarcodeMode = ref(false)
    const barcodeBuffer = ref('')
    const lastInputTime = ref(0)
    const isProcessingBarcode = ref(false)

    // Scanner detection
    const keyPressTimings = ref([])
    const isScannerConnected = ref(false)
    const scannerConfidence = ref(0)

    // Stores
    const shiftStore = useShiftStore()
    const cartStore = useCartStore()
    const settingsStore = useSettingsStore()

    const settings = computed(() => settingsStore.settings)
    const primaryColor = computed(() => settings.value?.appearance?.primaryColor || '#06b6d4')

    // ==========================================
    // ✅ Computed Properties
    // ==========================================
    const currentPlaceholder = computed(() => {
      if (qrBot.isConnected.value) {
        return isScannerConnected.value
          ? 'Scan the barcode now...'
          : 'Use the scanner or type manually...'
      }
      return props.placeholder || 'Search by product name or barcode...'
    })


    // ==========================================
    // ✅ Handler Functions
    // ==========================================

    const getStatusTitle = () => {
      if (qrBot.isConnected.value) {
        return 'Scanner mode - ready'
      }
      return 'Manual search mode'
    }

    const switchToBarcode = () => {
      qrBot.isConnected.value = !qrBot.isConnected.value
      isBarcodeMode.value = !isBarcodeMode.value

      const state = qrBot.isConnected.value ? 'Scanner Mode' : 'Manual Mode'
      console.log(`🔄 Switched to: ${state}`)

      if (window.$toast) {
        if (qrBot.isConnected.value) {
          window.$toast.success('📱 Scanner Mode Activated')
        } else {
          window.$toast.info('⌨️ Manual Mode Activated')
        }
      }

      // Focus على الـ input
      nextTick(() => {
        if (mainInput.value) {
          mainInput.value.focus()
        }
      })
    }

    const updateScannerConfidence = () => {
      if (keyPressTimings.value.length < 5) return

      const timeDifferences = []
      for (let i = 1; i < keyPressTimings.value.length; i++) {
        timeDifferences.push(keyPressTimings.value[i] - keyPressTimings.value[i - 1])
      }

      const avgDifference = timeDifferences.reduce((a, b) => a + b, 0) / timeDifferences.length
      const variance = timeDifferences.reduce((a, b) => a + Math.pow(b - avgDifference, 2), 0) / timeDifferences.length

      if (avgDifference < 70 && variance < 400) {
        scannerConfidence.value = Math.min(100, Math.round((70 - avgDifference) * 3 - variance / 100))
        isScannerConnected.value = scannerConfidence.value > 60
      } else {
        scannerConfidence.value = Math.max(0, scannerConfidence.value - 10)
        isScannerConnected.value = false
      }

      console.log(`📊 Speed: ${Math.round(avgDifference)}ms, Confidence: ${scannerConfidence.value}%`)
    }

    const handleBarcodeDetected = async (barcodeData) => {
      if (isProcessingBarcode.value) return
      isProcessingBarcode.value = true
      isLoading.value = true

      try {
        const { barcode, detectedByScanner, source = 'scanner' } = barcodeData

        console.log('🔍 Processing barcode:', barcode)

        if (!shiftStore.isShiftOpen) {
          if (window.$toast) {
            window.$toast.warning('براہ کرم پہلے شفٹ کھولیں')
          }
          return
        }

        const response = await getItemsFromFrappeDB(
          shiftStore.pos_profile,
          shiftStore.pos_profile?.selling_price_list,
          null,
          barcode
        )

        if (response && response.length > 0) {
          const product = response[0]
          cartStore.addToCart(product)
          lastBarcode.value = barcode

          if (window.$toast) {
            window.$toast.success(`✅ ${product.item_name}`)
          }

          console.log('✅ Product found and added to cart:', product.item_name)
        } else {
          if (window.$toast) {
            window.$toast.error('Product ' + barcode + ' not found')
          }
        }
      } catch (error) {
        console.error('❌ Error processing barcode:', error)
        if (window.$toast) {
          window.$toast.error('Barcode processing error')
        }
      } finally {
        isLoading.value = false
        isProcessingBarcode.value = false
        // مسح الـ input بعد المعالجة
        emit('update:modelValue', '')
        barcodeBuffer.value = ''
      }
    }

    const handleInput = (event) => {
      const value = event.target.value
      emit('update:modelValue', value)

      // التحقق سے الباركود التلقائي
      const isBarcodePattern = /^\d{8,20}$/.test(value)

      if (qrBot.isConnected.value && isBarcodePattern) {
        console.log('📱 Barcode detected from input:', value)
        handleBarcodeDetected({
          barcode: value,
          detectedByScanner: true,
          source: 'manual_input'
        })
      }
    }

    const handleKeydown = async (event) => {
      const currentTime = Date.now()
      const timeSinceLastInput = currentTime - lastInputTime.value

      // سجّل توقيت الضغطة
      if (event.key.length === 1) {
        keyPressTimings.value.push(currentTime)
        if (keyPressTimings.value.length > 20) {
          keyPressTimings.value.shift()
        }
        updateScannerConfidence()
      }

      lastInputTime.value = currentTime

      // إذا Escape = امسح الـ input
      if (event.key === 'Escape') {
        emit('update:modelValue', '')
        barcodeBuffer.value = ''
        return
      }

      // إذا Enter = معالجة التلاش کریں أو الباركود
      if (event.key === 'Enter') {
        event.preventDefault()
        const value = event.target.value.trim()

        if (qrBot.isConnected.value && /^\d{8,20}$/.test(value)) {
          // معالجة كـ barcode
          await handleBarcodeDetected({
            barcode: value,
            detectedByScanner: isScannerConnected.value,
            source: 'scanner'
          })
        } else if (value.length >= 2) {
          // معالجة كـ search عادي
          emit('enter', value)
        }
      }

      // إذا تأخير كبير = مستخدم يكتب يدوياً
      if (timeSinceLastInput > 100 && event.key.length === 1) {
        barcodeBuffer.value = ''
      }
    }

    const handleFocus = () => {
      console.log('Input focused')
    }

    const handleBlur = () => {
      // Keep focus على الـ input
      // nextTick(() => {
      //   if (mainInput.value) {
      //     mainInput.value.focus()
      //   }
      // })
      return
    }

    const clearSearch = () => {
      emit('update:modelValue', '')
      emit('clear')
      barcodeBuffer.value = ''

      nextTick(() => {
        if (mainInput.value) {
          mainInput.value.focus()
        }
      })
    }

    const focus = () => {
      if (mainInput.value) {
        mainInput.value.focus()
      }
    }

    // ==========================================
    // ✅ Lifecycle
    // ==========================================
    onMounted(() => {
      console.log('🚀 SearchBar mounted')

      if (mainInput.value && props.autofocus) {
        nextTick(() => {
          mainInput.value.focus()
        })
      }

      // Listen to QRBot events
      qrBot.on('barcode', (data) => {
        console.log('📲 Received barcode from QRBot:', data.barcode)
        lastBarcode.value = data.barcode
        emit('update:modelValue', data.barcode)
        handleBarcodeDetected({
          barcode: data.barcode,
          detectedByScanner: true,
          source: 'iPhone_QRBot'
        })
      })
    })

    onUnmounted(() => {
      console.log('🛑 SearchBar unmounted')
      qrBot.off('barcode', null)
    })


</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
