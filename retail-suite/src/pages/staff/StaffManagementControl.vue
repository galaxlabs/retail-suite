<!-- StaffManagementControl.vue -->
<template>

    <div class="w-full flex min-h-screen" :style="{ background: 'var(--item-bg)' }">
      <main class="flex flex-col flex-1 min-h-screen">

        <!-- Header -->
        <header
          class="mx-3 mt-3 sticky top-0 z-10 rounded-xl shadow-sm"
          :style="{
            background: 'var(--card-bg)',
            borderBottom: '1px solid var(--card-border)'
          }"
        >
          <div class="px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
              <button
                @click="goBack"
                class="p-2 rounded-lg transition"
                :style="{ color: 'var(--text-muted)' }"
                @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                @mouseleave="$event.currentTarget.style.background = 'transparent'"
              >
                <ArrowLeft class="w-6 h-6" />
              </button>
              <div>
                <h1 class="text-lg font-bold" :style="{ color: 'var(--text-main)' }">Basic Data Management</h1>
                <p class="text-sm" :style="{ color: 'var(--text-muted)' }">{{ totalItems }} items registered</p>
              </div>
            </div>
          </div>
        </header>

        <!-- Statistics Cards -->
        <section class="px-6 py-6">
          <div
            class="rounded-xl shadow-sm p-6"
            :style="{
              background: 'var(--card-bg)',
              border: '1px solid var(--card-border)'
            }"
          >
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="rounded-lg p-4 shadow"
                :style="{ background: 'var(--info-bg)', border: '1px solid var(--info-border)' }">
                <p class="text-sm font-semibold" :style="{ color: 'var(--focus-ring)' }">Job Designations</p>
                <p class="text-3xl font-bold mt-2" :style="{ color: 'var(--focus-ring)' }">{{ designations.length }}</p>
              </div>
              <div class="rounded-lg p-4 shadow"
                :style="{ background: 'var(--icon-bg-green)', border: '1px solid var(--icon-color-green)' }">
                <p class="text-sm font-semibold" :style="{ color: 'var(--icon-color-green)' }">Departments</p>
                <p class="text-3xl font-bold mt-2" :style="{ color: 'var(--icon-color-green)' }">{{ departments.length }}</p>
              </div>
              <div class="rounded-lg p-4 shadow"
                :style="{ background: 'var(--icon-bg-purple)', border: '1px solid var(--icon-color-purple)' }">
                <p class="text-sm font-semibold" :style="{ color: 'var(--icon-color-purple)' }">Job Roles</p>
                <p class="text-3xl font-bold mt-2" :style="{ color: 'var(--icon-color-purple)' }">{{ roles.length }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Tabs -->
        <section class="px-6 pb-6">
          <div
            class="rounded-xl shadow-sm overflow-hidden"
            :style="{
              background: 'var(--card-bg)',
              border: '1px solid var(--card-border)'
            }"
          >
            <!-- Tab Navigation -->
            <div
              class="flex flex-wrap"
              :style="{
                background: 'var(--item-bg)',
                borderBottom: '1px solid var(--card-border)'
              }"
            >
              <button
                v-for="tab in [
                  { key: 'designations', label: '💼 Job Designations' },
                  { key: 'departments',  label: '🏢 Departments' },
                  { key: 'roles',        label: '⭐ Job Roles' }
                ]"
                :key="tab.key"
                @click="activeTab = tab.key"
                class="px-6 py-4 font-semibold border-b-2 transition text-sm"
                :style="activeTab === tab.key
                  ? {
                      borderBottomColor: 'var(--focus-ring)',
                      color: 'var(--focus-ring)',
                      background: 'var(--card-bg)'
                    }
                  : {
                      borderBottomColor: 'transparent',
                      color: 'var(--text-muted)',
                      background: 'transparent'
                    }
                "
              >
                {{ tab.label }}
              </button>
            </div>

            <!-- Tab Content -->
            <div class="p-6">
              <div
                v-for="tab in [
                  { key: 'designations', label: 'Designation', items: filteredDesignations, all: designations, search: 'designationSearch', openFn: openDesignationModal, deleteFn: deleteDesignation, deleteKey: 'designation_name' },
                  { key: 'departments',  label: 'Department',  items: filteredDepartments, all: departments,  search: 'departmentSearch',  openFn: openDepartmentModal,  deleteFn: deleteDepartment,  deleteKey: 'department_name' },
                  { key: 'roles',        label: 'Role',        items: filteredRoles,        all: roles,        search: 'roleSearch',        openFn: openRoleModal,        deleteFn: deleteRole,        deleteKey: 'role_name' }
                ]"
                :key="tab.key"
                v-show="activeTab === tab.key"
                class="space-y-6"
              >
                <!-- Toolbar -->
                <div class="flex justify-between items-center gap-4">
                  <button
                    @click="tab.openFn()"
                    class="flex items-center gap-2 px-4 py-2 text-white rounded-lg transition text-sm font-semibold"
                    :style="{ background: 'var(--btn-primary)' }"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Add {{ tab.label }}
                  </button>
                  <input
                    v-model="$data[tab.search]"
                    type="text"
                    :placeholder="`Search ${tab.label.toLowerCase()}s...`"
                    class="px-4 py-2 rounded-lg focus:outline-none w-64 text-sm"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                  />
                </div>

                <!-- Table Card -->
                <div
                  class="rounded-xl shadow-sm overflow-hidden"
                  :style="{
                    background: 'var(--card-bg)',
                    border: '1px solid var(--card-border)'
                  }"
                >
                  <!-- Count Bar -->
                  <div
                    class="px-6 py-4"
                    :style="{
                      background: 'var(--item-bg)',
                      borderBottom: '1px solid var(--card-border)'
                    }"
                  >
                    <p class="text-sm font-semibold" :style="{ color: 'var(--text-sub)' }">
                      Showing {{ tab.items.length }} of {{ tab.all.length }} {{ tab.label.toLowerCase() }}s
                    </p>
                  </div>

                  <!-- Empty -->
                  <div v-if="tab.items.length === 0" class="text-center py-12">
                    <p :style="{ color: 'var(--text-muted)' }">
                      {{ tab.all.length === 0 ? `No ${tab.label.toLowerCase()}s yet` : 'No results found' }}
                    </p>
                  </div>

                  <!-- Table -->
                  <div v-else class="overflow-x-auto">
                    <table class="w-full">
                      <thead :style="{ background: 'var(--item-bg)' }">
                        <tr>
                          <th
                            v-for="col in ['#', tab.label, 'Actions']"
                            :key="col"
                            class="px-6 py-3 text-left text-sm font-semibold"
                            :style="{
                              color: 'var(--text-main)',
                              borderBottom: '1px solid var(--card-border)'
                            }"
                          >{{ col }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="(item, idx) in tab.items"
                          :key="item.id"
                          class="transition"
                          :style="{ borderBottom: '1px solid var(--card-border)' }"
                          @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                          @mouseleave="$event.currentTarget.style.background = 'transparent'"
                        >
                          <td class="px-6 py-4 text-sm font-medium" :style="{ color: 'var(--text-muted)' }">{{ idx + 1 }}</td>
                          <td class="px-6 py-4 text-sm font-medium" :style="{ color: 'var(--text-main)' }">{{ item.name }}</td>
                          <td class="px-6 py-4 text-sm">
                            <button
                              @click="tab.deleteFn(item[tab.deleteKey])"
                              class="rounded p-1 transition"
                              :style="{ color: 'var(--warning-border)' }"
                              @mouseover="$event.currentTarget.style.background = 'var(--warning-bg)'"
                              @mouseleave="$event.currentTarget.style.background = 'transparent'"
                              title="Delete"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                <line x1="10" y1="11" x2="10" y2="17"></line>
                                <line x1="14" y1="11" x2="14" y2="17"></line>
                              </svg>
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>
    </div>

    <!-- Reusable Modal Template -->
    <template v-for="modal in [
      {
        show: showDesignationModal,
        title: editingDesignationId ? 'Edit Designation' : 'Add Designation',
        model: designationForm,
        placeholder: 'Enter designation name',
        saveFn: saveDesignation,
        closeFn: () => showDesignationModal = false,
        saveLabel: editingDesignationId ? 'Update' : 'Save',
        error: null
      },
      {
        show: showDepartmentModal,
        title: editingDepartmentId ? 'Edit Department' : 'Add Department',
        model: departmentForm,
        placeholder: 'Enter department name',
        saveFn: saveDepartment,
        closeFn: () => showDepartmentModal = false,
        saveLabel: editingDepartmentId ? 'Update' : 'Save',
        error: modalError,
        company: company
      },
      {
        show: showRoleModal,
        title: editingRoleId ? 'Edit Role' : 'Add Role',
        model: roleForm,
        placeholder: 'Enter role name',
        saveFn: saveRole,
        closeFn: () => showRoleModal = false,
        saveLabel: editingRoleId ? 'Update' : 'Save',
        error: null
      }
    ]" :key="modal.title">
      <div
        v-if="modal.show"
        class="fixed inset-0 flex items-center justify-center z-50"
        style="background: rgba(0,0,0,0.5)"
      >
        <div
          class="rounded-xl shadow-lg p-8 max-w-md w-full mx-4"
          :style="{
            background: 'var(--card-bg)',
            border: '1px solid var(--card-border)'
          }"
        >
          <!-- Error -->
          <div
            v-if="modal.error"
            class="p-4 rounded-lg mb-4"
            :style="{
              background: 'var(--warning-bg)',
              border: '1px solid var(--warning-border)',
              color: 'var(--warning-border)'
            }"
          >
            <p class="font-semibold text-sm">❌ Error:</p>
            <p class="text-sm">{{ modal.error }}</p>
          </div>

          <h2 class="text-2xl font-bold mb-6" :style="{ color: 'var(--text-main)' }">
            {{ modal.title }}
          </h2>

          <!-- Company display (departments only) -->
          <div
            v-if="modal.company"
            class="w-full px-4 py-3 rounded-lg mb-6 text-sm"
            :style="{
              background: 'var(--item-bg)',
              color: 'var(--text-sub)',
              border: '1px solid var(--item-border)'
            }"
          >
            {{ modal.company }}
          </div>

          <input
            v-model="modal.model.name"
            type="text"
            :placeholder="modal.placeholder"
            class="w-full px-4 py-3 rounded-lg focus:outline-none mb-6 text-sm"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              border: '1px solid var(--input-border)'
            }"
          />

          <div class="flex gap-3">
            <button
              @click="modal.saveFn()"
              class="flex-1 px-4 py-2 text-white rounded-lg transition font-semibold text-sm"
              :style="{ background: 'var(--btn-primary)' }"
            >
              {{ modal.saveLabel }}
            </button>
            <button
              @click="modal.closeFn()"
              class="flex-1 px-4 py-2 rounded-lg transition font-semibold text-sm"
              :style="{
                background: 'var(--item-bg)',
                color: 'var(--text-main)',
                border: '1px solid var(--card-border)'
              }"
              @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
              @mouseleave="$event.currentTarget.style.background = 'var(--item-bg)'"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </template>


