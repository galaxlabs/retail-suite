<!-- ProductCard.vue -->
<template>
  <div
    class="select-none cursor-pointer transition-all duration-300 overflow-hidden rounded-2xl shadow group relative"
    :style="{ background: 'var(--card-bg)', color: 'var(--text-main)', border: '1px solid var(--card-border)' }"
    :title="product.name"
    @click="handleClick"
  >
    <!-- Product Image -->
    <div class="relative overflow-hidden" style="background: var(--item-bg);">
      <img
        :src="currentSrc"
        :alt="product.name"
        class="w-10/12 mx-auto h-24 sm:h-32 md:h-40 object-contain transition-transform duration-300 group-hover:scale-105"
        style="padding: 4px;"
        @error="handleImageError"
      />

      <!-- Stock Badge — top left -->
      <div
        class="absolute top-2 left-2 text-xs px-2 py-0.5 rounded-full font-semibold"
        :style="stockBadgeStyle"
      >
        {{ stockLabel }}
      </div>

      <!-- Cart Qty Badge — top right -->
      <transition name="pop">
        <div
          v-if="cartQuantity > 0"
          class="absolute top-2 right-2 text-xs w-6 h-6 rounded-full flex items-center justify-center font-bold"
          :style="{ background: 'var(--accent-green)', color: '#fff' }"
        >
          {{ cartQuantity }}
        </div>
      </transition>

      <!-- Hover Overlay -->
      <div
        class="absolute inset-0 flex items-end justify-center pb-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
        :style="{ background: 'var(--overlay-dark)' }"
      >
        <button
          class="flex items-center gap-1 px-4 py-1.5 rounded-full text-xs font-semibold transition-transform duration-150 active:scale-95"
          :style="{ background: 'var(--accent-cyan)', color: '#fff' }"
          :disabled="outOfStock"
          @click.stop="handleQuickAdd"
        >
          <PlusIcon class="w-3 h-3" />
          {{ outOfStock ? 'Out of Stock' : 'Add to Cart' }}
        </button>
      </div>

      <!-- Quick Add Overlay -->
      <div class="absolute inset-0 flex flex-col items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300" :style="{ background: 'var(--overlay-dark)' }">
        <button class="w-10/12 px-4 py-8 rounded-full font-semibold text-sm" :style="{ background: 'var(--card-bg)', color: 'var(--accent-cyan)' }" @click.stop="handleQuickAdd">
          <PlusIcon class="w-4 h-4 inline mr-1" /> Add to Cart
        </button>
        <div class="grid grid-cols-3 gap-1 w-10/12">
          <button @click.stop="$emit('add-to-cart', {...product, qty: 0.250})" class="rounded py-0.5 text-xs font-semibold transition active:scale-95" :style="{ background: 'var(--accent-cyan)', color: '#fff' }">250g</button>
          <button @click.stop="$emit('add-to-cart', {...product, qty: 0.500})" class="rounded py-0.5 text-xs font-semibold transition active:scale-95" :style="{ background: 'var(--accent-cyan)', color: '#fff' }">500g</button>
          <button @click.stop="$emit('add-to-cart', {...product, qty: 1})" class="rounded py-0.5 text-xs font-semibold transition active:scale-95" :style="{ background: 'var(--accent-cyan)', color: '#fff' }">1 KG</button>
        </div>
      </div>

    </div>

      <!-- Info Area -->
    <div class="px-3 pt-2 pb-3" :style="{ background: 'var(--card-bg)' }">
      <!-- Name -->
      <p
        class="font-semibold text-sm truncate leading-tight"
        :style="{ color: 'var(--text-main)' }"
        :title="product.item_name"
      >
        {{ product.item_name }}
      </p>

      <!-- Description -->
      <p
        v-if="product.description && product.description !== product.item_name"
        class="text-xs truncate mt-0.5"
        :style="{ color: 'var(--text-muted)' }"
      >
        {{ product.description }}
      </p>

      <!-- Price Row -->
      <div class="flex items-end justify-between mt-2">
        <div>
          <!-- Original price (crossed) if discounted -->
          <p
            v-if="product.discount_percentage > 0 || product.discount_amount > 0"
            class="text-xs line-through"
            :style="{ color: 'var(--text-muted)' }"
          >
            {{ formatPrice(product.original_rate) }}
          </p>
          <p
            class="font-bold text-sm"
            :style="{ color: discounted ? 'var(--accent-red, #ef4444)' : 'var(--primary-600)' }"
          >
            {{ formatPrice(product.rate) }}
          </p>
        </div>

        <!-- Qty / Stock -->
        <div class="flex flex-col items-end gap-0.5">
          <span
            v-if="product.actual_qty !== undefined"
            class="text-xs font-medium px-1.5 py-0.5 rounded"
            :style="qtyChipStyle"
          >
            {{ product.actual_qty }} {{ product.stock_uom || '' }}
          </span>
          <span
            v-if="isInCart"
            class="text-xs font-semibold"
            :style="{ color: 'var(--accent-green)' }"
          >
            ✓ In Cart
          </span>
        </div>
      </div>

      <!-- Discount Badge -->
      <div
        v-if="discounted"
        class="mt-1.5 inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full"
        :style="{ background: 'rgba(239,68,68,0.1)', color: 'var(--accent-red, #ef4444)' }"
      >
        <span v-if="product.discount_percentage > 0">-{{ product.discount_percentage }}%</span>
        <span v-else-if="product.discount_amount > 0">-{{ formatPrice(product.discount_amount) }}</span>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div
      v-if="isLoading"
      class="absolute inset-0 flex items-center justify-center"
      :style="{ background: 'var(--card-bg)', opacity: 0.85 }"
    >
      <LoadingSpinner class="w-6 h-6" />
    </div>
  </div>
