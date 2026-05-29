<template>
  <div class="fixed glass w-full h-screen left-0 top-0 z-50 flex flex-wrap justify-center content-center p-4 md:p-24">
    <!-- Background Overlay -->
    <div
      class="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
      @click="handleBackgroundClick"
    ></div>

    <!-- Modal Content -->
    <div
      class="relative w-full max-w-md mx-auto rounded-3xl p-6 md:p-8 bg-white shadow-2xl transform transition-all duration-300"
      :class="{ 'scale-95 opacity-0': !isVisible, 'scale-100 opacity-100': isVisible }"
    >
      <!-- Loading Overlay -->
      <div
        v-if="isLoading"
        class="absolute inset-0 bg-white bg-opacity-90 rounded-3xl flex items-center justify-center z-10"
      >
        <div class="text-center">
          <LoadingSpinner class="w-8 h-8 mx-auto mb-4" />
          <p class="text-gray-600">{{ loadingText }}</p>
        </div>
      </div>

      <!-- Header -->
      <div class="text-center mb-8">
        <!-- App Logo -->
        <div class="mb-6">
          <AppLogo class="w-24 h-24 mx-auto" />
        </div>

        <h3 class="text-2xl md:text-3xl font-bold text-gray-800 mb-2">
          FIRST TIME?
        </h3>
        <p class="text-gray-600 text-sm md:text-base">
          Welcome to Retail Suite! Let's get you started.
        </p>
      </div>

      <!-- Options -->
      <div class="space-y-4">
        <!-- Load Sample Data Option -->
        <button
          @click="handleLoadSample"
          class="w-full text-left rounded-xl bg-gray-500 text-white focus:outline-none hover:bg-cyan-400 px-4 py-4 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          :disabled="isLoading"
        >
          <div class="flex items-center">
            <!-- <SampleDataIcon class="w-6 h-6 mr-3 flex-shrink-0" /> -->
             <svg :class="class" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 4H6a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-2m-4-1v8m0 0l3-3m-3 3L9 8m-5 5h2.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293h3.172a1 1 0 00.707-.293l2.414-2.414a1 1 0 01.707-.293H20" />
            </svg>
            <div>
              <div class="font-semibold text-base">LOAD SAMPLE DATA</div>
              <div class="text-sm opacity-90 mt-1">
                Start with 12 sample products to explore the system
              </div>
            </div>
          </div>
        </button>

        <!-- Start Blank Option -->
        <button
          @click="handleStartBlank"
          class="w-full text-left rounded-xl bg-gray-500 text-white focus:outline-none hover:bg-teal-400 px-4 py-4 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          :disabled="isLoading"
        >
          <div class="flex items-center">
            <BlankIcon class="w-6 h-6 mr-3 flex-shrink-0" />
            <div>
              <div class="font-semibold text-base">LEAVE IT EMPTY</div>
              <div class="text-sm opacity-90 mt-1">
                Start with an empty inventory and add your own products
              </div>
            </div>
          </div>
        </button>
      </div>

      <!-- Additional Info -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <div class="text-center">
          <p class="text-xs text-gray-500 mb-2">
            You can change this later in settings
          </p>
          <div class="flex items-center justify-center space-x-4 text-xs text-gray-400">
            <span class="flex items-center">
              <CheckIcon class="w-3 h-3 mr-1" />
              Offline Storage
            </span>
            <span class="flex items-center">
              <CheckIcon class="w-3 h-3 mr-1" />
              No Registration
            </span>
          </div>
        </div>
      </div>

      <!-- Close Button (Optional) -->
      <button
        v-if="allowClose"
        @click="handleClose"
        class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 focus:outline-none p-1 rounded-full hover:bg-gray-100 transition-colors duration-200"
        :disabled="isLoading"
      >
        <CloseIcon class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'


