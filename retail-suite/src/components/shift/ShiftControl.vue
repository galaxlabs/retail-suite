<!-- ShiftControl.vue -->
<template>
  <div class="container-navbar">
    <div class="w-full mx-auto px-4 sm:px-6 lg:px-10">
      <div class="grid grid-cols-4 h-16">
        <!-- Shift Status Left Section -->
        <div class="col-span-3 flex items-center justify-center space-x-4">
          <!-- Shift Status Indicator -->
          <div class="flex items-center">
            <div class="relative">
              <div
                class="w-3 h-3 rounded-full"
                :class="shiftStore.isShiftOpen ? 'bg-green-500' : 'bg-gray-400'"
              />
              <div
                v-if="shiftStore.isShiftOpen"
                class="absolute inset-0 w-3 h-3 bg-green-500 rounded-full animate-ping opacity-75"
              />
            </div>
            <span class="ml-2 text-sm font-medium" style="color: var(--text-secondary)">
              {{ shiftStore.isShiftOpen ? 'Shift Active' : 'No Active Shift' }}
            </span>
          </div>

          <!-- Current Shift Info -->
          <div
            v-if="shiftStore.isShiftOpen && currentShift"
            class="hidden sm:flex items-center space-x-6 text-sm"
            style="color: var(--text-secondary)"
          >
            <div class="flex items-center">
              <UserIcon class="w-4 h-4 mr-1" />
              <span>{{ currentShift.user }}</span>
            </div>
            <div class="flex items-center">
              <ClockIcon class="w-4 h-4 mr-1" />
              <span>{{ shiftDuration }}</span>
            </div>
            <div class="flex items-center">
              <ReceiptIcon class="w-4 h-4 mr-1" />
              <span>{{ currentShift.transactions.length || 0 }} transactions</span>
            </div>
            <div class="flex items-center">
              <CashIcon class="w-7 h-[1.37rem] mr-1" />
              <span class="font-medium text-green-600">{{ formatPrice(currentShift.totalSales || 0) }}</span>
            </div>
          </div>
        </div>

        <!-- Right Section - 25% -->
        <div class="col-span-1 flex items-center justify-center gap-1">
            <!-- Draft Invoices -->
            <button
              v-if="shiftStore.isShiftOpen"
              @click="openDraftModal"
              class="w-8 h-8 flex items-center justify-center rounded-lg transition-all duration-200 hover:scale-110"
              title="Draft Invoices"
            >
              <FileText
                class="w-5 h-5"
                :style="{
                  color: draftInvoicesCount > 0
                    ? primaryColor
                    : '#6b7280'
                }"
              />
            </button>


          <!-- Shift Info -->
          <button v-if="shiftStore.isShiftOpen" @click="showShiftInfo = true"
            class="w-8 h-8 flex items-center justify-center rounded-lg transition-all duration-200 hover:scale-110"
            title="Shift Info">
            <Coins class="w-5 h-5" :style="{ color: showShiftInfo ? '#8b5cf6' : '#6b7280' }" />
          </button>

          <!-- Mobile Scanner -->
          <button @click="openScanner"
            class="w-8 h-8 flex items-center justify-center rounded-lg transition-all duration-200 hover:scale-110"
            title="Mobile Scanner">
            <BarcodeScannerIcon class="w-5 h-5"
              :style="{ color: showScanner ? '#8b5cf6' : '#6b7280' }" />
          </button>

          <!-- Close Shift -->
          <button v-if="shiftStore.isShiftOpen" @click="showCloseShiftModal = true"
            class="w-8 h-8 flex items-center justify-center rounded-lg transition-all duration-200 hover:scale-110 group"
            title="Close Shift">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
              stroke-linecap="round" class="w-5 h-5 transition-colors duration-200 group-hover:text-red-500"
              :style="{ color: showCloseShiftModal ? 'red' : '#6b7280' }">
              <path d="M18.36 6.64a9 9 0 1 1-12.73 0" />
              <line x1="12" y1="2" x2="12" y2="12" />
            </svg>
          </button>

          <!-- Theme Toggle -->
          <button @click="toggleTheme"
            class="w-8 h-8 flex items-center justify-center rounded-lg transition-all duration-200 hover:scale-110"
            :style="{ color: isDark ? '#facc15' : '#6b7280' }"
            title="Toggle Theme">
            <svg v-if="isDark" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" />
            </svg>
          </button>

          <!-- Wifi -->
          <button v-if="shiftStore.isShiftOpen" @click="showWifiModal = true"
            class="w-8 h-8 flex items-center justify-center rounded-lg transition-all duration-200 hover:scale-110"
            title="Wifi">
            <Wifi class="w-5 h-5" :style="{ color: wificonnected === 'connected' ? primaryColor : '#6b7280' }" />
          </button>

          <!-- Divider -->
          <div class="h-5 w-px mx-1" style="background: var(--item-border)" />

          <!-- Avatar -->
          <div v-if="shiftStore.isShiftOpen" class="cursor-pointer hover:scale-110 transition-all duration-200">
            <img :src="userAvatar" :alt="userName" class="w-7 h-7 rounded-full object-cover ring-2"
              :style="{ ringColor: primaryColor }" />
          </div>

        </div>

      </div>
    </div>

    <!-- Modals -->
    <OpenShiftModal
      v-if="showOpenShiftModal"
      @close="showOpenShiftModal = false"
      @success="handleShiftOpened"
      @error="handleShiftError"
    />

    <CloseShiftModal
      v-if="showCloseShiftModal"
      @close="showCloseShiftModal = false"
      @success="handleShiftClosed"
      @error="handleShiftError"
    />

    <ShiftInfoModal
      v-if="showShiftInfo"
      :shift="currentShift"
      @close="showShiftInfo = false"
    />
    <ScanQRModal
      v-if="showScanner"
      :session-id="sessionId"
      :url="getScannerUrl()"
      @close="showScanner = false"
    />
    <!-- DroidCam Toast Notification -->
    <Transition name="fade">
      <div
        v-if="showDroidCamNotification"
        class="fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg transition-all duration-300"
        :class="[
          droidcamNotificationStatus === 'success'
            ? 'bg-green-500 text-white'
            : droidcamNotificationStatus === 'error'
            ? 'bg-red-500 text-white'
            : 'bg-blue-500 text-white'
        ]"
      >
        <div class="flex items-center">
          <span v-if="droidcamNotificationStatus === 'success'" class="mr-2">✓</span>
          <span v-if="droidcamNotificationStatus === 'error'" class="mr-2">✕</span>
          <span v-if="droidcamNotificationStatus === 'connecting'" class="mr-2">⟳</span>
          <span>{{ droidcamNotificationMessage }}</span>
        </div>
      </div>
    </Transition>

    <DraftInvoicesModal
      v-model="showDraftInvoicesModal"
      :draft-invoices="draftInvoices"
      :is-loading="isDraftLoading"
      @open-invoice="handleOpenDraftInvoice"
      @delete-draft="(name) => { /* delete logic */ }"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Coins, Wifi, FileText } from 'lucide-vue-next'
