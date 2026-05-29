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
              <h1 class="text-lg font-bold" :style="{ color: 'var(--text-main)' }">Staff Management</h1>
              <p :style="{ color: 'var(--text-muted)' }">{{ staff.length }} registered employees</p>
            </div>
            <button
              @click="openCreateModal"
              class="flex items-center gap-2 px-4 py-2 text-white rounded-lg transition"
              :style="{ background: 'var(--btn-primary)' }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
                <line x1="12" y1="12" x2="12" y2="18"></line>
                <line x1="9" y1="15" x2="15" y2="15"></line>
              </svg>
              New Employee
            </button>
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
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">

              <!-- Total -->
              <div
                class="rounded-lg p-4 shadow"
                :style="{
                  background: 'var(--info-bg)',
                  border: '1px solid var(--info-border)'
                }"
              >
                <p class="text-sm font-semibold" :style="{ color: 'var(--focus-ring)' }">Total Employees</p>
                <p class="text-3xl font-bold mt-2" :style="{ color: 'var(--focus-ring)' }">{{ staff.length }}</p>
              </div>

              <!-- Active -->
              <div
                class="rounded-lg p-4 shadow"
                :style="{
                  background: 'var(--icon-bg-green)',
                  border: '1px solid var(--icon-color-green)'
                }"
              >
                <p class="text-sm font-semibold" :style="{ color: 'var(--icon-color-green)' }">Active Employees</p>
                <p class="text-3xl font-bold mt-2" :style="{ color: 'var(--icon-color-green)' }">{{ activeStaff }}</p>
              </div>

              <!-- Average Salary -->
              <div
                class="rounded-lg p-4 shadow"
                :style="{
                  background: 'var(--icon-bg-purple)',
                  border: '1px solid var(--icon-color-purple)'
                }"
              >
                <p class="text-sm font-semibold" :style="{ color: 'var(--icon-color-purple)' }">Average Salary</p>
                <p class="text-3xl font-bold mt-2" :style="{ color: 'var(--icon-color-purple)' }">
                  {{ formatCurrency(averageSalary, currencyCode, locale) }}
                </p>
              </div>

              <!-- Total Salaries -->
              <div
                class="rounded-lg p-4 shadow"
                :style="{
                  background: 'var(--warning-bg)',
                  border: '1px solid var(--warning-border)'
                }"
              >
                <p class="text-sm font-semibold" :style="{ color: 'var(--warning-border)' }">Total Salaries</p>
                <p class="text-3xl font-bold mt-2" :style="{ color: 'var(--warning-border)' }">
                  {{ formatCurrency(totalSalaries, currencyCode, locale) }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <!-- Filters and Search -->
        <section class="px-6 pb-6">
          <div
            class="rounded-xl shadow-sm p-6"
            :style="{
              background: 'var(--card-bg)',
              border: '1px solid var(--card-border)'
            }"
          >
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">

              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by name or employee ID..."
                class="px-4 py-2 rounded-lg focus:outline-none transition-all"
                :style="{
                  background: 'var(--input-bg)',
                  color: 'var(--text-main)',
                  border: '1px solid var(--input-border)'
                }"
              />

              <select
                v-model="departmentFilter"
                class="px-4 py-2 rounded-lg focus:outline-none transition-all"
                :style="{
                  background: 'var(--input-bg)',
                  color: 'var(--text-main)',
                  border: '1px solid var(--input-border)'
                }"
              >
                <option value="">All Departments</option>
                <option v-for="dept in departments" :key="dept.name" :value="dept.name">{{ dept.name }}</option>
              </select>

              <select
                v-model="statusFilter"
                class="px-4 py-2 rounded-lg focus:outline-none transition-all"
                :style="{
                  background: 'var(--input-bg)',
                  color: 'var(--text-main)',
                  border: '1px solid var(--input-border)'
                }"
              >
                <option value="">All Statuses</option>
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
                <option value="Left">Left</option>
              </select>

              <select
                v-model="sortBy"
                class="px-4 py-2 rounded-lg focus:outline-none transition-all"
                :style="{
                  background: 'var(--input-bg)',
                  color: 'var(--text-main)',
                  border: '1px solid var(--input-border)'
                }"
              >
                <option value="recent">Most Recent</option>
                <option value="name">Name</option>
                <option value="salary">Salary</option>
                <option value="department">Department</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Staff Table -->
        <section class="px-6 pb-6">
          <div
            class="rounded-xl shadow-sm overflow-hidden"
            :style="{
              background: 'var(--card-bg)',
              border: '1px solid var(--card-border)'
            }"
          >
            <!-- Table Header Bar -->
            <div
              class="px-6 py-4"
              :style="{
                background: 'var(--item-bg)',
                borderBottom: '1px solid var(--card-border)'
              }"
            >
              <p class="text-sm font-semibold" :style="{ color: 'var(--text-sub)' }">
                Showing {{ filteredStaff.length }} of {{ staff.length }} staff members
              </p>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full">
                <thead :style="{ background: 'var(--item-bg)' }">
                  <tr>
                    <th
                      v-for="col in ['Name','Employee ID','Department','Position','Salary','Status','Actions']"
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
                    v-for="member in paginatedStaff"
                    :key="member.id"
                    class="transition"
                    :style="{ borderBottom: '1px solid var(--card-border)' }"
                    @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                    @mouseleave="$event.currentTarget.style.background = 'transparent'"
                  >
                    <td @click="navigateTo('StaffProfile', member.name)"
                      class="px-6 py-4 text-sm cursor-pointer" :style="{ color: 'var(--text-sub)' }">
                      {{ member.employee_name }}
                    </td>
                    <td @click="navigateTo('StaffProfile', member.name)"
                      class="px-6 py-4 text-sm font-medium cursor-pointer" :style="{ color: 'var(--text-main)' }">
                      #{{ member.name }}
                    </td>
                    <td class="px-6 py-4 text-sm" :style="{ color: 'var(--text-sub)' }">
                      {{ getDepartmentLabel(member.department) }}
                    </td>
                    <td class="px-6 py-4 text-sm" :style="{ color: 'var(--text-sub)' }">
                      {{ member.designation }}
                    </td>
                    <td class="px-6 py-4 text-sm font-semibold" :style="{ color: 'var(--text-main)' }">
                      {{ formatCurrency(member.salary, currencyCode, locale) }}
                    </td>
                    <td class="px-6 py-4 text-sm">
                      <span :class="getStatusClass(member.status)" class="px-2 py-1 rounded text-xs font-semibold">
                        {{ getStatusLabel(member.status) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm space-x-2">
                      <button @click="viewStaff(member)"
                        class="transition rounded p-1"
                        :style="{ color: 'var(--focus-ring)' }"
                        @mouseover="$event.currentTarget.style.background = 'var(--info-bg)'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                        title="View Profile"
                      ><Eye class="w-5 h-5" /></button>
                      <button @click="editStaff(member)"
                        class="transition rounded p-1"
                        :style="{ color: 'var(--warning-border)' }"
                        @mouseover="$event.currentTarget.style.background = 'var(--warning-bg)'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                        title="Edit"
                      ><Edit2 class="w-5 h-5" /></button>
                      <button @click="deleteStaff(member.name)"
                        class="transition rounded p-1"
                        :style="{ color: 'var(--warning-border)' }"
                        @mouseover="$event.currentTarget.style.background = 'var(--warning-bg)'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                        title="Delete"
                      ><Trash2 class="w-5 h-5" /></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Empty State -->
            <div v-if="filteredStaff.length === 0" class="text-center py-12">
              <p :style="{ color: 'var(--text-muted)' }">No matching employees found</p>
            </div>

            <!-- Pagination Footer -->
            <div
              class="px-6 py-4 flex items-center justify-between"
              :style="{
                background: 'var(--item-bg)',
                borderTop: '1px solid var(--card-border)'
              }"
            >
              <p class="text-sm" :style="{ color: 'var(--text-sub)' }">
                Showing {{ startIndex + 1 }}-{{ Math.min(endIndex, filteredStaff.length) }}
                of {{ filteredStaff.length }} employees
              </p>
              <div class="flex items-center gap-2">

                <button
                  @click="previousPage"
                  :disabled="currentPage === 1"
                  class="px-3 py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  :style="{
                    border: '1px solid var(--card-border)',
                    color: 'var(--text-sub)',
                    background: 'var(--card-bg)'
                  }"
                  @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                  @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                >← Previous</button>

                <div class="flex items-center gap-1">
                  <button
                    v-for="page in totalPages"
                    :key="page"
                    @click="goToPage(page)"
                    class="px-3 py-2 rounded-lg transition text-sm"
                    :style="currentPage === page
                      ? { background: 'var(--btn-primary)', color: '#fff', border: 'none' }
                      : { border: '1px solid var(--card-border)', color: 'var(--text-sub)', background: 'var(--card-bg)' }
                    "
                  >{{ page }}</button>
                </div>

                <button
                  @click="nextPage"
                  :disabled="currentPage === totalPages"
                  class="px-3 py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  :style="{
                    border: '1px solid var(--card-border)',
                    color: 'var(--text-sub)',
                    background: 'var(--card-bg)'
                  }"
                  @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                  @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                >Next →</button>
              </div>
            </div>
          </div>
        </section>

      </main>
    </div>

    <!-- Modals -->
    <StaffModal
      v-if="showModal"
      :staff="editingStaff"
      :departments="departments"
      :designations="designations"
      :genders="genders"
      @save="saveStaff"
      :error="modalError"
      @close="showModal = false"
    />
    <StaffProfileModal
      v-if="showProfileModal"
      :salaryHistory="salaryHistory"
      :attendanceRecords="attendanceRecords"
      :staff="selectedStaff"
      @close="() => { showProfileModal = false; salaryHistory = []; attendanceRecords = [] }"
    />

</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import router from '@/router'
import StaffModal from '@/components/modals/StaffModal.vue'
import StaffProfileModal from '@/components/modals/StaffProfileModal.vue'

import { Users, Plus, Download, Edit2, Eye, Trash2, ArrowLeft } from 'lucide-vue-next'
import { formatCurrency } from '@/utils/formatters.js'
import { useSettingsStore } from '@/stores/settings.js'
import { useStaffStore } from '@/stores/staff'

/* =========================
   Lifecycle Hooks
========================= */
onMounted(async() => {
    await loadStaff()
    await loadDepartments()
    await loadDesgniations()
    loadGenders()
})

/* =========================
   Store
========================= */
const staffStore = useStaffStore()

/* =========================
   State
========================= */
const staff = ref([])
const loadStaff = async () => {
  try {
    await staffStore.fetchStaff()
    staff.value = staffStore.staff
  } catch (error) {
    console.error("Error loading staff:", error)
  }
}

const departments = ref([])
const loadDepartments = async () => {
  try {
    const response = await staffStore.getDepartments()
    if (response.status === 'error') {
      console.error("Error loading departments:", response.message)
      return
    }else{
      console.log("Departments loaded:", response)
      departments.value = response.data
    }
  } catch (error) {
    console.error("Error loading departments:", error)
  }
}

const genders = ref([])

const loadGenders = () => {
  genders.value = ["Male", "Female"]
}

const designations = ref([])
const loadDesgniations = async () => {
  try {
    const response = await staffStore.getDesignations()
    if (response.status === 'error') {
      console.error("Error loading designations:", response.message)
      return
    }else{
      console.log("Designations loaded:", response)
      designations.value = response.data
    }
  } catch (error) {
    console.error("Error loading designations:", error)
  }
}
/* =========================
   Filters & Modals
========================= */


const searchQuery = ref('')
const departmentFilter = ref('')
const statusFilter = ref('')
const sortBy = ref('recent')

const showModal = ref(false)
const showProfileModal = ref(false)
const editingStaff = ref(null)
const selectedStaff = ref(null)

const currentPage = ref(1)
const itemsPerPage = ref(8)

const modalError = ref('')
/* =========================
   Computed
========================= */
const filteredStaff = computed(() => {
  let filtered = staff.value.filter(s => {
    const matchSearch =
      !searchQuery.value ||
      s.name.includes(searchQuery.value) ||
      s.employee_name.includes(searchQuery.value)

    const matchDepartment =
      !departmentFilter.value || s.department === departmentFilter.value

    const matchStatus =
      !statusFilter.value || s.status === statusFilter.value

    return matchSearch && matchDepartment && matchStatus
  })

  if (sortBy.value === 'name') {
    filtered.sort((a, b) => a.name.localeCompare(b.name, 'ar'))
  } else if (sortBy.value === 'salary') {
    filtered.sort((a, b) => b.salary - a.salary)
  } else if (sortBy.value === 'department') {
    filtered.sort((a, b) => a.department.localeCompare(b.department, 'ar'))
  } else {
    filtered.sort((a, b) => new Date(b.joinDate) - new Date(a.joinDate))
  }

  return filtered
})

const activeStaff = computed(
  () => staff.value.filter(s => s.status === 'Active').length
)

const totalSalaries = computed(
  () => staff.value.reduce((sum, s) => sum + s.salary, 0)
)

const averageSalary = computed(() =>
  staff.value.length ? totalSalaries.value / staff.value.length : 0
)

/* =========================
   Pagination
========================= */
const totalPages = computed(() =>
  Math.ceil(filteredStaff.value.length / itemsPerPage.value)
)

const startIndex = computed(() =>
  (currentPage.value - 1) * itemsPerPage.value
)

const endIndex = computed(() =>
  startIndex.value + itemsPerPage.value
)

const paginatedStaff = computed(() =>
  filteredStaff.value.slice(startIndex.value, endIndex.value)
)

/* =========================
   Methods
========================= */
const getDepartmentLabel = dept => ({
  sales: "المبيعات",
  warehouse: "المستودع",
  cashier: "الكاشيرز",
  management: "الإدارة",
}[dept] || dept)

const getStatusClass = status => ({
  Active: "bg-green-100 text-green-800",
  Inactive: "bg-gray-100 text-gray-800",
  Left: "bg-yellow-100 text-yellow-800",
}[status] || "bg-gray-100 text-gray-800")

const getStatusLabel = status => ({
  Active: "نشط",
  Inactive: "غير نشط",
  Left: "مغادر",
}[status] || status)

const openCreateModal = () => {
  editingStaff.value = null
  showModal.value = true
}

const editStaff = member => {
  console.log("Editing staff:", member)
  editingStaff.value = { ...member }
  editingStaff.value.gender = member.gender;
  editingStaff.value.department = member.department;
  editingStaff.value.middle_name = member.middle_name || '';
  // editStaff.value.salary = Number(member.salary);
  console.log("mmmmm", editingStaff.value)
  showModal.value = true
}

const viewStaff = async (member) => {
  selectedStaff.value = member
  showProfileModal.value = true

  // تحميل سجل الرواتب
  await employeeSalaryHistory(member.name)
  await employeeAttendance(member.name)
}


const deleteStaff = async(name) => {
  if (confirm('هل تريد حذف هذا الموظف؟')) {
     try {
        const request = await staffStore.deleteStaff(name)
        // Update local list
        if (request.status === 'success') {
            console.log("Employee deleted successfully")
            await loadStaff()
        }else{
          console.error("Error deleting staff:", request.message)
        }

    } catch (err) {
        console.error("Error deleting staff:", err)
      }
  }
}
// In StaffManagement.vue - Update the saveStaff method

const saveStaff = async (member) => {
  try {
    // Call the store
    modalError.value = ''
    const response = await staffStore.createStaff(member)

    console.log("Save Staff Response:", response)

    // Check response status
    if (response.status === 'error') {
      // Show error in modal - don't close it
      modalError.value = response.message
    }else{
      console.log("Employee saved successfully:", response)
      showModal.value = false

      // Refresh staff list
      await loadStaff()
    }

    // Success - update local list and close modal
    // if (member.id) {
    //   // Update existing
    //   const index = staff.value.findIndex(s => s.id === member.id)
    //   if (index !== -1) {
    //     staff.value[index] = member
    //   }
    // } else {
    //   // Add new
    //   member.id = Math.max(...staff.value.map(s => s.id), 0) + 1
    //   staff.value.push(member)
    // }

    // Close modal on success

    // console.log("Employee saved successfully:", response.message)
    // Optional: Show success notification
  } catch (err) {
    console.error("Error saving staff:", err)
    modalError.value = err?.message || "حدث خطأ أثناء حفظ البيانات"
  }
}
//
const salaryHistory = ref([])
const employeeSalaryHistory = async (employeeName) => {
  try {
    const response = await staffStore.getStaffSalaryHistory(employeeName)
    if (response.status === 'error') {
      console.error("Error fetching salary history:", response.message)
      return []
    } else {
      console.log("Salary history fetched:", response)
      salaryHistory.value = response.data
      return response.data
    }
  } catch (error) {
    console.error("Error fetching salary history:", error)
    return []
  }
}
const attendanceRecords = ref([])
const employeeAttendance = async (employeeName) => {
  try {
    const response = await staffStore.getStaffAttendance(employeeName)
    if (response.status === 'error') {
      console.error("Error fetching attendance:", response.message)
      return []
    } else {
      console.log("Attendance fetched:", response)
      attendanceRecords.value = response.data
      return response.data
    }
  } catch (error) {
    console.error("Error fetching attendance:", error)
    return []
  }
}

const previousPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const goToPage = page => {
  currentPage.value = page
}

const navigateTo = (route, staffName) => {
  router.push({ name: route, params: { staff_name: staffName } })
}

const goBack = () => {
  router.back()
}
/* =========================
   Settings
========================= */
const settingsStore = useSettingsStore()
const currencyCode =
  settingsStore?.settings?.store?.currencyCode || 'PKR'
const locale =
  settingsStore?.settings?.store?.locale || 'en-PK'



</script>

<style scoped>
/* الستايل موجود في Tailwind CSS */
</style>
