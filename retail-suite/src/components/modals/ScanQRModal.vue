<!-- components/modals/ScanQRModal.vue -->
<!-- Desktop POS modal: shows QR code for cashier to scan with mobile device -->

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="$emit('close')"
    >
      <div
        class="relative rounded-2xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden"
        style="background: var(--card-bg); border: 1px solid var(--card-border);"
      >
        <!-- Header -->
        <div
          class="flex items-center justify-between px-5 py-4"
          style="border-bottom: 1px solid var(--card-border);"
        >
          <div class="flex items-center gap-2">
            <!-- Animated scan icon -->
            <div class="relative w-8 h-8 flex items-center justify-center rounded-lg"
              style="background: var(--primary-50, #ecfeff);"
            >
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none"
                style="color: var(--primary-600, #0891b2);"
                stroke="currentColor" stroke-width="2"
              >
                <path d="M3 5h2M7 5h1M3 5v2M21 5h-2M17 5h-1M21 5v2M3 19h2M7 19h1M3 19v-2M21 19h-2M17 19h-1M21 19v-2"/>
                <rect x="7" y="7" width="4" height="4" rx="0.5"/>
                <rect x="13" y="7" width="4" height="4" rx="0.5"/>
                <rect x="7" y="13" width="4" height="4" rx="0.5"/>
                <path d="M13 13h1M16 13h1M13 16h4"/>
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-semibold" style="color: var(--text-main);">Mobile Scanner</h3>
              <p class="text-xs" style="color: var(--text-muted);">Scan QR with your phone</p>
            </div>
          </div>
          <button
            @click="$emit('close')"
            class="w-7 h-7 flex items-center justify-center rounded-full transition-colors"
            style="background: var(--card-border); color: var(--text-muted);"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- QR Code Area -->
        <div class="flex flex-col items-center px-6 py-6 gap-4">

          <!-- Status pill -->
          <div
            class="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium"
            :style="isListening
              ? 'background:#dcfce7; color:#16a34a;'
              : 'background:#fef9c3; color:#ca8a04;'"
          >
            <div
              class="w-2 h-2 rounded-full"
              :class="isListening ? 'bg-green-500 animate-pulse' : 'bg-yellow-400'"
            />
            {{ isListening ? 'Listening for barcodes…' : 'Initializing…' }}
          </div>

          <!-- QR Code container -->
          <div
            class="relative rounded-xl p-3"
            style="background: #fff; border: 1px solid var(--card-border);"
          >
            <!-- QR rendered here by qrcode.js -->
            <canvas ref="qrCanvas" class="block" />

            <!-- Scan line animation overlay -->
            <div class="absolute inset-3 overflow-hidden rounded-lg pointer-events-none">
              <div class="scan-line" />
            </div>
          </div>

          <!-- Session ID + URL -->
          <div class="w-full">
            <p class="text-xs text-center mb-1" style="color: var(--text-muted);">
              Session ID
            </p>
            <div
              class="flex items-center gap-2 px-3 py-2 rounded-lg"
              style="background: var(--content-panel-bg); border: 1px solid var(--card-border);"
            >
              <code class="flex-1 text-xs truncate" style="color: var(--text-main);">
                {{ sessionId }}
              </code>
              <button
                @click="copyUrl"
                class="text-xs px-2 py-0.5 rounded-md transition-colors font-medium"
                style="background: var(--primary-100, #cffafe); color: var(--primary-700, #0e7490);"
              >
                {{ copied ? '✓' : 'Copy URL' }}
              </button>
              <button
                @click="regenerateSession"
                class="text-xs px-2 py-0.5 rounded-md transition-colors font-medium"
                style="background: var(--card-border); color: var(--text-main);"
              >
                New Session
              </button>
            </div>
          </div>

          <!-- Last scanned indicator -->
          <Transition name="slide-up">
            <div
              v-if="lastScanned"
              class="w-full flex items-center gap-2 px-3 py-2 rounded-lg"
              style="background: #f0fdf4; border: 1px solid #bbf7d0;"
            >
              <svg class="w-4 h-4 text-green-500 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
              <div class="min-w-0">
                <p class="text-xs font-semibold text-green-700 truncate">Barcode: {{ lastScanned.barcode }}</p>
                <p class="text-xs text-green-600">Added to cart ✓</p>
              </div>
            </div>
          </Transition>

          <!-- Instructions -->
          <ol class="w-full space-y-1.5">
            <li
              v-for="(step, i) in steps"
              :key="i"
              class="flex items-start gap-2 text-xs"
              style="color: var(--text-muted);"
            >
              <span
                class="shrink-0 w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold mt-px"
                style="background: var(--primary-100, #cffafe); color: var(--primary-700, #0e7490);"
              >{{ i + 1 }}</span>
              {{ step }}
            </li>
          </ol>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useMobileScanSession } from '@/services/useMobileScanSession'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'