</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useStaffStore } from '@/stores/staff'
import { getDefaultCompany } from '@/services/api'
import Swal from 'sweetalert2'


// State
const modalError = ref("")
const loading = ref(false)
const company = ref('')
const router = useRouter()
const staffStore = useStaffStore()

// Tabs
const activeTab = ref('designations')

// Search filters
const designationSearch = ref('')
const departmentSearch = ref('')
const roleSearch = ref('')

// Designations
const showDesignationModal = ref(false)
const editingDesignationId = ref(null)
const designationForm = ref({ name: '' })
const designations = ref([])

// Departments
const departments = ref([])
const showDepartmentModal = ref(false)
const editingDepartmentId = ref(null)
const departmentForm = ref({ name: '' })

// Roles
const roles = ref([])
const showRoleModal = ref(false)
const editingRoleId = ref(null)
const roleForm = ref({ name: '' })

// Filtered Results
const filteredDesignations = computed(() => {
  return designations.value.filter(item =>
    item.name.toLowerCase().includes(designationSearch.value.toLowerCase())
  )
})

const filteredDepartments = computed(() => {
  return departments.value.filter(item =>
    item.name.toLowerCase().includes(departmentSearch.value.toLowerCase())
  )
})

const filteredRoles = computed(() => {
  return roles.value.filter(item =>
    item.name.toLowerCase().includes(roleSearch.value.toLowerCase())
  )
})

