<!-- ShiftList.vue -->
<template>

    <div class="w-full flex" style="font-size: 13px;" :style="{ background: 'var(--item-bg)' }">
      <main class="flex flex-col flex-1">

        <!-- Header -->
        <header
          class="mx-3 mt-3 sticky top-0 z-10 rounded-lg shadow-sm"
          :style="{
            background: 'var(--card-bg)',
            border: '1px solid var(--card-border)'
          }"
        >
          <div class="px-4 py-2 flex justify-between items-center">
            <div class="flex items-center gap-2">
              <ShiftsIcon class="w-5 h-5" :style="{ color: 'var(--focus-ring)' }" />
              <h1 class="text-sm font-bold" :style="{ color: 'var(--text-main)' }">Shifts</h1>
            </div>
            <div class="flex gap-2">
              <button @click="exportShifts" :disabled="isLoading"
                class="inline-flex items-center gap-1.5 text-white px-3 py-1.5 rounded-md text-xs transition-colors disabled:opacity-50"
                :style="{ background: 'var(--text-muted)' }"
              >
                <ExportIcon class="w-3 h-3" /> Export
              </button>
              <button @click="viewCurrentShift" :disabled="isLoading"
                class="inline-flex items-center gap-1.5 text-white px-3 py-1.5 rounded-md text-xs transition-colors disabled:opacity-50"
                :style="{ background: 'var(--focus-ring)' }"
              >
                <RefreshIcon class="w-3 h-3" /> Refresh
              </button>
            </div>
          </div>
        </header>

        <!-- Statistics -->
        <section class="px-3 pt-3">
          <div
            class="rounded-lg shadow-sm p-3"
            :style="{
              background: 'var(--card-bg)',
              border: '1px solid var(--card-border)'
            }"
          >
            <h2 class="text-xs font-semibold uppercase tracking-wide mb-2" :style="{ color: 'var(--text-muted)' }">
              Statistics
            </h2>
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
              <StatsCard title="Today Shift"   :value="statistics.today_shifts"  icon="BarChart3"  color="blue" />
              <StatsCard title="This Week"     :value="statistics.week_shifts"   icon="DollarSign" color="green" />
              <StatsCard title="This Month"    :value="statistics.month_shifts"  icon="TrendingUp" color="purple" />
              <StatsCard title="Average Sales" :value="statistics.average_sales" icon="DollarSign" color="orange" />
            </div>
          </div>
        </section>

        <!-- Filters -->
        <section class="px-3 pt-3">
          <div
            class="rounded-lg shadow-sm p-3"
            :style="{
              background: 'var(--card-bg)',
              border: '1px solid var(--card-border)'
            }"
          >
            <div class="grid grid-cols-2 md:grid-cols-5 gap-2 mb-2">

              <!-- Search -->
              <div class="col-span-2">
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Search</label>
                <div class="relative">
                  <SearchIcon class="absolute left-2.5 top-2 w-3 h-3 pointer-events-none" :style="{ color: 'var(--text-muted)' }" />
                  <input v-model="searchQuery" @input="searchShifts" type="text"
                    class="w-full pl-8 pr-3 py-1.5 rounded-md focus:outline-none text-xs transition-all"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                    placeholder="Shift name, cashier..."
                  />
                </div>
              </div>

              <!-- From -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">From</label>
                <input v-model="filters.date_from" @change="applyFilters" type="date"
                  class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
                  :style="{
                    background: 'var(--input-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--input-border)'
                  }"
                />
              </div>

              <!-- To -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">To</label>
                <input v-model="filters.date_to" @change="applyFilters" type="date"
                  class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
                  :style="{
                    background: 'var(--input-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--input-border)'
                  }"
                />
              </div>

              <!-- Count -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Count</label>
                <div
                  class="px-2 py-1.5 rounded-md font-semibold text-xs"
                  :style="{
                    background: 'var(--item-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--item-border)'
                  }"
                >
                  {{ filteredShifts.length }} shifts
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-3 gap-2">

              <!-- Status -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Status</label>
                <select v-model="filters.status" @change="applyFilters"
                  class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
                  :style="{
                    background: 'var(--input-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--input-border)'
                  }"
                >
                  <option value="">All Status</option>
                  <option value="open">Open</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <!-- Cashier -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Cashier</label>
                <select v-model="filters.cashier" @change="applyFilters"
                  class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
                  :style="{
                    background: 'var(--input-bg)',
                    color: 'var(--text-main)',
                    border: '1px solid var(--input-border)'
                  }"
                >
                  <option value="">All Cashiers</option>
                  <option v-for="c in uniqueCashiers" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>

              <!-- Clear Filters -->
              <div class="flex items-end">
                <button @click="resetFilters"
                  class="w-full px-3 py-1.5 rounded-md text-xs transition-colors"
                  :style="{
                    background: 'var(--item-bg)',
                    color: 'var(--text-sub)',
                    border: '1px solid var(--item-border)'
                  }"
                  @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                  @mouseleave="$event.currentTarget.style.background = 'var(--item-bg)'"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Table -->
        <section class="px-3 pt-3 pb-3">
          <div
            class="rounded-lg shadow-sm flex flex-col overflow-hidden"
            :style="{
              background: 'var(--card-bg)',
              border: '1px solid var(--card-border)'
            }"
          >
            <!-- Table Header Bar -->
            <div
              class="px-4 py-2 flex items-center gap-2"
              :style="{ borderBottom: '1px solid var(--card-border)' }"
            >
              <ShiftsIcon class="w-4 h-4" :style="{ color: 'var(--text-muted)' }" />
              <span class="text-xs font-semibold" :style="{ color: 'var(--text-sub)' }">All Shifts</span>
              <span class="text-xs" :style="{ color: 'var(--text-muted)' }">({{ shifts.length }})</span>
              <span class="ml-1 text-xs flex items-center gap-1" :style="{ color: 'var(--text-muted)' }">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                Click row for details
              </span>
              <span v-if="isLoading" class="text-xs ml-auto" :style="{ color: 'var(--text-muted)' }">Loading...</span>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto" style="scrollbar-width: thin;">
              <table class="w-full border-collapse" style="font-size: 12px; min-width: 650px;">

                <!-- Table Head -->
                <thead
                  class="sticky top-0 z-10"
                  :style="{ background: 'var(--item-bg)' }"
                >
                  <tr>
                    <th class="w-6 px-2 py-2" :style="{ borderBottom: '1px solid var(--card-border)' }"></th>
                    <th v-for="label in ['Shift','Opened By','Date','Total Sales','Invoices','Status','Actions']"
                      :key="label"
                      class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide whitespace-nowrap"
                      :class="['Total Sales','Invoices','Status','Actions'].includes(label) ? 'text-center' : ''"
                      :style="{
                        color: 'var(--text-muted)',
                        borderBottom: '1px solid var(--card-border)'
                      }"
                    >
                      {{ label }}
                    </th>
                  </tr>
                </thead>

                <tbody>
                  <template v-for="shift in paginatedShifts" :key="shift.name">

                    <!-- Main Row -->
                    <tr
                      class="transition-colors cursor-pointer"
                      :style="{
                        background: expandedRows.has(shift.name) ? 'var(--choice-active-bg)' : 'var(--card-bg)',
                        borderBottom: '1px solid var(--card-border)'
                      }"
                      @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                      @mouseleave="$event.currentTarget.style.background = expandedRows.has(shift.name) ? 'var(--choice-active-bg)' : 'var(--card-bg)'"
                      @click="toggleRow(shift.name)"
                    >
                      <!-- Arrow -->
                      <td class="px-2 py-2 text-center">
                        <svg class="w-3 h-3 transition-transform duration-200 mx-auto"
                          :class="expandedRows.has(shift.name) ? 'rotate-90' : ''"
                          :style="{ color: 'var(--text-muted)' }"
                          fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                        </svg>
                      </td>

                      <!-- Shift Name -->
                      <td class="px-3 py-2 whitespace-nowrap">
                        <div class="flex items-center gap-2">
                          <div
                            class="w-6 h-6 rounded flex items-center justify-center flex-shrink-0"
                            :style="{ background: 'var(--info-bg)' }"
                          >
                            <ShiftsIcon class="w-3.5 h-3.5" :style="{ color: 'var(--focus-ring)' }" />
                          </div>
                          <div>
                            <div class="font-medium" :style="{ color: 'var(--text-main)' }">{{ shift.name }}</div>
                            <div style="font-size:10px;" :style="{ color: 'var(--text-muted)' }">
                              {{ shift.duration || 'In Progress' }}
                            </div>
                          </div>
                        </div>
                      </td>

                      <!-- Opened By -->
                      <td class="px-3 py-2 whitespace-nowrap">
                        <div class="flex items-center gap-1.5">
                          <div
                            class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 font-semibold"
                            style="font-size:10px;"
                            :style="{
                              background: 'var(--item-bg)',
                              color: 'var(--text-sub)',
                              border: '1px solid var(--item-border)'
                            }"
                          >
                            {{ shift.user?.slice(0, 1).toUpperCase() }}
                          </div>
                          <span :style="{ color: 'var(--text-sub)' }">{{ shift.user }}</span>
                        </div>
                      </td>

                      <!-- Date -->
                      <td class="px-3 py-2 whitespace-nowrap" :style="{ color: 'var(--text-muted)' }">
                        {{ shift.posting_date }}
                      </td>

                      <!-- Total Sales -->
                      <td class="px-3 py-2 whitespace-nowrap text-right font-semibold" :style="{ color: 'var(--focus-ring)' }">
                        {{ formatCurrency(shift.total_sales, currencyCode, locale) }}
                      </td>

                      <!-- Invoices -->
                      <td class="px-3 py-2 whitespace-nowrap text-center">
                        <span v-if="shift.invoices?.length"
                          class="inline-flex items-center justify-center w-5 h-5 text-white rounded-full font-semibold"
                          style="font-size:10px;"
                          :style="{ background: 'var(--focus-ring)' }"
                        >
                          {{ shift.invoices.length }}
                        </span>
                        <span v-else :style="{ color: 'var(--text-muted)' }">—</span>
                      </td>

                      <!-- Status -->
                      <td class="px-3 py-2 whitespace-nowrap text-center">
                        <span
                          class="inline-flex items-center px-2 py-0.5 rounded-full font-medium"
                          style="font-size:10px;"
                          :style="shift.status === 'Open'
                            ? { background: 'var(--icon-bg-green)', color: 'var(--icon-color-green)' }
                            : { background: 'var(--item-bg)', color: 'var(--text-muted)' }
                          "
                        >
                          <span
                            class="w-1.5 h-1.5 rounded-full mr-1 inline-block"
                            :style="{ background: shift.status === 'Open' ? 'var(--icon-color-green)' : 'var(--text-muted)' }"
                          />
                          {{ shift.status === 'Open' ? 'Open' : 'Closed' }}
                        </span>
                      </td>

                      <!-- Actions -->
                      <td class="px-3 py-2 whitespace-nowrap" @click.stop>
                        <div class="flex items-center justify-center gap-1">
                          <button @click="viewShift(shift.name)"
                            class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                            :style="{ color: 'var(--focus-ring)' }"
                            @mouseover="$event.currentTarget.style.background = 'var(--info-bg)'"
                            @mouseleave="$event.currentTarget.style.background = 'transparent'"
                            title="View"
                          >
                            <Eye class="w-3.5 h-3.5" />
                          </button>
                          <button @click="printShift(shift.name)"
                            class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                            :style="{ color: 'var(--icon-color-green)' }"
                            @mouseover="$event.currentTarget.style.background = 'var(--icon-bg-green)'"
                            @mouseleave="$event.currentTarget.style.background = 'transparent'"
                            title="Print"
                          >
                            <PrintIcon class="w-3.5 h-3.5" />
                          </button>
                          <button v-if="shift.status === 'Open'" @click="closeShift(shift.name)"
                            class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                            :style="{ color: 'var(--warning-border)' }"
                            @mouseover="$event.currentTarget.style.background = 'var(--warning-bg)'"
                            @mouseleave="$event.currentTarget.style.background = 'transparent'"
                            title="Close"
                          >
                            <DeleteIcon class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>

                    <!-- Expanded Detail Row -->
                    <tr v-if="expandedRows.has(shift.name)">
                      <td colspan="8"
                        class="px-4 py-3"
                        :style="{
                          background: 'var(--item-bg)',
                          borderBottom: '1px solid var(--card-border)'
                        }"
                      >
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-2">

                          <!-- Closing Info -->
                          <div
                            class="rounded-md p-2.5"
                            :style="{
                              background: 'var(--card-bg)',
                              border: '1px solid var(--card-border)'
                            }"
                          >
                            <div class="text-xs font-semibold uppercase tracking-wide mb-2" :style="{ color: 'var(--text-muted)' }">
                              Closing Info
                            </div>
                            <div class="space-y-1.5">
                              <div class="flex justify-between items-center">
                                <span style="font-size:11px;" :style="{ color: 'var(--text-muted)' }">Closing Date</span>
                                <span class="font-medium" style="font-size:11px;" :style="{ color: 'var(--text-sub)' }">
                                  {{ shift.closing_shift?.posting_date || '—' }}
                                </span>
                              </div>
                              <div class="flex justify-between items-center">
                                <span style="font-size:11px;" :style="{ color: 'var(--text-muted)' }">Closed By</span>
                                <span class="font-medium" style="font-size:11px;" :style="{ color: 'var(--text-sub)' }">
                                  {{ shift.closed_by_name || '—' }}
                                </span>
                              </div>
                            </div>
                          </div>

                          <!-- Balances -->
                          <div
                            class="rounded-md p-2.5"
                            :style="{
                              background: 'var(--card-bg)',
                              border: '1px solid var(--card-border)'
                            }"
                          >
                            <div class="text-xs font-semibold uppercase tracking-wide mb-2" :style="{ color: 'var(--text-muted)' }">
                              Balances
                            </div>
                            <div class="space-y-1.5">
                              <div class="flex justify-between items-center">
                                <span style="font-size:11px;" :style="{ color: 'var(--text-muted)' }">Opening</span>
                                <span class="font-semibold" style="font-size:11px;" :style="{ color: 'var(--text-sub)' }">
                                  {{ formatCurrency(shift.total_opening_cash, currencyCode, locale) }}
                                </span>
                              </div>
                              <div class="flex justify-between items-center">
                                <span style="font-size:11px;" :style="{ color: 'var(--text-muted)' }">Closing</span>
                                <span class="font-semibold" style="font-size:11px;" :style="{ color: 'var(--text-sub)' }">
                                  {{ shift.closing_shift
                                    ? formatCurrency(shift.closing_shift.closing_balance?.find(c => c.mode_of_payment === 'Cash')?.closing_amount || 0, currencyCode, locale)
                                    : '—' }}
                                </span>
                              </div>
                            </div>
                          </div>

                          <!-- Duration -->
                          <div
                            class="rounded-md p-2.5"
                            :style="{
                              background: 'var(--card-bg)',
                              border: '1px solid var(--card-border)'
                            }"
                          >
                            <div class="text-xs font-semibold uppercase tracking-wide mb-2" :style="{ color: 'var(--text-muted)' }">
                              Duration
                            </div>
                            <div class="flex items-center gap-1.5 mt-1">
                              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" :style="{ color: 'var(--text-muted)' }">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                              </svg>
                              <span class="font-medium" style="font-size:12px;" :style="{ color: 'var(--text-sub)' }">
                                {{ shift.duration || 'In Progress' }}
                              </span>
                            </div>
                          </div>

                          <!-- Quick Actions -->
                          <div
                            class="rounded-md p-2.5"
                            :style="{
                              background: 'var(--card-bg)',
                              border: '1px solid var(--card-border)'
                            }"
                          >
                            <div class="text-xs font-semibold uppercase tracking-wide mb-2" :style="{ color: 'var(--text-muted)' }">
                              Quick Actions
                            </div>
                            <div class="flex flex-col gap-1">
                              <button @click="viewShift(shift.name)"
                                class="w-full text-left px-2 py-1 text-xs rounded transition-colors flex items-center gap-1.5"
                                :style="{
                                  color: 'var(--focus-ring)',
                                  background: 'var(--info-bg)'
                                }"
                                @mouseover="$event.currentTarget.style.background = 'var(--info-border)'"
                                @mouseleave="$event.currentTarget.style.background = 'var(--info-bg)'"
                              >
                                <Eye class="w-3 h-3" /> View Details
                              </button>
                              <button @click="printShift(shift.name)"
                                class="w-full text-left px-2 py-1 text-xs rounded transition-colors flex items-center gap-1.5"
                                :style="{
                                  color: 'var(--icon-color-green)',
                                  background: 'var(--icon-bg-green)'
                                }"
                                @mouseover="$event.currentTarget.style.background = 'var(--item-border)'"
                                @mouseleave="$event.currentTarget.style.background = 'var(--icon-bg-green)'"
                              >
                                <PrintIcon class="w-3 h-3" /> Print Shift
                              </button>
                              <button v-if="shift.status === 'Open'" @click="closeShift(shift.name)"
                                class="w-full text-left px-2 py-1 text-xs rounded transition-colors flex items-center gap-1.5"
                                :style="{
                                  color: 'var(--warning-border)',
                                  background: 'var(--warning-bg)'
                                }"
                                @mouseover="$event.currentTarget.style.background = 'var(--warning-border)'; $event.currentTarget.style.color = '#fff'"
                                @mouseleave="$event.currentTarget.style.background = 'var(--warning-bg)'; $event.currentTarget.style.color = 'var(--warning-border)'"
                              >
                                <DeleteIcon class="w-3 h-3" /> Close Shift
                              </button>
                            </div>
                          </div>

                        </div>
                      </td>
                    </tr>

                  </template>
                </tbody>
              </table>
            </div>

            <!-- Loading -->
            <div v-if="isLoading" class="flex flex-col items-center justify-center py-10" :style="{ color: 'var(--text-muted)' }">
              <svg class="w-7 h-7 animate-spin mb-2" :style="{ color: 'var(--focus-ring)' }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              <span class="text-xs">Loading shifts...</span>
            </div>

            <!-- Empty -->
            <div v-if="paginatedShifts.length === 0 && !isLoading" class="flex flex-col items-center justify-center py-10" :style="{ color: 'var(--text-muted)' }">
              <div
                class="w-10 h-10 flex items-center justify-center rounded-full mb-2"
                :style="{ background: 'var(--item-bg)' }"
              >
                <svg class="w-5 h-5" :style="{ color: 'var(--text-muted)', opacity: 0.5 }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V7a2 2 0 00-2-2h-3.586a1 1 0 01-.707-.293l-1.414-1.414A2 2 0 0010.586 3H6a2 2 0 00-2 2v6m16 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2v-6m16 0H4" />
                </svg>
              </div>
              <p class="text-xs font-medium" :style="{ color: 'var(--text-sub)' }">No Shifts Found</p>
              <p class="text-xs mt-0.5" :style="{ color: 'var(--text-muted)' }">Try adjusting your filters</p>
            </div>

            <!-- Pagination -->
            <div
              v-if="totalPages > 1"
              class="px-4 py-2.5"
              :style="{
                borderTop: '1px solid var(--card-border)',
                background: 'var(--item-bg)'
              }"
            >
              <div class="flex items-center justify-between">
                <span class="text-xs" :style="{ color: 'var(--text-muted)' }">
                  Showing {{ ((currentPage - 1) * itemsPerPage) + 1 }}–{{ Math.min(currentPage * itemsPerPage, filteredShifts.length) }}
                  of {{ filteredShifts.length }}
                </span>
                <div class="flex items-center gap-1">
                  <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage === 1"
                    class="px-2 py-1 text-xs rounded disabled:opacity-40 transition-colors"
                    :style="{
                      border: '1px solid var(--card-border)',
                      color: 'var(--text-sub)',
                      background: 'var(--card-bg)'
                    }"
                  >Prev</button>

                  <button v-for="page in visiblePages" :key="page" @click="currentPage = page"
                    class="px-2 py-1 text-xs rounded transition-colors font-medium"
                    :style="currentPage === page
                      ? { background: 'var(--focus-ring)', color: '#fff', border: '1px solid var(--focus-ring)' }
                      : { background: 'var(--card-bg)', color: 'var(--text-sub)', border: '1px solid var(--card-border)' }
                    "
                  >{{ page }}</button>

                  <button @click="currentPage = Math.min(totalPages, currentPage + 1)" :disabled="currentPage === totalPages"
                    class="px-2 py-1 text-xs rounded disabled:opacity-40 transition-colors"
                    :style="{
                      border: '1px solid var(--card-border)',
                      color: 'var(--text-sub)',
                      background: 'var(--card-bg)'
                    }"
                  >Next</button>
                </div>
              </div>
            </div>

          </div>
        </section>

      </main>
    </div>