import eventBus from '@/utils/eventBus'

const emit = defineEmits(['close'])

// ── Session composable ────────────────────────────────────────────────────────
const {
  sessionId,
  isListening,
  lastScanned,
  pairingConfirmed,
  startListening,
  stopListening,
  refreshSession,
  getScannerUrl
} = useMobileScanSession()
// ── Stores ────────────────────────────────────────────────────────────────────
const cartStore = useCartStore()
const productsStore = useProductsStore()

// ── Local state ───────────────────────────────────────────────────────────────
const qrCanvas = ref(null)
const copied = ref(false)

const steps = [
  'Open your phone camera or QR reader',
  'Scan the QR code above',
  'The scanner page opens in your browser',
  'Scan product barcodes – cart updates instantly',
]

// ── QR Code generation (uses qrcode library via CDN-style dynamic import) ─────
const generateQR = async () => {
  try {
    // Use qrcode package if installed, otherwise fallback to API
    let QRCode
    try {
      QRCode = (await import('qrcode')).default
    } catch {
      // not installed – use public QR API as canvas image
      renderQRFallback()
      return
    }

    const url = getScannerUrl()
    await QRCode.toCanvas(qrCanvas.value, url, {
      width: 220,
      margin: 1,
      color: { dark: '#0f172a', light: '#ffffff' },
      errorCorrectionLevel: 'M',
    })
  } catch (err) {
    console.error('QR generation error:', err)
    renderQRFallback()
  }
}

// Fallback: draw QR via image from api.qrserver.com
const renderQRFallback = () => {
  const url = getScannerUrl()
  const apiUrl = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(url)}&color=0f172a&bgcolor=ffffff`
  const canvas = qrCanvas.value
  const ctx = canvas.getContext('2d')
  canvas.width = 220
  canvas.height = 220

  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => ctx.drawImage(img, 0, 0, 220, 220)
  img.onerror = () => {
    // Last resort: show text
    ctx.fillStyle = '#f1f5f9'
    ctx.fillRect(0, 0, 220, 220)
    ctx.fillStyle = '#475569'
    ctx.font = '12px monospace'
    ctx.fillText('QR Error – copy URL below', 10, 110)
  }
  img.src = apiUrl
}

// ── Copy scanner URL ──────────────────────────────────────────────────────────
const copyUrl = async () => {
  try {
    await navigator.clipboard.writeText(getScannerUrl())
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // fallback
    const el = document.createElement('textarea')
    el.value = getScannerUrl()
    document.body.appendChild(el)
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

const regenerateSession = async () => {
  stopListening()
  refreshSession()
  pairingConfirmed.value = false
  lastScanned.value = null
  await generateQR()
  startListening()
}

// ── Handle barcode from eventBus ──────────────────────────────────────────────
// The useMobileScanSession composable re-emits on eventBus('barcode:scanned')
// We handle cart addition here — same as DroidCam pattern in ShiftControl
const handleBarcode = ({ barcode }) => {
  // Find product by barcode in already-loaded products
  // item_barcode is an array: [{ barcode: "27074442", posa_uom: "Box" }]
  const product = productsStore.products.find(p =>
    Array.isArray(p.item_barcode) &&
    p.item_barcode.some(b => b.barcode === barcode)
  )

  if (!product) {
    console.warn(`⚠️ No product found for barcode: ${barcode}`)
    if (window.$toast) {
      window.$toast.warning(`Product not found for barcode: ${barcode}`)
    }
    return
  }

  // Find the matching barcode entry (for posa_uom)
  const barcodeEntry = product.item_barcode.find(b => b.barcode === barcode)

  console.log(`✅ Found product: ${product.item_name}`)
  cartStore.addToCart(product, barcodeEntry)

  // Update lastScanned for UI feedback
  lastScanned.value = { barcode, productName: product.item_name }

  if (window.$toast) {
    window.$toast.success(`Added: ${product.item_name}`)
  }
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  await generateQR()
  startListening()
  eventBus.on('barcode:scanned', handleBarcode)
})

onUnmounted(() => {
  stopListening()
  eventBus.off('barcode:scanned', handleBarcode)
})
watch(pairingConfirmed, (val) => {
  if (val) {
    console.log("📱 Mobile Connected → closing modal")
    emit('close')
  }
})
</script>

<style scoped>
.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #06b6d4, transparent);
  animation: scan 2s linear infinite;
  border-radius: 1px;
}

@keyframes scan {
  0%   { top: 0%; opacity: 0; }
  10%  { opacity: 1; }
  90%  { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.animate-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}

.slide-up-enter-active { transition: all 0.3s ease; }
.slide-up-leave-active { transition: all 0.2s ease; }
.slide-up-enter-from  { opacity: 0; transform: translateY(8px); }
.slide-up-leave-to    { opacity: 0; transform: translateY(-4px); }
</style>