// Load Data Functions
const loadDesignations = async () => {
  try {
    const response = await staffStore.getDesignations()
    if (response && Array.isArray(response.data)) {
      designations.value = response.data
    } else {
      console.warn('No designations found')
    }
  } catch (e) {
    console.error('Failed to load designations', e)
  }
}

const loadDepartments = async () => {
  try {
    const request = await staffStore.getDepartments(company.value)
    if (request && Array.isArray(request.data)) {
      departments.value = request.data
    } else {
      console.warn('No departments found for company:', company.value)
    }
  } catch (e) {
    console.error('Failed to load departments', e)
  }
}

const loadRoles = async () => {
  try {
    const response = await staffStore.getRoles()
    if (response && Array.isArray(response.data)) {
      roles.value = response.data
    } else {
      console.warn('No roles found')
    }
  } catch (e) {
    console.error('Failed to load roles', e)
  }
}

// Modal Open Functions
const openDesignationModal = () => {
  showDesignationModal.value = true
  editingDesignationId.value = null
  designationForm.value = { name: '' }
}

const openDepartmentModal = () => {
  showDepartmentModal.value = true
  editingDepartmentId.value = null
  departmentForm.value = { name: '' }
}

const openRoleModal = () => {
  showRoleModal.value = true
  editingRoleId.value = null
  roleForm.value = { name: '' }
}

