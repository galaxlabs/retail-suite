<template>
  <div v-if="barcode" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">Barcode Details</h3>
        <button
          @click="$emit('close')"
          class="text-gray-500 hover:text-gray-700 text-2xl font-light"
        >
          ✕
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 space-y-6">
        <!-- Barcode Display -->
        <div class="flex justify-center bg-gray-50 p-8 rounded-lg border border-gray-200">
          <div class="text-center">
            <img :src="barcode.preview" class="w-64 h-34 flex items-center justify-center mb-4">
            <p class="text-sm text-gray-600">{{ barcode.code }}</p>
          </div>
        </div>

        <!-- Product Information -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide">Product Name</p>
              <p class="text-lg font-semibold text-gray-900">{{ barcode.productName }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide">SKU</p>
              <p class="text-lg font-mono text-gray-900">{{ barcode.sku }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide">Barcode Code</p>
              <p class="text-lg font-mono text-gray-900">{{ barcode.code }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide">Barcode Type</p>
              <span class="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                {{ barcode.type }}
              </span>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide">Status</p>
              <span :class="getStatusBadge(barcode.status)" class="inline-block px-3 py-1 rounded-full text-sm font-medium">
                {{ capitalizeStatus(barcode.status) }}
              </span>
            </div>
            <div>

              <p class="text-xs text-gray-500 uppercase tracking-wide">Created Date</p>
              <p class="text-sm text-gray-900">{{ formatDate(barcode.creation) }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide">Last Used</p>
              <p class="text-sm text-gray-900">{{ formatDate(barcode.lastUsed) || 'Never' }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase tracking-wide">Usage Count</p>
              <p class="text-lg font-semibold text-gray-900">{{ barcode.usageCount || 0 }}</p>
            </div>
          </div>
        </div>

        <!-- Printable Section -->
        <div id="printable-barcode" class="hidden">
          <div class="p-12">
            <div class="border-b-2 border-gray-900 pb-4 mb-6">
              <h1 class="text-lg font-bold">Product Label</h1>
            </div>
            <div class="flex justify-center mb-8">
              <div v-html="barcode.preview"></div>
            </div>
            <div class="grid grid-cols-2 gap-8 text-sm">
              <div>
                <p class="text-xs text-gray-600 uppercase font-semibold mb-2">Product</p>
                <p>{{ barcode.productName }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-600 uppercase font-semibold mb-2">SKU</p>
                <p class="font-mono">{{ barcode.sku }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-600 uppercase font-semibold mb-2">Barcode</p>
                <p class="font-mono">{{ barcode.code }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-600 uppercase font-semibold mb-2">Type</p>
                <p>{{ barcode.type }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions Section -->
        <div class="p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-3">
          <p class="text-sm font-medium text-gray-700">Quick Actions</p>
          <div class="grid grid-cols-2 gap-3">
            <button
              @click="copyToClipboard(barcode.code)"
              class="px-3 py-2 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-lg transition text-sm font-medium"
            >
              Copy Code
            </button>
            <button
              @click="downloadBarcode"
              class="px-3 py-2 bg-green-100 text-green-700 hover:bg-green-200 rounded-lg transition text-sm font-medium"
            >
              Download
            </button>
            <button
              @click="printBarcode"
              class="px-3 py-2 bg-purple-100 text-purple-700 hover:bg-purple-200 rounded-lg transition text-sm font-medium"
            >
              Print
            </button>
            <button
              @click="shareBarcode"
              class="px-3 py-2 bg-orange-100 text-orange-700 hover:bg-orange-200 rounded-lg transition text-sm font-medium"
            >
              Share
            </button>
          </div>
        </div>

        <!-- Copy Notification -->
        <div v-if="copySuccess" class="p-3 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-green-800 text-sm">✓ Barcode code copied to clipboard</p>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'


  const props = defineProps( {
    barcode: {
      type: Object,
      required: true
    }
  })
  const emit = defineEmits(['close'])

  const copySuccess = ref(false)

  const getStatusBadge = (status) => {
    const badges = {
      active: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      inactive: 'bg-red-100 text-red-800'
    }
    return badges[status] || 'bg-gray-100 text-gray-800'
  }

const capitalizeStatus = (status) =>
  String(status || 'unknown').charAt(0).toUpperCase() +
  String(status || 'unknown').slice(1)

  const formatDate = (date) => {
    if (!date) return 'N/A'
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      copySuccess.value = true
      setTimeout(() => {
        copySuccess.value = false
      }, 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const downloadBarcode = () => {
    // TODO: Implement download as image
    window.$toast?.info('Downloading barcode...')
  }

  const printBarcode = () => {
    const printElement = document.getElementById('printable-barcode')
    if (printElement) {
      const printWindow = window.open('', '', 'height=600,width=800')
      printWindow.document.write(printElement.innerHTML)
      printWindow.document.close()
      printWindow.print()
    }
  }

  const shareBarcode = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Barcode',
        text: `Barcode: ${props.barcode.code}`,
        url: window.location.href
      }).catch(err => console.log('Share error:', err))
    } else {
      window.$toast?.warning('Share not supported')
    }
  }

</script>