</template>
<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'

import { Eye } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import ExportIcon from '@/components/icons/ExportIcon.svg'
import RefreshIcon from '@/components/icons/RefreshIcon.svg'
import SearchIcon from '@/components/icons/SearchIcon.svg'
import { useInvoicesStore } from '@/stores/invoices'
import DeleteIcon from '@/components/icons/DeleteIcon.svg'
import PrintIcon from '@/components/icons/PrintIcon.svg'
import { useShiftStore } from '../../stores/shift'
import { formatCurrency } from '../../utils/formatters'
import ShiftsIcon from '@/components/icons/shifts.svg'
import StatsCard from '../../layout/StatsCard.vue'
import { useSettingsStore } from '@/stores/settings'

const router = useRouter()
const invoicesStore = useInvoicesStore()
const shiftStore = useShiftStore()
const settingsStore = useSettingsStore()

const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(10)
const loading = ref(false)
const error = ref(null)
const isLoading = ref(false)

// ✅ Expandable rows state
const expandedRows = ref(new Set())
function toggleRow(name) {
  const next = new Set(expandedRows.value)
  next.has(name) ? next.delete(name) : next.add(name)
  expandedRows.value = next
}

const filters = reactive({
  status: '',
  date_from: '',
  date_to: '',
  cashier: ''
})