import { useShiftStore } from '@/stores/shift'
import OpenShiftModal from '@/components/modals/OpenShiftModal.vue'
import CloseShiftModal from '@/components/modals/CloseShiftModal.vue'
import ShiftInfoModal from '@/components/modals/ShiftInfoModal.vue'
import DraftInvoicesModal from '@/components/modals/DraftInvoicesModal.vue'
import { formatDuration, formatPrice } from '../../utils/formatters'
import { get_shift_summary } from '../../composables/shift'
import eventBus from '../../utils/eventBus'
import { useDroidCamClient } from '@/services/barcodeWebSocketClient'
import UserIcon   from '@/components/icons/UserIcon.svg'
import ClockIcon    from '@/components/icons/ClockIcon.svg'
import ReceiptIcon            from '@/components/icons/ReceiptIcon.svg'
import CashIcon               from '@/components/icons/CashIcon.svg'
import InfoIcon               from '@/components/icons/InfoIcon.svg'
import PlayIcon               from '@/components/icons/PlayIcon.svg'
import BarcodeScannerIcon     from '@/components/icons/BarcodeScanner.svg'
import { useSettingsStore }   from '@/stores/settings.js'
import { useInvoicesStore }   from '@/stores/invoices'
import { useCartStore }       from '@/stores/cart'
import { useMobileScanSession } from '@/services/useMobileScanSession'
import ScanQRModal from '@/components/modals/ScanQRModal.vue'