</template>
<script setup>
import { ref, computed} from 'vue'
import { formatPrice } from '@/utils/formatters'
import  PlusIcon from '@/components/icons/PlusIcon.svg';
import LoadingSpinner from '../icons/LoadingSpinner.vue';
import config from '@/config/frappe'

const props = defineProps({
  product: { type: Object, required: true },
  isInCart: { type: Boolean, default: false },
  cartQuantity: { type: Number, default: 0 }
})

import { useProductsStore } from '@/stores/products'

const store = useProductsStore()


const emit = defineEmits(['add-to-cart', 'remove-from-cart', 'view-details'])

const isLoading = ref(false)
const imageError = ref(false)

const defaultImageSrc = `${config.FRAPPE_URL}/img/default-product.jpg`

const stockLabel = computed(() => {
  const qty = props.product.actual_qty
  if (qty === undefined || qty === null) return ''
  if (qty <= 0) return 'Out of stock'
  if (qty <= 5) return 'Limited quantity'
  return 'Available'
})


const discounted = computed(() =>
  props.product.discount_percentage > 0 || props.product.discount_amount > 0
)

const outOfStock = computed(() =>
  props.product.actual_qty !== undefined && props.product.actual_qty <= 0
)


const stockBadgeStyle = computed(() => {
  const qty = props.product.actual_qty
  if (qty === undefined || qty === null) return { display: 'none' }
  if (qty <= 0) return { background: 'rgba(239,68,68,0.15)', color: '#ef4444' }
  if (qty <= 5) return { background: 'rgba(245,158,11,0.15)', color: '#f59e0b' }
  return { background: 'rgba(16,185,129,0.15)', color: '#10b981' }
})

// Qty chip color
const qtyChipStyle = computed(() => {
  const qty = props.product.actual_qty
  if (qty === undefined || qty === null) return {}
  if (qty <= 0) return { background: 'rgba(239,68,68,0.1)', color: '#ef4444' }
  if (qty <= 5) return { background: 'rgba(245,158,11,0.1)', color: '#f59e0b' }
  return { background: 'rgba(16,185,129,0.1)', color: '#10b981' }
})

const handleClick = () => emit('view-details', props.product)



// Handle quick add to cart
const handleQuickAdd = async () => {
    if (isLoading.value) return

    isLoading.value = true

    try {
      await new Promise(resolve => setTimeout(resolve, 200)) // Simulate loading
      emit('add-to-cart', props.product)
    } catch (error) {
      console.error('Error adding to cart:', error)
    } finally {
      isLoading.value = false
    }
}


const currentSrc = computed(() => {
  if (!props.product?.image) return defaultImageSrc

  // لو الصورة جاية full URL
  if (props.product.image.startsWith('http')) {
    return props.product.image
  }

  return `${config.FRAPPE_URL}${props.product.image}`
})

// Handle image loading error
const handleImageError = () => {
  imageError.value = true
}
</script>

<style scoped>
/* Hover effects */
.group:hover .group-hover\:scale-105 {
  transform: scale(1.05);
}

.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

/* Card animations */
.transition-all {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Price styling */
.text-cyan-600 {
  color: #0891b2;
}

/* Truncate text */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Badge animations */
.opacity-0 {
  opacity: 0;
}

.group:hover .opacity-0 {
  opacity: 1;
}

/* Smooth transitions for all elements */
* {
  transition: all 0.2s ease-in-out;
}

/* Focus states for accessibility */
.cursor-pointer:focus {
  outline: 2px solid #06b6d4;
  outline-offset: 2px;
}

button:focus {
  outline: 2px solid #06b6d4;
  outline-offset: 2px;
}

/* Loading overlay */
.bg-opacity-80 {
  background-opacity: 0.8;
}

/* Image aspect ratio */
.h-32 {
  height: 8rem;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .text-sm {
    font-size: 0.75rem;
  }

  .h-32 {
    height: 6rem;
  }
}

/* Error state for images */
img[src=""] {
  background: #f3f4f6;
}

/* Animation for cart quantity badge */
.bg-green-500 {
  animation: bounceIn 0.3s ease-out;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
