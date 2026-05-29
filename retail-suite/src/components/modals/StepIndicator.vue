

<!-- 🚀 النسخة 2: بدون SVG (أبسط) -->
<template>
  <div class="w-full py-8 px-6">
    <!-- Step Indicator Container -->
    <div class="relative mb-8" ref="containerRef">
      <!-- Lines Container -->
      <div ref="linesContainer" class="absolute inset-0 pointer-events-none" />

      <!-- Steps Circle -->
      <div class="flex items-center justify-between relative z-10">
        <div
          v-for="(step, index) in steps"
          :key="index"
          :ref="setStepRef(index)"
          class="flex flex-col items-center cursor-pointer group"
          @click="canClickStep(index) && $emit('change-step', index)"
        >
          <!-- Circle -->
          <div
            :class="[
              'w-12 h-12 rounded-full flex items-center justify-center font-bold text-base',
              'transition-all duration-500 transform shadow-md',
              'group-hover:scale-105',
              currentStep > index
                ? 'bg-gradient-to-br from-green-400 to-green-600 text-white ring-0'
                : currentStep === index
                ? 'bg-gradient-to-br from-blue-400 to-blue-600 text-white scale-110 ring-4 ring-blue-200 shadow-lg'
                : 'bg-gray-300 text-gray-600 ring-0'
            ]"
          >
            <span v-if="currentStep > index" class="text-lg">✓</span>
            <span v-else>{{ index + 1 }}</span>
          </div>

          <!-- Label -->
          <p
            :class="[
              'text-xs font-semibold transition-colors duration-300 mt-2 text-center',
              currentStep >= index ? 'text-blue-600' : 'text-gray-500'
            ]"
          >
            {{ step }}
          </p>
        </div>
      </div>
    </div>

    <!-- Status Bar -->
    <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
      <p class="text-sm text-blue-900">
        <strong>{{ steps[currentStep] }}</strong> -
        <span class="text-blue-700">{{ currentStep + 1 }} of {{ steps.length }}</span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUpdated, ref, watch, reactive } from 'vue'

const props = defineProps({
  currentStep: {
    type: Number,
    required: true
  },
  steps: {
    type: Array,
    required: true
  }
})

const containerRef = ref(null)
const linesContainer = ref(null)
const stepElements = reactive({})

// دالة لمحفوظ کریں مرجع كل خطوة
const setStepRef = (index) => {
  return (el) => {
    if (el) stepElements[index] = el
  }
}

// دالة حساب المسافة بين دائرتين
const getDistance = (el1, el2, containerRect) => {
  const rect1 = el1.getBoundingClientRect()
  const rect2 = el2.getBoundingClientRect()

  // مركز الدائرة الأولى
  const x1 = rect1.left - containerRect.left + rect1.width / 2
  const y1 = rect1.top - containerRect.top + rect1.height / 2

  // مركز الدائرة السیکنڈ
  const x2 = rect2.left - containerRect.left + rect2.width / 2
  const y2 = rect2.top - containerRect.top + rect2.height / 2

  // المسافة اليوقليدية
  const distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))
  const angle = Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI)

  return { distance, angle, x1, y1, x2, y2 }
}

// دالة رسم الخطوط
const drawLines = () => {
  const container = linesContainer.value
  if (!container) return

  container.innerHTML = '' // امسح القديم

  const containerRect = containerRef.value.getBoundingClientRect()
  const keys = Object.keys(stepElements).sort((a, b) => a - b)

  // ارسم خط بين كل دائرتين متتاليتين
  for (let i = 0; i < keys.length - 1; i++) {
    const el1 = stepElements[keys[i]]
    const el2 = stepElements[keys[i + 1]]

    if (el1 && el2) {
      const { distance, angle, x1, y1 } = getDistance(el1, el2, containerRect)

      // أنشئ خط
      const line = document.createElement('div')
      line.style.cssText = `
        position: absolute;
        height: 4px;
        width: ${distance -35}px;
        left: ${x1}px;
        top: ${y1-10}px;
        transform-origin: left center;
        transform: rotate(${angle}deg);
        border-radius: 8px;
        transition: all 0.7s ease;
        background: ${
          props.currentStep - 1 >= i
            ? 'linear-gradient(to right, #22c55e, #16a34a)'
            : '#d1d5db'
        };
        z-index: 0;
      `
      container.appendChild(line)
    }
  }
}

// عند الـ mount
onMounted(() => {
  setTimeout(drawLines, 100)
  window.addEventListener('resize', drawLines)
})

// عند كل اپ ڈیٹ کریں
onUpdated(() => {
  drawLines()
})

// عند تغيير الخطوة الحالية
watch(() => props.currentStep, () => {
  drawLines()
})

defineEmits(['change-step'])

const canClickStep = (stepIndex) => {
  return stepIndex <= props.currentStep
}
</script>
