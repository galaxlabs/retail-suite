<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-8 text-center">
      <!-- Icon -->
      <div class="mb-6">
        <div v-if="progress < 100" class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full">
          <Loader class="w-8 h-8 text-blue-600 animate-spin" />
        </div>
        <div v-else class="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full">
          <Check class="w-8 h-8 text-green-600" />
        </div>
      </div>

      <!-- Title -->
      <h2 class="text-2xl font-bold text-gray-900 mb-2">
        {{ progress === 100 ? 'کامیاب!' : 'پروسیسنگ جاری ہے' }}
      </h2>

      <!-- Subtitle -->
      <p class="text-gray-600 mb-6">
        {{ progress === 100
          ? `تم معالجة حاضری للوردية: ${shiftName}`
          : `جاري معالجة حاضری للوردية: ${shiftName}`
        }}
      </p>

      <!-- Progress Bar -->
      <div class="mb-6">
        <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
          <div
            class="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
        <p class="text-sm text-gray-600 mt-2">{{ progress }}%</p>
      </div>

      <!-- Status Messages -->
      <div class="mb-6 text-left bg-gray-50 rounded-lg p-4 max-h-40 overflow-y-auto">
        <div
          v-for="(msg, index) in statusMessages"
          :key="index"
          class="text-sm text-gray-700 py-1"
        >
          {{ msg }}
        </div>
      </div>

      <!-- Estimated Time -->
      <div v-if="progress < 100" class="mb-6 text-sm text-gray-500">
        <p>وقت المتبقي: <span class="font-semibold">{{ estimatedTime }}</span></p>
      </div>

      <!-- Close Button -->
      <button
        v-if="progress === 100"
        @click="$emit('close')"
        class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        بند کریں
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Loader, Check } from 'lucide-vue-next'

/* ========================
   Props & Emits
======================== */
const props = defineProps({
  shiftName: {
    type: String,
    required: true
  },
  progress: {
    type: Number,
    default: 0,
    validator: (val) => val >= 0 && val <= 100
  }
})

const emit = defineEmits(['close'])

/* ========================
   State
======================== */
const statusMessages = ref([
  'جاري بدء معالجة حاضری...'
])
const startTime = ref(Date.now())
const estimatedTotalTime = 30000 // 30 seconds (configurable)

/* ========================
   Computed
======================== */
const estimatedTime = computed(() => {
  if (props.progress === 0) return 'حساب...'

  const elapsed = Date.now() - startTime.value
  const totalEstimated = (elapsed / props.progress) * 100
  const remaining = totalEstimated - elapsed

  const seconds = Math.ceil(remaining / 1000)

  if (seconds < 60) {
    return `${seconds} سیکنڈ`
  }

  const minutes = Math.ceil(seconds / 60)
  return `${minutes} سےٹ`
})

/* ========================
   Methods
======================== */
const addStatusMessage = (message) => {
  statusMessages.value.push(message)

  // Keep only last 10 messages
  if (statusMessages.value.length > 10) {
    statusMessages.value.shift()
  }
}

/* ========================
   Lifecycle
======================== */
onMounted(() => {
  // Simulate progress updates (in real app, these would come from backend)
  const interval = setInterval(() => {
    if (props.progress >= 25 && statusMessages.value.length === 1) {
      addStatusMessage('✓ داخلے اور خارجے کے ریکارڈ لوڈ ہو گئے')
    }
    if (props.progress >= 50 && statusMessages.value.length === 2) {
      addStatusMessage('✓ کام کے اوقات پروسیس ہو رہے ہیں')
    }
    if (props.progress >= 75 && statusMessages.value.length === 3) {
      addStatusMessage('✓ جاري اپ ڈیٹ کریں سجلات الغياب')
    }
    if (props.progress >= 95 && statusMessages.value.length === 4) {
      addStatusMessage('✓ پروسیسنگ مکمل ہو رہی ہے')
    }
  }, 500)

  return () => clearInterval(interval)
})
</script>

<style scoped>
/* Tailwind CSS styles */
</style>