const shifts = ref([])
const statistics = reactive({
  today_shifts: 0,
  today_sales: 0,
  week_shifts: 0,
  week_sales: 0,
  month_shifts: 0,
  month_sales: 0,
  average_sales: 0
})

const locale = computed(() => settingsStore.settings.locale || 'en-PK')
const currencyCode = computed(() => settingsStore.settings.currency || 'PKR')
const uniqueCashiers = computed(() => invoicesStore.cashiers)

const filteredShifts = computed(() => {
  let result = [...shifts.value]
  if (searchQuery.value) {
    result = result.filter(s =>
      s.name.toString().includes(searchQuery.value) ||
      (s.user && s.user.includes(searchQuery.value)) ||
      (s.closed_by_name && s.closed_by_name.includes(searchQuery.value))
    )
  }
  if (filters.status)    result = result.filter(s => s.status?.toLowerCase() === filters.status.toLowerCase())
  if (filters.cashier)   result = result.filter(s => s.user === filters.cashier || s.closed_by_name === filters.cashier)
  if (filters.date_from) {
    const from = new Date(filters.date_from)
    result = result.filter(s => new Date(s.posting_date) >= from)
  }
  if (filters.date_to) {
    const to = new Date(filters.date_to)
    to.setHours(23, 59, 59, 999)
    result = result.filter(s => new Date(s.posting_date) <= to)
  }
  return result
})

