<!-- SupplierModal.vue - English Version with Premium Design -->

<template>
  <div class="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
    <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[95vh] overflow-y-auto">
      <!-- Header with Premium Gradient -->
      <div class="px-8 py-6 bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500 sticky top-0 z-10 flex justify-between items-center rounded-t-2xl">
        <div>
          <h2 class="text-3xl font-bold text-white">
            {{ supplier ? 'Edit Supplier' : 'Add New Supplier' }}
          </h2>
          <p class="text-indigo-100 text-sm mt-2">
            {{ supplier ? 'Modify supplier details and information' : 'Enter new supplier details' }}
          </p>
        </div>
        <button
          @click="$emit('close')"
          class="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition duration-200 w-10 h-10 flex items-center justify-center"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Form Content -->
      <div class="px-8 py-8 space-y-8">
        <form @submit.prevent="handleSubmit" class="space-y-8">

          <!-- Section 1: Basic Information -->
          <section class="space-y-6">
            <div class="flex items-center gap-4 pb-4 border-b-2 border-indigo-100">
              <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold text-lg">1</span>
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900">Basic Information</h3>
                <p class="text-gray-500 text-sm mt-1">Enter supplier name and classification</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Name -->
              <div>
                <label class="text-sm font-semibold text-gray-800 block mb-3">Name <span class="text-red-500">*</span></label>
                <input
                  v-model="formData.name"
                  type="text"
                  placeholder="e.g., ABC Manufacturing Ltd."
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white"

                />
               </div>
              <!-- Supplier Name -->
              <div class="md:col-span-2">
                <label class="text-sm font-semibold text-gray-800 block mb-3">Supplier Name <span class="text-red-500">*</span></label>
                <input
                  v-model="formData.supplier_name"
                  type="text"
                  placeholder="e.g., ABC Manufacturing Ltd."
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white"
                  required
                />
              </div>

              <!-- Supplier Group -->
              <div>
                <label class="text-sm font-semibold text-gray-800 block mb-3">Supplier Group</label>
                <select
                  v-model="formData.supplier_group"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white cursor-pointer"
                >
                  <option value="">Select a group</option>
                  <option v-for="group in supplierGroups" :key="group.name" :value="group.name">
                    {{ group.name }}
                  </option>
                </select>
              </div>

              <!-- Supplier Type -->
              <div>
                <label class="text-sm font-semibold text-gray-800 block mb-3">Supplier Type</label>
                <select
                  v-model="formData.supplier_type"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white cursor-pointer"
                >
                  <option value="">Select a type</option>
                  <option value="Company">Company</option>
                  <option value="Individual">Individual</option>
                  <option value="Partnership">Partnership</option>
                </select>
              </div>

              <!-- Status -->
              <div>
                <label class="text-sm font-semibold text-gray-800 block mb-3">Supplier Status</label>
                <div class="flex gap-4 pt-2">
                  <label class="flex items-center gap-2 cursor-pointer px-4 py-3 border border-gray-300 rounded-lg transition hover:bg-gray-50" :class="formData.disabled === '0' ? 'bg-green-50 border-green-300' : ''">
                    <input
                      v-model="formData.disabled"
                      type="radio"
                      value="0"
                      class="w-4 h-4 text-green-600"
                    />
                    <span class="text-sm font-medium text-gray-700">Active</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer px-4 py-3 border border-gray-300 rounded-lg transition hover:bg-gray-50" :class="formData.disabled === '1' ? 'bg-red-50 border-red-300' : ''">
                    <input
                      v-model="formData.disabled"
                      type="radio"
                      value="1"
                      class="w-4 h-4 text-red-600"
                    />
                    <span class="text-sm font-medium text-gray-700">Inactive</span>
                  </label>
                </div>
              </div>
            </div>
          </section>

          <!-- Section 2: Contact Information -->
          <section class="space-y-6">
            <div class="flex items-center justify-between pb-4 border-b-2 border-indigo-100">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span class="text-white font-bold text-lg">2</span>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-gray-900">Contact Information
                    <span class="text-blue-600">{{ formData.contact_name }}</span></h3>
                  <p class="text-gray-500 text-sm mt-1">Email and phone details</p>
                </div>
              </div>
              <label class="flex items-center gap-2 cursor-pointer hover:bg-indigo-50 px-4 py-2 rounded-lg transition">
                <input
                  v-model="show_primary_contact"
                  type="checkbox"
                  class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                />
                <span class="text-sm font-medium text-gray-700">{{ show_primary_contact ? 'Hide' : 'Show' }}</span>
              </label>
            </div>

            <transition name="fade-slide">
              <div v-if="show_primary_contact" class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
                <!-- Email -->
                <div>
                  <label class="text-sm font-semibold text-gray-800 block mb-3">Email Address</label>
                  <input
                    v-model="formData.email_id"
                    type="email"
                    placeholder="e.g., contact@supplier.com"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white"
                  />
                </div>

                <!-- Mobile Number -->
                <div>
                  <label class="text-sm font-semibold text-gray-800 block mb-3">Mobile Number <span class="text-red-500">*</span></label>
                  <input
                    v-model="formData.mobile_no"
                    type="tel"
                    placeholder="e.g., +1 234 567 8900"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white"
                    required
                  />
                </div>
              </div>
            </transition>
          </section>

          <!-- Section 3: Address Information -->
          <section class="space-y-6">
            <div class="flex items-center justify-between pb-4 border-b-2 border-indigo-100">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span class="text-white font-bold text-lg">3</span>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-gray-900">Address Information</h3>
                  <p class="text-gray-500 text-sm mt-1">Complete address details</p>
                </div>
              </div>
              <label class="flex items-center gap-2 cursor-pointer hover:bg-indigo-50 px-4 py-2 rounded-lg transition">
                <input
                  v-model="show_primary_address"
                  type="checkbox"
                  class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                />
                <span class="text-sm font-medium text-gray-700">{{ show_primary_address ? 'Hide' : 'Show' }}</span>
              </label>
            </div>

            <transition name="fade-slide">
              <div v-if="show_primary_address" class="space-y-6 pt-4">
                <!-- Address Lines -->
                 <h3>{{ formData.contact_name }}</h3>
                <div>
                  <label class="text-sm font-semibold text-gray-800 block mb-3">Address Line 1</label>
                  <textarea
                    v-model="formData.address_line1"
                    placeholder="e.g., 123 Business Street, Suite 100"
                    rows="2"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white resize-none"
                  ></textarea>
                </div>

                <div>
                  <label class="text-sm font-semibold text-gray-800 block mb-3">Address Line 2 <span class="text-gray-400 font-normal">(Optional)</span></label>
                  <textarea
                    v-model="formData.address_line2"
                    placeholder="e.g., Building A, Floor 5"
                    rows="2"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white resize-none"
                  ></textarea>
                </div>

                <!-- City, State, Country Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="text-sm font-semibold text-gray-800 block mb-3">City</label>
                    <input
                      v-model="formData.city"
                      type="text"
                      placeholder="e.g., New York"
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white"
                    />
                  </div>

                  <div>
                    <label class="text-sm font-semibold text-gray-800 block mb-3">State / Province</label>
                    <input
                      v-model="formData.state"
                      type="text"
                      placeholder="e.g., New York"
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white"
                    />
                  </div>

                  <div>
                    <label class="text-sm font-semibold text-gray-800 block mb-3">Country</label>
                    <input
                      v-model="formData.country"
                      type="text"
                      placeholder="e.g., United States"
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white"
                    />
                  </div>

                  <div>
                    <label class="text-sm font-semibold text-gray-800 block mb-3">Postal Code</label>
                    <input
                      v-model="formData.pin_code"
                      type="text"
                      placeholder="e.g., 10001"
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white"
                    />
                  </div>
                </div>
              </div>
            </transition>
          </section>

          <!-- Section 4: Additional Notes -->
          <section class="space-y-6">
            <div class="flex items-center gap-4 pb-4 border-b-2 border-indigo-100">
              <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold text-lg">4</span>
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900">Additional Notes</h3>
                <p class="text-gray-500 text-sm mt-1">Any additional information</p>
              </div>
            </div>

            <div>
              <label class="text-sm font-semibold text-gray-800 block mb-3">Notes <span class="text-gray-400 font-normal">(Optional)</span></label>
              <textarea
                v-model="formData.custom_note"
                placeholder="Add any additional remarks or information about this supplier..."
                rows="4"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition duration-200 bg-gray-50 focus:bg-white resize-none"
              ></textarea>
            </div>
          </section>

          <!-- Form Actions -->
          <div class="flex gap-4 pt-8 border-t-2 border-gray-100">
            <button
              type="button"
              @click="$emit('close')"
              class="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition duration-200 font-semibold text-gray-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-lg hover:from-indigo-700 hover:to-blue-700 transition duration-200 font-semibold shadow-lg hover:shadow-xl"
            >
              {{ supplier ? 'Update Supplier' : 'Create Supplier' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, watch } from 'vue'

/* =========================
   Props & Emits
========================= */
const props = defineProps({
  supplier: {
    type: Object,
    default: null
  },
  supplierGroups: {
    type: Array,
    default: () => []
  },
  contacts: {
    type: Array,
    default: () => []
  },
  addresses: {
    type: Object,
    default: () => ({})
  },
})

const emit = defineEmits(['save', 'close'])

/* =========================
   State
========================= */
const show_primary_contact = ref(false)
const show_primary_address = ref(false)
const formData = ref({
  name: '',
  supplier_name: '',
  supplier_group: '',
  supplier_type: '',
  mobile_no: '',
  email_id: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  country: '',
  pin_code: '',
  disabled: 0,
  custom_note: ''
})


/* =========================
   Methods
========================= */
const resetForm = () => {
  formData.value = {
  name: '',
  supplier_name: '',
  supplier_group: '',
  supplier_type: '',
  mobile_no: '',
  email_id: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  country: '',
  pin_code: '',
  disabled: 0,
  custom_note: '',
  contact_name: '',
  }
}

const handleSubmit = () => {
  if (!formData.value.supplier_name) {
    window.$toast?.warning('Please fill in required fields')
    return
  }
  emit('save', { ...formData.value })
}

/* =========================
   Watchers
========================= */
watch(
  [() => props.supplier, () => props.supplierGroups, () => props.contacts, () => props.addresses],
  ([newSupplier, newGroups, newContacts, newAddresses]) => {
    if (newSupplier) {
      console.log('Populating form with supplier data:', newSupplier)
      console.log('Supplier contacts:', newContacts)
      console.log('Supplier addresses:', newAddresses)
      console.log('Groups:', newGroups)
      console.log('Selected group:', newSupplier.supplier_group)

      formData.value = {
        name: newSupplier.name || '',
        supplier_name: newSupplier.supplier_name || '',
        supplier_group: newSupplier.supplier_group || '',
        supplier_type: newSupplier.supplier_type || '',
        mobile_no: newContacts.mobile_no || '',
        email_id: newContacts.email_id || '',
        address_line1: newAddresses?.address_line1 || '',
        address_line2: newAddresses?.address_line2 || '',
        city: newAddresses?.city || '',
        state: newAddresses?.state || '',
        country: newAddresses?.country || '',
        pin_code: newAddresses?.pin_code || '',
        disabled: newSupplier.disabled,
        custom_note: newSupplier.custom_note || '',
        contact_name: newContacts.name || ''
      }
    } else {
      resetForm()
    }
  },
  { immediate: true }
)
</script>


<style scoped>
input, textarea, select {
  font-family: inherit;
}
</style>
<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, max-height 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  max-height: 0;
}

.fade-enter-to, .fade-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