// Stores
const cartStore = useCartStore()
const shiftStore = useShiftStore()
const settingsStore = useSettingsStore()
const invoicesStore = useInvoicesStore()
const {sessionId, getScannerUrl, startListening} = useMobileScanSession()

const emit = defineEmits(['shift-opened', 'shift-closed', 'shift-error'])


const showScanner = ref(false)
// Shift Modals
const showOpenShiftModal = ref(false)
const showCloseShiftModal = ref(false)
const showShiftInfo = ref(false)
const shiftDuration = ref('')
// DroidCam State
const isDroidCamConnecting = ref(false)
const showDroidCamNotification = ref(false)
const droidcamNotificationMessage = ref('')
const droidcamNotificationStatus = ref('connecting') // 'connecting', 'success', 'error'

let notificationTimeout = null
let durationInterval = null
let wifiInterval = null

const showDraftInvoicesModal = ref(false)
const draftInvoices = ref([])
const isDraftLoading = ref(false)

const draftInvoicesCount = computed(() => draftInvoices.value.length)

const openDraftModal = async () => {
  showDraftInvoicesModal.value = true
  isDraftLoading.value = true
  console.log('currentShift', currentShift.value.name)
  draftInvoices.value = await invoicesStore.loadDraftInvoices(currentShift.value.name)
  isDraftLoading.value = false
}



const wificonnected = ref('disconnected')
const checkInternetConnection = async () => {
  if (!navigator.onLine) {
    wificonnected.value = 'disconnected'
    return
  }

  try {
    await fetch('https://1.1.1.1/cdn-cgi/trace', {
      method: 'GET',
      cache: 'no-cache',
      signal: AbortSignal.timeout(3000),
    })
    wificonnected.value = 'connected'
  } catch {
    wificonnected.value = 'disconnected'
  }
}



const userAvatar = ref('https://ui-avatars.com/api/?name=Ahmed+Reda&background=0D8ABC&color=fff')
const userName = computed(() => shiftStore.userName)

// DroidCam Composable
const {
isConnected: isDroidCamConnected,
connectionStatus,
droidcamIP,
connectToDroidCam,
disconnectDroidCam
} = useDroidCamClient()


const openScanner = () => {
  showScanner.value = true
  startListening()
}


const currentShift = computed(() => shiftStore.currentShift)

// theme
const isDark = computed(() => settingsStore.settings.appearance.theme === 'dark')
const primaryColor = computed(() => {
  return settingsStore.settings.value?.appearance?.primaryColor || '#06b6d4';
})

const handleDroidCamConnect = async () => {
  if (isDroidCamConnected.value) {
    // قطع الاتصال
    isDroidCamConnecting.value = true
    await disconnectDroidCam()
    isDroidCamConnecting.value = false

    showNotification('DroidCam Disconnected', 'success')
  } else {
    // الاتصال
    isDroidCamConnecting.value = true

    try {
      showNotification('Connecting to DroidCam...', 'connecting')

      // استخدم IP سے المتغير أو القيمة پہلے سے طے شدہة
      const ipAddress = droidcamIP.value || '192.168.8.15'

      await connectToDroidCam(ipAddress, 4747)

      if (isDroidCamConnected.value) {
        showNotification(`Connected to DroidCam (${ipAddress})`, 'success')

        // استقبال أحداث الباركود
        window.addEventListener('barcode-scanned', handleBarcodeScanned)
      } else {
        showNotification('Failed to connect to DroidCam', 'error')
      }
    } catch (error) {
      console.error('DroidCam connection error:', error)
      showNotification(`Connection failed: ${error.message}`, 'error')
    } finally {
      isDroidCamConnecting.value = false
    }
  }
}


const handleBarcodeScanned = (event) => {
    console.log(`📦 Barcode Scanned function 2`)
  const { barcode, timestamp } = event.detail
  console.log(`📦 Barcode Scanned: ${barcode} at ${timestamp}`)

  // بث الحدث للـ components الأخرى
  eventBus.emit('barcode:scanned', {
    barcode,
    timestamp
  })
}

/**
 * دیکھیں إشعار DroidCam
 */