const props = defineProps( {
    allowClose: {
      type: Boolean,
      default: false
    },
    autoShow: {
      type: Boolean,
      default: true
    }
})
const emit = defineEmits(['load-sample', 'start-blank', 'close'])


  const isVisible = ref(false)
  const isLoading = ref(false)
  const loadingText = ref('')

  // Show modal with animation
  const show = () => {
    isVisible.value = true
  }

  // Hide modal with animation
  const hide = () => {
    isVisible.value = false
  }

  // Handle load sample data
      const handleLoadSample = async () => {
      const response = await fetch('/data/sample.json')
      console.log('rrrrrrrrrrrrrrr',response)
      if (!response.ok) throw new Error('Failed to load sample.json')
      if (isLoading.value) return

      isLoading.value = true
      loadingText.value = 'Loading sample products...'

      try {
          // Simulate loading delay for better UX
          await new Promise(resolve => setTimeout(resolve, 1000))

          emit('load-sample')
      } catch (error) {
          console.error('Error loading sample data:', error)
          window.$toast?.error('Failed to load sample data. Please try again.')
      } finally {
          isLoading.value = false
          loadingText.value = ''
      }
      }

  // Handle start blank
  const handleStartBlank = async () => {
    if (isLoading.value) return

    isLoading.value = true
    loadingText.value = 'Setting up your store...'

    try {
      // Simulate setup delay
      await new Promise(resolve => setTimeout(resolve, 500))

      emit('start-blank')
    } catch (error) {
      console.error('Error starting blank:', error)
      window.$toast?.error('Failed to initialize. Please try again.')
    } finally {
      isLoading.value = false
      loadingText.value = ''
    }
  }

  // Handle close
  const handleClose = () => {
    if (isLoading.value || !props.allowClose) return

    hide()
    setTimeout(() => {
      emit('close')
    }, 300)
  }

  // Handle background click
  const handleBackgroundClick = () => {
    if (props.allowClose) {
      handleClose()
    }
  }

  // Handle escape key
  const handleEscape = (event) => {
    if (event.key === 'Escape' && props.allowClose) {
      handleClose()
    }
  }

  // Lifecycle
  onMounted(() => {
    if (props.autoShow) {
      nextTick(() => {
        show()
      })
    }

    // Add escape key listener
    document.addEventListener('keydown', handleEscape)
  })

  // Cleanup
  // onBeforeUnmount(() => {
  //   document.removeEventListener('keydown', handleEscape)
  // })

// Icon Components
const AppLogo = {
  props: ['class'],
  template: `
    <svg :class="class" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32.623 32.605">
      <path d="M15.612 0c-.36.003-.705.01-1.03.021C8.657.223 5.742 1.123 3.4 3.472.714 6.166-.145 9.758.019 17.607c.137 6.52.965 9.271 3.542 11.768 1.31 1.269 2.658 2 4.73 2.57.846.232 2.73.547 3.56.596.36.021 2.336.048 4.392.06 3.162.018 4.031-.016 5.63-.221 3.915-.504 6.43-1.778 8.234-4.173 1.806-2.396 2.514-5.731 2.516-11.846.001-4.407-.42-7.59-1.278-9.643-1.463-3.501-4.183-5.53-8.394-6.258-1.634-.283-4.823-.475-7.339-.46z" fill="#fff"/>
      <path d="M16.202 13.758c-.056 0-.11 0-.16.003-.926.031-1.38.172-1.747.538-.42.421-.553.982-.528 2.208.022 1.018.151 1.447.553 1.837.205.198.415.313.739.402.132.036.426.085.556.093.056.003.365.007.686.009.494.003.63-.002.879-.035.611-.078 1.004-.277 1.286-.651.282-.374.392-.895.393-1.85 0-.688-.066-1.185-.2-1.506-.228-.547-.653-.864-1.31-.977a7.91 7.91 0 00-1.147-.072z" fill="#00dace"/>
      <path d="M16.22 19.926c-.056 0-.11 0-.16.003-.925.031-1.38.172-1.746.539-.42.42-.554.981-.528 2.207.02 1.018.15 1.448.553 1.838.204.198.415.312.738.4.132.037.426.086.556.094.056.003.365.007.686.009.494.003.63-.002.88-.034.61-.08 1.003-.278 1.285-.652.282-.374.393-.895.393-1.85 0-.688-.066-1.185-.2-1.506-.228-.547-.653-.863-1.31-.977a7.91 7.91 0 00-1.146-.072z" fill="#00dace"/>
    </svg>
  `
}

const SampleDataIcon = {
  props: ['class'],
  template: `
    <svg :class="class" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 4H6a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-2m-4-1v8m0 0l3-3m-3 3L9 8m-5 5h2.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293h3.172a1 1 0 00.707-.293l2.414-2.414a1 1 0 01.707-.293H20" />
    </svg>
  `
}

const BlankIcon = {
  props: ['class'],
  template: `
    <svg :class="class" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
    </svg>
  `
}

const CheckIcon = {
  props: ['class'],
  template: `
    <svg :class="class" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
    </svg>
  `
}

const CloseIcon = {
  props: ['class'],
  template: `
    <svg :class="class" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
    </svg>
  `
}

const LoadingSpinner = {
  props: ['class'],
  template: `
    <div :class="class" class="animate-spin rounded-full border-2 border-b-transparent border-cyan-500"></div>
  `
}
</script>

<style scoped>
/* Glass effect */
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
}

/* Modal animations */
.transform {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Button hover effects */
button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

button:active {
  transform: translateY(0);
}

/* Loading animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Backdrop blur */
.backdrop-blur-sm {
  backdrop-filter: blur(4px);
}

/* Focus states */
button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.5);
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .rounded-3xl {
    border-radius: 1.5rem;
  }

  .p-6 {
    padding: 1rem;
  }
}

/* Color variables */
.bg-gray-500 {
  background-color: #64748b;
}

.hover\:bg-cyan-400:hover {
  background-color: #22d3ee;
}

.hover\:bg-teal-400:hover {
  background-color: #2dd4bf;
}
</style>