const paginatedShifts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredShifts.value.slice(start, start + itemsPerPage.value)
})

const totalPages = computed(() => Math.ceil(filteredShifts.value.length / itemsPerPage.value))

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  if (end - start < maxVisible - 1) start = Math.max(1, end - maxVisible + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

watch(
  () => [shiftStore.shifts, invoicesStore.invoices],
  async () => {
    await shiftStore.fetchShiftStatistics()
    Object.assign(statistics, shiftStore.statistics)
  },
  { deep: true }
)

async function loadShifts() {
  loading.value = true
  error.value = null
  try {
    const response = await shiftStore.loadShifts({ status: filters.status })
    shifts.value = response.status === 'success' ? shiftStore.shifts : []
  } catch (err) {
    console.error('❌ Error fetching shifts:', err)
    shifts.value = []
  } finally {
    loading.value = false
  }
}

function viewShift(name)    { router.push(`/shifts/${name}`) }
function viewCurrentShift() { router.push('/shifts/current') }
function printShift(id)     { console.log('🖨️ Print shift:', id) }
function closeShift(id)     { if (confirm('هل أنت متأكد سے بند کریں هذا الشيفت؟')) console.log('🔒 Close shift:', id) }
function searchShifts()     { currentPage.value = 1 }
function applyFilters()     { currentPage.value = 1; loadShifts() }
function exportShifts()     { console.log('📤 Export shifts') }

function resetFilters() {
  filters.status = filters.date_from = filters.date_to = filters.cashier = ''
  currentPage.value = 1
  loadShifts()
}

onMounted(async () => {
  isLoading.value = true
  try {
    await loadShifts()
    const st = await shiftStore.fetchShiftStatistics()
    Object.assign(statistics, st)
  } finally {
    isLoading.value = false
  }
})
</script>