const showNotification = (message, status = 'connecting') => {
  droidcamNotificationMessage.value = message
  droidcamNotificationStatus.value = status
  showDroidCamNotification.value = true

  // إخفاء الإشعار بعد 3 ثواني
  if (notificationTimeout) clearTimeout(notificationTimeout)

  if (status === 'connecting') {
    // لا تخفي إشعار الاتصال تلقائياً
    return
  }

  notificationTimeout = setTimeout(() => {
    showDroidCamNotification.value = false
  }, 3000)
}

/**
 * اپ ڈیٹ کریں مدة Shift
 */
const updateShiftDuration = () => {
  if (shiftStore.isShiftOpen && currentShift.value) {
    const startTime = new Date(currentShift.value.period_start_date)
    const now = new Date()
    shiftDuration.value = formatDuration(startTime, now)
  } else {
    shiftDuration.value = ''
  }
}

const refreshShiftSummary = async () => {
  try {
    if (shiftStore.isShiftOpen && currentShift.value?.name) {
      const summary = await get_shift_summary({ name: currentShift.value.name })
      shiftStore.currentShift.totalSales = summary.total_sales || 0
      shiftStore.currentShift.transactions = summary.transactions || []
    }
  } catch (err) {
    console.error('Failed to refresh shift summary:', err)
  }
}

const handleShiftOpened = (shift) => {
  showOpenShiftModal.value = false
  emit('shift-opened', shift)
  if (window.$toast) {
    window.$toast.success(`Shift opened successfully for ${shift.userName}`)
  }
}

const handleShiftClosed = (shift) => {
  showCloseShiftModal.value = false
  emit('shift-closed', shift)
  if (window.$toast) {
    window.$toast.success('Shift closed successfully')
  }
}

const handleShiftError = (error) => {
  emit('shift-error', error)
  if (window.$toast) {
    window.$toast.error(error.message || 'Shift operation failed')
  }
}
const toggleTheme = () => {
  const newTheme = settingsStore.settings.appearance.theme === 'dark' ? 'light' : 'dark'
  settingsStore.settings.appearance.theme = newTheme
  applyTheme(newTheme)
}
const applyTheme = (theme) => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// في ShiftControl.vue
const handleOpenDraftInvoice = (invoiceName) => {
  const invoice = draftInvoices.value.find(inv => inv.name === invoiceName)
  if (!invoice) return

  cartStore.loadDraftInvoice(invoice)
  showDraftInvoicesModal.value = false
}

onMounted(() => {

  checkInternetConnection()
  window.addEventListener('online', checkInternetConnection)
  window.addEventListener('offline', checkInternetConnection)
  wifiInterval = setInterval(checkInternetConnection, 10000)


  updateShiftDuration()
  durationInterval = setInterval(updateShiftDuration, 1000)
  eventBus.on('invoice:created', refreshShiftSummary)

  // الاستماع لأحداث DroidCam
  window.addEventListener('droidcam-connected', () => {
    console.log('✅ DroidCam connected')
  })

  window.addEventListener('droidcam-disconnected', () => {
    console.log('❌ DroidCam disconnected')
  })
})

onUnmounted(() => {

  window.removeEventListener('online', checkInternetConnection)
  window.removeEventListener('offline', checkInternetConnection)
  clearInterval(wifiInterval)

  if (durationInterval) clearInterval(durationInterval)
  if (notificationTimeout) clearTimeout(notificationTimeout)

  eventBus.off('invoice:created', refreshShiftSummary)

  window.removeEventListener('barcode-scanned', handleBarcodeScanned)
  window.removeEventListener('droidcam-connected', null)
  window.removeEventListener('droidcam-disconnected', null)

  // قطع الاتصال عند غلق الـ component
  if (isDroidCamConnected.value) {
    disconnectDroidCam()
  }



})

</script>

<style scoped>
.container-navbar {
  background: var(--nav-bg);
  border-bottom: 1px solid var(--card-border);
}

/* Animations */
@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-ping {
  animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Button Styles */
button {
  transition: all 0.2s ease;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
}

button:active:not(:disabled) {
  transform: translateY(0);
}

button:disabled {
  cursor: not-allowed;
}
/* Responsive */
@media (max-width: 640px) {
  .space-x-5 > * + * {
    margin-left: 0.75rem;
  }
}
</style>