// Save Functions
const saveDesignation = async() => {
  if (!designationForm.value.name.trim()) {
    window.$toast?.warning('Please enter a designation name')
    return
  }

  try {
    loading.value = true
    modalError.value = ""

    const designationData = {
      designation_name: designationForm.value.name,
    }
    const response = await staffStore.createDesignation(designationData)

    if (response.status === 'success') {
      await Swal.fire({
        title: "Designation Created",
        text: response?.message,
        icon: "success",
        timer: 1000,
        timerProgressBar: true,
        showConfirmButton: false
      })
      showDesignationModal.value = false
      designationForm.value = { name: '' }
      await loadDesignations()
    } else {
      modalError.value = response.message || 'Failed to create designation.'
    }
  } catch (error) {
    console.error('Error creating designation:', error)
    modalError.value = 'An error occurred. Please try again.'
  } finally {
    loading.value = false
  }
}

const saveDepartment = async() => {
  if (!departmentForm.value.name.trim()) {
    window.$toast?.warning('Please enter a department name')
    return
  }
  try {
    loading.value = true
    modalError.value = ""

    const departmentData = {
      department_name: departmentForm.value.name,
      company: company.value
    }

    const response = await staffStore.createDepartment(departmentData)

    if (response.status === 'success') {
      await Swal.fire({
        title: "Department Created",
        text: response?.message,
        icon: "success",
        timer: 1000,
        timerProgressBar: true,
        showConfirmButton: false
      })
      showDepartmentModal.value = false
      departmentForm.value = { name: '' }
      await loadDepartments()
    } else {
      modalError.value = response.message || 'Failed to create department.'
    }
  } catch (error) {
    console.error('Error creating department:', error)
    modalError.value = 'An error occurred. Please try again.'
  } finally {
    loading.value = false
  }
}

const saveRole = async() => {
  if (!roleForm.value.name.trim()) {
    window.$toast?.warning('Please enter a role name')
    return
  }
  try {
    loading.value = true
    modalError.value = ""

    const roleData = {
      role_name: roleForm.value.name,
    }
    const response = await staffStore.createRole(roleData)

    if (response.status === 'success') {
      await Swal.fire({
        title: "Role Created",
        text: response?.message,
        icon: "success",
        timer: 1000,
        timerProgressBar: true,
        showConfirmButton: false
      })
      showRoleModal.value = false
      roleForm.value = { name: '' }
      await loadRoles()
    } else {
      modalError.value = response.message || 'Failed to create role.'
    }
  } catch (error) {
    console.error('Error creating role:', error)
    modalError.value = 'An error occurred. Please try again.'
  } finally {
    loading.value = false
  }
}

// Delete Functions
const deleteDesignation = async (designationId) => {
  if (confirm('Are you sure you want to delete this designation?')) {
    try {
      const response = await staffStore.deleteDesignation(designationId)

      if (response.status === 'success') {
        await Swal.fire({
          title: "Deleted",
          text: response?.message,
          icon: "success",
          timer: 1000,
          timerProgressBar: true,
          showConfirmButton: false
        })
        await loadDesignations()
      } else {
        modalError.value = response.message || 'Failed to delete designation.'
      }
    } catch (error) {
      console.error('Error deleting designation:', error)
    }
  }
}

const deleteDepartment = async (departmentName) => {
  try {
    const result = await Swal.fire({
      title: 'Confirm Deletion',
      text: `Are you sure you want to delete department: ${departmentName}?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, delete it!',
      cancelButtonText: 'Cancel',
      reverseButtons: true
    })

    if (result.isConfirmed) {
      const response = await staffStore.deleteDepartment(departmentName)

      if (response.status === 'success') {
        await Swal.fire({
          title: "Deleted",
          text: response?.message,
          icon: "success",
          timer: 1000,
          timerProgressBar: true,
          showConfirmButton: false
        })
        await loadDepartments()
      } else {
        modalError.value = response.message || 'Failed to delete department.'
      }
    }
  } catch (error) {
    console.error('Error deleting department:', error)
  }
}

const deleteRole = async (roleName) => {
  if (confirm('Are you sure you want to delete this role?')) {
    try {
      const response = await staffStore.deleteRole(roleName)

      if (response.status === 'success') {
        await Swal.fire({
          title: "Deleted",
          text: response?.message,
          icon: "success",
          timer: 1000,
          timerProgressBar: true,
          showConfirmButton: false
        })
        await loadRoles()
      } else {
        modalError.value = response.message || 'Failed to delete role.'
      }
    } catch (error) {
      console.error('Error deleting role:', error)
    }
  }
}

const goBack = () => {
  router.back()
}

// Computed
const totalItems = computed(
  () =>
    designations.value.length +
    departments.value.length +
    roles.value.length
)

// On Mount
onMounted(async () => {
  try {
    const res = await getDefaultCompany()
    company.value = res?.message || res || ''
    if (!company.value) {
      console.warn('No default company found')
    } else {
      await loadDesignations()
      await loadDepartments()
      await loadRoles()
    }
  } catch (e) {
    console.error('Failed to load company', e)
  }
})
</script>
