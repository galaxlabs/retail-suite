<template>
    <div fluid>
      <div v-show="!dialog" class="w-full min-h-screen flex" :style="{ background: 'var(--item-bg)' }">
        <!-- Main Content -->
        <div class="flex-1 p-2 space-y-5">
          <div class="min-h-screen grid grid-cols-1 md:grid-cols-3 gap-4">

            <!-- Left Section -->
            <div
              class="md:col-span-2 shadow-lg rounded-2xl p-6"
              :style="{
                background: 'var(--card-bg)',
                border: '1px solid var(--card-border)'
              }"
            >
              <Customer @customer-selected="handleCustomerSelected" />
              <v-divider />

              <!-- Invoices Section -->
              <div>
                <!-- Search Section -->
                <div class="grid m-4 grid-cols-1 md:grid-cols-12 gap-4">
                  <div class="md:col-span-4">
                    <v-select
                      :list-props="{ bgColor: 'white' }"
                      item-color="cyan"
                      clearable
                      hide-details
                      density="comfortable"
                      variant="outlined"
                      background-color="white"
                      v-model="pos_profile_search"
                      :items="pos_profiles_list"
                      item-value="name"
                      label="Select POS Profile"
                      class="custom-vselect"
                    />
                  </div>
                  <div class="md:col-span-5" />
                  <div class="md:col-span-3">
                    <button
                      @click="fetchAllData"
                      :disabled="invoices_loading"
                      class="w-full text-white font-bold rounded-lg px-6 py-3 transition duration-300 active:scale-95 shadow-md uppercase tracking-wide text-sm disabled:cursor-not-allowed"
                      :style="{ background: PrimaryColor }"
                    >
                      <span v-if="invoices_loading" class="inline-block animate-spin mr-2">⟳</span>
                      <span>{{ invoices_loading ? 'Loading...' : 'Search' }}</span>
                    </button>
                  </div>
                </div>

                <!-- Totals Row -->
                <div class="grid m-1 grid-cols-1 md:grid-cols-12 gap-4">
                  <div class="md:col-span-6">
                    <strong :style="{ color: 'var(--text-main)' }" class="text-lg">Invoices</strong>
                    <span
                      v-if="total_outstanding_amount"
                      class="font-semibold ml-2"
                      :style="{ color: 'var(--icon-color-green)' }"
                    >
                      - Total Outstanding :
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formatCurrency(total_outstanding_amount) }}
                    </span>
                  </div>
                  <div class="md:col-span-6">
                    <p v-if="total_selected_invoices" class="font-semibold text-end" :style="{ color: 'var(--warning-border)' }">
                      <span>Total Selected :</span>
                      <span class="ml-2">
                        {{ currencySymbol(pos_profile.currency) }}
                        {{ formatCurrency(total_selected_invoices) }}
                      </span>
                    </p>
                  </div>
                </div>
                <!-- Invoices Table -->
                <div
                  class="mt-4 rounded-lg overflow-hidden"
                  :style="{ border: '1px solid var(--card-border)' }"
                >
                  <!-- Loading -->
                  <div
                    v-if="invoices_loading"
                    class="flex items-center justify-center gap-3 py-8"
                    :style="{ color: 'var(--text-muted)' }"
                  >
                    <div
                      class="w-6 h-6 rounded-full animate-spin"
                      :style="{ border: '2px solid var(--card-border)', borderTopColor: 'var(--focus-ring)' }"
                    />
                    Loading...
                  </div>

                  <div v-else class="overflow-x-auto">
                    <table class="w-full" style="font-size: 13px;">

                      <!-- Head -->
                      <thead :style="{ background: 'var(--item-bg)' }">
                        <tr>
                          <!-- Select All -->
                          <th class="px-3 py-2 w-10" :style="{ borderBottom: '1px solid var(--card-border)' }">
                            <input
                              type="checkbox"
                              :checked="outstanding_invoices.length > 0 &&
                                        outstanding_invoices.every(i => selected_invoices.includes(i.name))"
                              :indeterminate="outstanding_invoices.some(i => selected_invoices.includes(i.name)) &&
                                              !outstanding_invoices.every(i => selected_invoices.includes(i.name))"
                              @change="e => {
                                if (e.target.checked)
                                  selected_invoices = outstanding_invoices.map(i => i.name)
                                else
                                  selected_invoices = []
                                handleInvoiceSelection(selected_invoices)
                              }"
                            />
                          </th>
                          <th
                            v-for="col in invoices_headers"
                            :key="col.key"
                            class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide whitespace-nowrap"
                            :style="{
                              color: 'var(--text-muted)',
                              borderBottom: '1px solid var(--card-border)'
                            }"
                          >
                            {{ col.title }}
                          </th>
                        </tr>
                      </thead>

                      <!-- Body -->
                      <tbody>
                        <tr
                          v-for="item in outstanding_invoices"
                          :key="item.name"
                          class="transition-colors cursor-pointer"
                          :style="{
                            background: selected_invoices.includes(item.name)
                              ? 'var(--choice-active-bg)'
                              : 'transparent',
                            borderBottom: '1px solid var(--card-border)'
                          }"
                          @click="() => {
                            const idx = selected_invoices.indexOf(item.name)
                            if (idx === -1) selected_invoices.push(item.name)
                            else selected_invoices.splice(idx, 1)
                            handleInvoiceSelection(selected_invoices)
                          }"
                          @mouseover="e => {
                            if (!selected_invoices.includes(item.name))
                              e.currentTarget.style.background = 'var(--nav-item-hover-bg)'
                          }"
                          @mouseleave="e => {
                            e.currentTarget.style.background = selected_invoices.includes(item.name)
                              ? 'var(--choice-active-bg)'
                              : 'transparent'
                          }"
                        >
                          <!-- Row checkbox -->
                          <td class="px-3 py-2 w-10" @click.stop>
                            <input
                              type="checkbox"
                              :checked="selected_invoices.includes(item.name)"
                              @change="() => {
                                const idx = selected_invoices.indexOf(item.name)
                                if (idx === -1) selected_invoices.push(item.name)
                                else selected_invoices.splice(idx, 1)
                                handleInvoiceSelection(selected_invoices)
                              }"
                            />
                          </td>
                          <!-- Invoice Name -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span :style="{ color: 'var(--text-sub)' }">{{ item.name }}</span>
                          </td>
                          <!-- Customer Name -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span :style="{ color: 'var(--text-sub)' }">{{ item.customer_name }}</span>
                          </td>
                          <!-- Posting Date -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span :style="{ color: 'var(--text-sub)' }">{{ formatDate(item.posting_date) }}</span>
                          </td>

                          <!-- Due Date -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span :style="{ color: 'var(--text-sub)' }">{{ formatDate(item.due_date) }}</span>
                          </td>

                          <!-- Grand Total -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span class="font-medium" :style="{ color: 'var(--text-main)' }">
                              {{ currencySymbol(item.currency) }} {{ formatCurrency(item.grand_total) }}
                            </span>
                          </td>

                          <!-- Outstanding Amount -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span class="font-semibold" :style="{ color: 'var(--focus-ring)' }">
                              {{ currencySymbol(item.currency) }} {{ formatCurrency(item.outstanding_amount) }}
                            </span>
                          </td>
                        </tr>

                        <!-- Empty State -->
                        <tr v-if="outstanding_invoices.length === 0">
                            <td
                              :colspan="invoices_headers.length + 1"
                              class="px-4 py-10"
                            >
                              <div
                                class="flex flex-col items-center justify-center text-center gap-3"
                              >
                                <FileText
                                  class="w-14 h-14"
                                  :style="{ color: 'var(--text-muted)' }"
                                />

                                <p
                                  class="text-sm font-medium"
                                  :style="{ color: 'var(--text-muted)' }"
                                >
                                  {{
                                    customer_name
                                      ? 'No outstanding invoices found'
                                      : 'Select a customer to view invoices'
                                  }}
                                </p>
                              </div>
                            </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <v-divider class="my-4" />
              </div>

              <!-- Unallocated Payment Section -->
              <div v-if="pos_profile.posa_allow_reconcile_payments && unallocated_payments.length">

                <!-- Header Row -->
                <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <p>
                    <strong :style="{ color: 'var(--text-main)' }">Payments</strong>
                    <span
                      v-if="total_unallocated_amount"
                      class="font-semibold ml-2"
                      :style="{ color: 'var(--focus-ring)' }"
                    >
                      - Total Unallocated :
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formatCurrency(total_unallocated_amount) }}
                    </span>
                  </p>
                  <p
                    v-if="total_selected_payments"
                    class="font-semibold"
                    :style="{ color: 'var(--warning-border)' }"
                  >
                    Total Selected :
                    <span class="ml-2">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formatCurrency(total_selected_payments) }}
                    </span>
                  </p>
                </div>

                <!-- Table -->
                <div
                  class="rounded-lg overflow-hidden"
                  :style="{ border: '1px solid var(--card-border)' }"
                >
                  <!-- Loading -->
                  <div
                    v-if="unallocated_payments_loading"
                    class="flex items-center justify-center gap-3 py-8"
                    :style="{ color: 'var(--text-muted)' }"
                  >
                    <div
                      class="w-6 h-6 rounded-full animate-spin"
                      :style="{ border: '2px solid var(--card-border)', borderTopColor: 'var(--focus-ring)' }"
                    />
                    Loading...
                  </div>

                  <div v-else class="overflow-x-auto">
                    <table class="w-full" style="font-size: 13px;">

                      <!-- Head -->
                      <thead :style="{ background: 'var(--item-bg)' }">
                        <tr>
                          <!-- Select All -->
                          <th class="px-3 py-2 w-10" :style="{ borderBottom: '1px solid var(--card-border)' }">
                            <input
                              v-if="!singleSelect"
                              type="checkbox"
                              :checked="unallocated_payments.length > 0 &&
                                        unallocated_payments.every(p => selected_payments.includes(p.name))"
                              :indeterminate="unallocated_payments.some(p => selected_payments.includes(p.name)) &&
                                              !unallocated_payments.every(p => selected_payments.includes(p.name))"
                              @change="e => {
                                if (e.target.checked)
                                  selected_payments = unallocated_payments.map(p => p.name)
                                else
                                  selected_payments = []
                                handlePaymentSelection(selected_payments)
                              }"
                            />
                          </th>
                          <th
                            v-for="col in unallocated_payments_headers"
                            :key="col.key"
                            class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide whitespace-nowrap"
                            :style="{
                              color: 'var(--text-muted)',
                              borderBottom: '1px solid var(--card-border)'
                            }"
                          >
                            {{ col.title }}
                          </th>
                        </tr>
                      </thead>

                      <!-- Body -->
                      <tbody>
                        <tr
                          v-for="item in unallocated_payments"
                          :key="item.name"
                          class="transition-colors cursor-pointer"
                          :style="{
                            background: selected_payments.includes(item.name)
                              ? 'var(--choice-active-bg)'
                              : 'transparent',
                            borderBottom: '1px solid var(--card-border)'
                          }"
                          @click="() => {
                            if (singleSelect) {
                              selected_payments = selected_payments.includes(item.name) ? [] : [item.name]
                            } else {
                              const idx = selected_payments.indexOf(item.name)
                              if (idx === -1) selected_payments.push(item.name)
                              else selected_payments.splice(idx, 1)
                            }
                            handlePaymentSelection(selected_payments)
                          }"
                          @mouseover="e => {
                            if (!selected_payments.includes(item.name))
                              e.currentTarget.style.background = 'var(--nav-item-hover-bg)'
                          }"
                          @mouseleave="e => {
                            e.currentTarget.style.background = selected_payments.includes(item.name)
                              ? 'var(--choice-active-bg)'
                              : 'transparent'
                          }"
                        >
                          <!-- Row Checkbox -->
                          <td class="px-3 py-2 w-10" @click.stop>
                            <input
                              type="checkbox"
                              :checked="selected_payments.includes(item.name)"
                              @change="() => {
                                if (singleSelect) {
                                  selected_payments = selected_payments.includes(item.name) ? [] : [item.name]
                                } else {
                                  const idx = selected_payments.indexOf(item.name)
                                  if (idx === -1) selected_payments.push(item.name)
                                  else selected_payments.splice(idx, 1)
                                }
                                handlePaymentSelection(selected_payments)
                              }"
                            />
                          </td>
                            <!-- Payment Name -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span class="font-medium" :style="{ color: 'var(--text-main)' }">
                              {{ item.name }}
                            </span>
                          </td>
                          <!-- Mode of Payment  -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span class="font-medium" :style="{ color: 'var(--text-main)' }">
                              {{ item.mode_of_payment }}
                            </span>
                          </td>
                          <!-- Posting Date  -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span class="font-medium" :style="{ color: 'var(--text-main)' }">
                              {{ item.posting_date }}
                            </span>
                          </td>
                          <!-- Paid Amount -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span class="font-medium" :style="{ color: 'var(--text-main)' }">
                              {{ currencySymbol(item.currency) }} {{ formatCurrency(item.paid_amount) }}
                            </span>
                          </td>

                          <!-- Unallocated Amount -->
                          <td class="px-3 py-2 whitespace-nowrap">
                            <span class="font-semibold" :style="{ color: 'var(--focus-ring)' }">
                              {{ currencySymbol(item.currency) }} {{ formatCurrency(item.unallocated_amount) }}
                            </span>
                          </td>
                        </tr>

                        <!-- Empty State -->
                        <tr v-if="unallocated_payments.length === 0">
                          <td
                            :colspan="unallocated_payments_headers.length + 1"
                            class="px-4 py-10 text-center text-sm"
                            :style="{ color: 'var(--text-muted)' }"
                          >
                            No payments found
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <hr class="my-4" :style="{ borderColor: 'var(--card-border)' }">
              </div>
              <hr :style="{ borderColor: 'var(--card-border)' }">

              <!-- Mpesa Section -->
              <div v-if="pos_profile.posa_allow_mpesa_reconcile_payments">
                <v-row>
                  <v-col md="8" cols="12">
                    <p>
                      <strong :style="{ color: 'var(--text-main)' }">Search Mpesa Payments</strong>
                    </p>
                  </v-col>
                  <v-col md="4" cols="12" v-if="total_selected_mpesa_payments">
                    <p class="text-end font-semibold" :style="{ color: 'var(--warning-border)' }">
                      <span>Total Selected :</span>
                      <span>
                        {{ currencySymbol(pos_profile.currency) }}
                        {{ formtCurrency(total_selected_mpesa_payments) }}
                      </span>
                    </p>
                  </v-col>
                </v-row>
                <v-row align="center" no-gutters class="mb-1">
                  <v-col md="4" cols="12" class="mr-1">
                    <v-text-field dense outlined color="primary" :label="'Search by Name'" background-color="white" hide-details v-model="mpesa_search_name" clearable />
                  </v-col>
                  <v-col md="4" cols="12" class="mr-1">
                    <v-text-field dense outlined color="primary" :label="'Search by Mobile'" background-color="white" hide-details v-model="mpesa_search_mobile" clearable />
                  </v-col>
                  <v-col />
                  <v-col md="3" cols="12">
                    <v-btn block color="warning" dark @click="get_draft_mpesa_payments_register">Search</v-btn>
                  </v-col>
                </v-row>
                <v-data-table
                  :headers="mpesa_payment_headers"
                  :items="mpesa_payments"
                  item-key="name"
                  class="elevation-1 mt-0"
                  :single-select="singleSelect"
                  show-select
                  v-model="selected_mpesa_payments"
                  :loading="mpesa_payments_loading"
                  checkbox-color="primary"
                >
                  <template v-slot:item.amount="{ item }">
                    <span :style="{ color: 'var(--focus-ring)' }">
                      {{ currencySymbol(item.currency) }} {{ formtCurrency(item.amount) }}
                    </span>
                  </template>
                </v-data-table>
              </div>
            </div>

            <!-- Payment Section -->
            <div
              class="shadow-lg rounded-2xl p-6 sticky top-5 max-h-screen overflow-y-auto"
              :style="{
                background: 'var(--card-bg)',
                border: '1px solid var(--card-border)'
              }"
            >
              <!-- Header -->
              <div class="mb-6">
                <h2 class="text-2xl font-bold text-center" :style="{ color: 'var(--text-main)' }">
                  Payment information
                </h2>
              </div>

              <div class="space-y-6">

                <!-- Total Invoices -->
                <div
                  class="p-4 rounded-xl"
                  :style="{
                    background: 'var(--item-bg)',
                    border: '1px solid var(--item-border)'
                  }"
                >
                  <div class="flex justify-between items-center">
                    <span class="font-semibold" :style="{ color: 'var(--text-sub)' }">Total Invoices</span>
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium" :style="{ color: 'var(--text-muted)' }">
                        {{ currencySymbol(pos_profile.currency) }}
                      </span>
                      <input
                        :value="formatCurrency(total_selected_invoices)"
                        type="text"
                        readonly
                        class="w-32 rounded-lg p-2.5 text-right font-bold cursor-not-allowed"
                        :style="{
                          background: 'var(--input-bg)',
                          border: '1px solid var(--input-border)',
                          color: 'var(--focus-ring)'
                        }"
                      />
                    </div>
                  </div>
                </div>

                <v-divider />

                <!-- Total Payments -->
                <div>
                  <div
                    v-if="total_selected_payments"
                    class="p-4 rounded-xl"
                    :style="{
                      background: 'var(--item-bg)',
                      border: '1px solid var(--item-border)'
                    }"
                  >
                    <div class="flex justify-between items-center">
                      <span class="font-semibold" :style="{ color: 'var(--text-sub)' }">Total Payments:</span>
                      <div class="flex items-center gap-2">
                        <span class="text-sm font-medium" :style="{ color: 'var(--text-muted)' }">
                          {{ currencySymbol(pos_profile.currency) }}
                        </span>
                        <input
                          class="w-32 rounded-lg p-2.5 text-right font-bold cursor-not-allowed"
                          :style="{
                            background: 'var(--input-bg)',
                            border: '1px solid var(--input-border)',
                            color: 'var(--focus-ring)'
                          }"
                          :value="formatCurrency(total_selected_payments)"
                          readonly
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <v-divider />

                <!-- Difference Amount -->
                <div
                  class="p-4 rounded-xl shadow-sm"
                  :style="{
                    background: 'var(--warning-bg)',
                    borderLeft: '4px solid var(--warning-border)'
                  }"
                >
                  <div class="flex justify-between items-center">
                    <span class="font-semibold" :style="{ color: 'var(--text-main)' }">Difference</span>
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium" :style="{ color: 'var(--text-sub)' }">
                        {{ currencySymbol(pos_profile.currency) }}
                      </span>
                      <input
                        :value="formatCurrency(total_of_diff)"
                        type="text"
                        readonly
                        class="w-32 rounded-lg p-2.5 text-right font-bold cursor-not-allowed"
                        :style="{
                          background: 'var(--input-bg)',
                          color: total_of_diff >= 0 ? 'var(--icon-color-green)' : 'var(--warning-border)',
                          border: total_of_diff >= 0
                            ? '1px solid var(--icon-color-green)'
                            : '1px solid var(--warning-border)'
                        }"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex gap-3 mt-8">
                <button
                  @click="submit"
                  :disabled="selected_invoices.length === 0 && selected_payments.length === 0"
                  class="flex-1 py-3 px-4 text-white font-semibold rounded-lg transition duration-300 shadow-md disabled:cursor-not-allowed active:scale-95"
                  :style="{ background: selected_invoices.length && selected_payments.length ? 'var(--btn-info)' : 'var(--text-muted)' }"
                >
                  <span v-if="!invoices_loading">✓ Pay</span>

                  <span v-else class="flex items-center justify-center gap-2">
                    <span class="inline-block animate-spin">⟳</span>
                    Processing..
                  </span>
                </button>

                <button
                  type="button"
                  class="px-6 py-3 font-semibold rounded-lg transition duration-200"
                  :style="{
                    background: 'var(--card-bg)',
                    color: 'var(--text-main)',
                    border: '2px solid var(--card-border)'
                  }"
                  @mouseover="$event.currentTarget.style.background = 'var(--item-bg)'"
                  @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                >
                  Cancel
                </button>
              </div>

              <p class="text-xs text-center mt-4" :style="{ color: 'var(--text-muted)' }">
                Note: Please ensure the entered information is correct before confirming payment.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000" position="top" rounded="lg">
      <template v-slot:default>
        <div class="flex items-center gap-2">
          <span class="text-lg">{{ snackbarMessage }}</span>
        </div>
      </template>
    </v-snackbar>

    <!-- No Shift Warning -->
    <div
      v-if="!isShiftOpen"
      class="fixed inset-0 flex items-center justify-center z-40"
      style="background: rgba(0,0,0,0.5)"
    >
      <div
        class="rounded-lg shadow-xl max-w-md w-full mx-4 p-6 text-center"
        :style="{
          background: 'var(--card-bg)',
          border: '1px solid var(--card-border)'
        }"
      >
        <div class="mb-4">
          <div
            class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
            :style="{
              background: 'var(--warning-bg)',
              border: '1px solid var(--warning-border)'
            }"
          >
            <WarningIcon class="w-8 h-8" :style="{ color: 'var(--warning-border)' }" />
          </div>
          <h3 class="text-lg font-semibold mb-2" :style="{ color: 'var(--text-main)' }">
            No Active Shift
          </h3>
          <p :style="{ color: 'var(--text-muted)' }">
            Please open a shift before starting sales transactions.
          </p>
        </div>

        <div class="flex justify-center space-x-4 mt-6">
          <button
            v-if="!shiftStore.isShiftOpen"
            @click="showOpenShiftModal = true"
            :style="{ color: hover ? 'var(--primary-600)' : 'var(--text-muted)' }"
            @mouseover="hover = true"
            @mouseleave="hover = false"
            class="w-8 h-8 flex items-center justify-center cursor-pointer transition-all duration-200 hover:scale-110"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="M18.36 6.64a9 9 0 1 1-12.73 0" />
              <line x1="12" y1="2" x2="12" y2="12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <OpenShiftModal
      v-if="showOpenShiftModal"
      @success="handleShiftOpened"
      @error="handleShiftError"
      @close="showOpenShiftModal = false"
    />
    <!-- Reconcile Result Modal -->
<Teleport to="body">
  <div
    v-if="showReconcileModal"
    class="fixed inset-0 z-50 flex items-center justify-center"
    style="background: rgba(0,0,0,0.5)"
    @click.self="showReconcileModal = false"
  >
    <div
      class="rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden"
      :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
    >
      <!-- Header -->
      <div
        class="flex items-center justify-between px-6 py-4"
        :style="{ borderBottom: '1px solid var(--card-border)' }"
      >
        <div class="flex items-center gap-2">
          <span class="text-lg">✓</span>
          <h3 class="font-semibold text-base" :style="{ color: 'var(--text-main)' }">
            Reconciliation details
          </h3>
        </div>
        <button
          @click="showReconcileModal = false"
          class="w-7 h-7 flex items-center justify-center rounded-full transition"
          :style="{ color: 'var(--text-muted)' }"
        >
          ✕
        </button>
      </div>

      <!-- Body -->
      <div class="px-6 py-5 space-y-5">
        <!-- Payments Table -->
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide mb-2"
             :style="{ color: 'var(--text-muted)' }">
            Reconciled payments
          </p>
          <div class="rounded-lg overflow-hidden"
               :style="{ border: '1px solid var(--card-border)' }">
            <table class="w-full" style="font-size: 13px;">
              <thead :style="{ background: 'var(--item-bg)' }">
                <tr>
                  <th class="px-4 py-2 text-left font-medium"
                      :style="{ color: 'var(--text-muted)', borderBottom: '1px solid var(--card-border)' }">
                    Payment Entry
                  </th>
                  <th class="px-4 py-2 text-right font-medium"
                      :style="{ color: 'var(--text-muted)', borderBottom: '1px solid var(--card-border)' }">
                    Amount
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in reconcileModalData.payments" :key="row.name"
                    :style="{ borderBottom: '1px solid var(--card-border)' }">
                  <td class="px-4 py-2 font-mono text-xs" :style="{ color: 'var(--text-sub)' }">
                    {{ row.name }}
                  </td>
                  <td class="px-4 py-2 text-right font-semibold" :style="{ color: 'var(--focus-ring)' }">
                    {{ currencySymbol(pos_profile.currency) }} {{ formatCurrency(row.amount) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Invoices Table -->
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide mb-2"
             :style="{ color: 'var(--text-muted)' }">
            Reconciled invoices
          </p>
          <div class="rounded-lg overflow-hidden"
               :style="{ border: '1px solid var(--card-border)' }">
            <table class="w-full" style="font-size: 13px;">
              <thead :style="{ background: 'var(--item-bg)' }">
                <tr>
                  <th class="px-4 py-2 text-left font-medium"
                      :style="{ color: 'var(--text-muted)', borderBottom: '1px solid var(--card-border)' }">
                    Invoice
                  </th>
                  <th class="px-4 py-2 text-right font-medium"
                      :style="{ color: 'var(--text-muted)', borderBottom: '1px solid var(--card-border)' }">
                    Amount
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in reconcileModalData.invoices" :key="row.name"
                    :style="{ borderBottom: '1px solid var(--card-border)' }">
                  <td class="px-4 py-2 font-mono text-xs" :style="{ color: 'var(--text-sub)' }">
                    {{ row.name }}
                  </td>
                  <td class="px-4 py-2 text-right font-semibold" :style="{ color: 'var(--icon-color-green)' }">
                    {{ currencySymbol(pos_profile.currency) }} {{ formatCurrency(row.amount) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div
        class="flex justify-end px-6 py-4"
        :style="{ borderTop: '1px solid var(--card-border)' }"
      >
        <button
          @click="showReconcileModal = false"
          class="px-6 py-2 rounded-lg font-semibold text-sm transition active:scale-95"
          :style="{
            background: 'var(--btn-info)',
            color: 'white'
          }"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</Teleport>
</template>
<script setup>
import OpenShiftModal from '@/components/modals/OpenShiftModal.vue'
import Customer from '@/components/cart/CustomerSection.vue'
import { FileText } from 'lucide-vue-next'
import { useShiftStore } from '@/stores/shift'
import { useToast } from "vue-toastification"
import { ref, computed, watch, onMounted } from 'vue'
import { get_currency_symbol } from '../utils/formatters'
import { storeToRefs } from 'pinia'
import { toRaw } from 'vue'
import WarningIcon from '@/components/icons/WarningIcon.svg'

import { getOutstandingInvoices, get_unallocated_payments, processPayment, getPaymentModes } from '../composables/payment'

// Reconcile Modal
const showReconcileModal = ref(false)
const reconcileModalData = ref({ payments: [], invoices: [] })

const showOpenShiftModal = ref(false)
const toast = useToast()
// Snackbar state (إذا كنت تستخدم vuetify)
const snackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('info')


const shiftStore = useShiftStore()
const { isShiftOpen } = storeToRefs(shiftStore)

const customer_name = ref('')
const company = ref('')
const currency = shiftStore.currency
const company_profile = ref('')
const pos_profile = computed(() => shiftStore.pos_profile || {})

const singleSelect = ref(false)
const invoices_loading = ref(false)
const unallocated_payments_loading = ref(false)
const mpesa_payments_loading = ref(false)

const pos_profile_search = computed(() => shiftStore.pos_profile_name || {})
const pos_profiles_list = ref([])

const outstanding_invoices = ref([])
const selected_invoices = ref([])

const unallocated_payments = ref([])
const selected_payments = ref([])

const mpesa_search_name = ref('')
const mpesa_search_mobile = ref('')
const mpesa_payments = ref([])
const selected_mpesa_payments = ref([])

const selected_invoices_objects = ref([])

const selected_payments_objects = ref([])

const invoices_headers = ref([
  { title: 'Invoice', value: 'name', sortable: true },
  { title: 'Customer', value: 'customer', sortable: true },
  { title: 'Date', value: 'posting_date', sortable: true },
  { title: 'Due Date', value: 'due_date', sortable: true },
  { title: 'Total', value: 'grand_total', align: 'end', sortable: true },
  { title: 'Outstanding', value: 'outstanding_amount', align: 'end', sortable: true }
])

const unallocated_payments_headers = ref([
  { title: 'Payment', value: 'name', sortable: true },
  { title: 'mode of payment', value: 'mode_of_payment', sortable: true },
  { title: 'Date', value: 'posting_date', sortable: true },
  { title: 'Paid Amount', value: 'paid_amount', align: 'end', sortable: true },
  { title: 'Unallocated', value: 'unallocated_amount', align: 'end', sortable: true }
])

const mpesa_payment_headers = ref([
  { title: 'Name', value: 'name', sortable: true },
  { title: 'Mobile', value: 'mobile', sortable: true },
  { title: 'Transaction ID', value: 'transaction_id', sortable: true },
  { title: 'Amount', value: 'amount', align: 'end', sortable: true }
])



//(1) //// --------- reactive watch -------////
    //  total Selected Payment //
const total_selected_payments = ref(0)
const total_selected_invoices = ref(0)
const total_selected_mpesa_payments = ref(0)

//  Shift O\I
// ===============================================================================================
// (2) ///// Computed *******
// ===============================================================================================
// ✨ Dialog من الـ store (لا تعريف محلي)
const dialog = computed({
  get: () => shiftStore.showOpeningVoucherDialog,
  set: (value) => shiftStore.setShowOpeningVoucherDialog(value)
})

const total_payment_methods = () => {
  const raw = toRaw(payment_methods.value || [])
  return raw.reduce((acc, cur) => acc + Number(cur.amount || 0), 0)
}
console.log("total_payment_methods",total_payment_methods)

const total_of_diff = computed(() => {
  const invoices = total_selected_invoices.value
  const payments = total_selected_payments.value
  const mpesa = total_selected_mpesa_payments.value
  const new_payments = payment_methods.value.reduce((sum, m) => sum + (m.amount || 0), 0)


  return invoices - (payments + mpesa + new_payments)
})


const payment_methods = computed({
  get: () => shiftStore.payment_methods || [],
  set: (value) => {
      shiftStore.payment_methods = value
    }

})

const total_unallocated_amount = computed(() => {
  return unallocated_payments.value.reduce((sum, pmt) => sum + (pmt.unallocated_amount || 0), 0)
})

// Watch لتنبيه المستخدم عند إضافة دفعة جديدة
const hasNewPaymentEntry = computed(() => {
  return payment_methods.value?.some(m => m.amount && m.amount > 0)
})

// ============================================================================================
// (3) Function Helper
// ============================================================================================

const showToast = (message, type = 'info') => {
    const toastConfig = {
    info: { color: 'blue', icon: 'ℹ️' },
    success: { color: 'green', icon: '✓' },
    warning: { color: 'orange', icon: '⚠️' },
    error: { color: 'red', icon: '✕' }
  }

  const config = toastConfig[type] || toastConfig.info
  console.log(`[${type.toUpperCase()}] ${message}`)
  toast[type](message)
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}


const currencySymbol = (currency) => {
  return get_currency_symbol(currency);
};

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-GB')
}

const setFormatedCurrency = (method, field, value) => {
  if (value !== null && value !== undefined) {
    method[field] = parseFloat(value) || 0
  }
}
// ============================================================================================
// (4) Functions & Logic
// ============================================================================================
const onInvoiceSelected = ({ value, item }) => {
  if (!item) return
  console.log("onInvoiceSelected", item, value)
  if (value) {
    if (!selected_invoices.value.find(inv => inv.name === item.name)) {
      selected_invoices.value.push(item)
    }
  } else {
    selected_invoices.value = selected_invoices.value.filter(
      inv => inv.name !== item.name
    )
  }
}

const handleCustomerSelected = (customer) => {
    console.log('🧩 Customer selected in Pay.vue:', customer)
    customer_name.value = customer.customer_name
}
const handleInvoiceSelection = (selectedNames) => {
    // تحويل الـ names إلى objects كاملة
    selected_invoices_objects.value = toRaw(outstanding_invoices.value).filter(inv =>
      selectedNames.includes(inv.name)
    )

    console.log('Selected full objects:', toRaw(selected_invoices.value))
}

const handlePaymentSelection = (selectedNames) => {
  selected_payments_objects.value = toRaw(unallocated_payments.value).filter(pmt =>
    selectedNames.includes(pmt.name)
  )

  console.log('Selected full objects:', toRaw(selected_payments.value))
}


const get_outstanding_invoices = async () => {
  console.log("search get_outstanding_invoices")
  invoices_loading.value = true
  console.log("company", pos_profile.value.company)
  console.log("Customer_name", customer_name.value)
  console.log("company", pos_profile.value.company)
  console.log("currency", pos_profile.value.currency)
  console.log("pos_profile_name", pos_profile.value.name)

  try {
    const response = await getOutstandingInvoices(
      pos_profile.value.company,
      pos_profile.value.currency,
      customer_name.value,
      pos_profile.value.name
    )
    console.log("OutStanding response", response)
    outstanding_invoices.value = toRaw((response || []).map(inv => ({
      ...inv,
      name: inv.name
    })))
    console.log("Out Standing", outstanding_invoices.value)
  } catch (error) {
    console.error('Error fetching invoices:', error)
  } finally {
    invoices_loading.value = false
  }
}

const  getUnallocatedPayments = async () => {
  if (!pos_profile.value.posa_allow_reconcile_payments) return;
      unallocated_payments_loading.value = true;

  if (!customer_name.value) {
      unallocated_payments.value = [];
      unallocated_payments_loading.value = false;
    return;
  }
  const response = await get_unallocated_payments(
    customer_name.value,
    pos_profile.value.company,
    pos_profile.value.currency,
    null
  )
  console.log("get_unallocated_payments",response)
  if (response){
    unallocated_payments.value = response
    unallocated_payments_loading.value = false
  }
}

const get_draft_mpesa_payments_register = async () => {
  mpesa_payments_loading.value = true
  try {
    mpesa_payments.value = []
  } catch (error) {
    console.error('Error fetching M-Pesa payments:', error)
  } finally {
    mpesa_payments_loading.value = false
  }
}

const fetchAllData = async () => {
  try {
    await Promise.all([
      get_outstanding_invoices(),
      getUnallocatedPayments()
    ])
  } catch (error) {
    showToast("Error loading data", "error")
  }
}
const submit = async () => {

  if (selected_invoices.value.length === 0 || selected_payments.value.length === 0) {
    showToast("Please select at least one invoice or payment", "warning");
    return;
  }

  // Normalize payment amounts
    const normalized_payments = toRaw(payment_methods.value).map((p) => ({
      ...p,
      amount: parseFloat(p.amount) || 0,
    }));

    // Build payload
    const payload = {
      customer: customer_name.value,
      company: pos_profile.value.company,
      currency: pos_profile.value.currency,
      pos_opening_shift_name: shiftStore.pos_opening_shift?.name ||
                          toRaw(shiftStore.pos_opening_shift)?.name,
      pos_profile_name: pos_profile.value.name,
      pos_profile: toRaw(pos_profile.value),

      payment_methods: normalized_payments,
      selected_invoices: toRaw(selected_invoices_objects.value),
      selected_payments: toRaw(selected_payments_objects.value),
      selected_mpesa_payments: toRaw(selected_mpesa_payments.value),

      total_selected_invoices: total_selected_invoices.value,
      total_selected_payments: total_selected_payments.value,
      total_selected_mpesa_payments: total_selected_mpesa_payments.value,
      total_payment_methods: normalized_payments.reduce(
      (acc, p) => acc + (p.amount || 0),
      0
    ),
    };

    console.log("🧾 Submitting payment payload:", payload);

      try {

        const resProcess = await processPayment(payload)
        if (resProcess){

           // Parse HTML
          reconcileModalData.value = parseReconcileMsg(resProcess.msg)

          // توست مختصر
          const pCount = reconcileModalData.value.payments.length
          const iCount = reconcileModalData.value.invoices.length
          showToast(`Payment reconciled — ${pCount} payment(s), ${iCount} invoice(s)`, "success")

          // افتح الـ modal
          showReconcileModal.value = true

          resetForm()
        }else{
            console.log("Processing Payment Not Suceessfully")
            showToast(
                "An error occurred while processing the payment. Please try again.",
                'error'
              )
        }
        get_outstanding_invoices()
        getUnallocatedPayments()

      } catch (error) {
          showToast(
              `Error: ${error.message || 'Payment failed'}`,
              'error'
            )
            console.error('Error submitting payment:', error)
      }
}

const resetForm = () => {
  selected_invoices.value = []
  selected_payments.value = []
  selected_mpesa_payments.value = []
  customer_name.value = ''

}
const parseReconcileMsg = (htmlMsg) => {
  const tempDiv = document.createElement("div")
  tempDiv.innerHTML = htmlMsg
  const tables = tempDiv.querySelectorAll("table")

  const parseTable = (table) => {
    if (!table) return []
    return Array.from(table.querySelectorAll("tbody tr")).map(row => {
      const cells = row.querySelectorAll("td")
      return { name: cells[0]?.innerText || '', amount: cells[1]?.innerText || '' }
    })
  }

  return {
    payments: parseTable(tables[0]),
    invoices: parseTable(tables[1])
  }
}

// Handle shift events
const handleShiftOpened = async (shift) => {
  // await shiftStore.checkActiveShift()
  showOpenShiftModal.value = false
}

const handleShiftError = (error) => {
    console.error('Shift error:', error)
  }
// ==========================================================================================
// WATCH & MOUNT
// ==========================================================================================

watch(pos_profile, (val) => {
  console.log('pos_profile updated:', val)
})

watch(
  () => shiftStore.isShiftOpen,
  (val) => {
    if (val) {
      console.log("✅ Shift opened, payment methods:", toRaw(payment_methods.value))
    }
  },
  { immediate: true }
)
console.log("payment_methods.value", payment_methods.value);
const total_outstanding_amount = computed(() => {
  return outstanding_invoices.value.reduce((sum, inv) => sum + (inv.outstanding_amount || 0), 0)
})

watch(
  hasNewPaymentEntry,
  (hasNew, hadNew) => {
    // لما يضيف قيمة أول مرة في Mode of Payment
    if (hasNew && !hadNew && selected_payments.value.length === 0) {
      showToast(
        'تم إضافة دفعة جديدة. يمكنك اختيار فاتورة لتسوية الدفعة أو الاحتفاظ بها كدفعة معلقة',
        'info'
      )
    }
  }
)
    // Total Selected Payment
watch(
  [selected_payments, unallocated_payments, customer_name],
  ([selected, payments, customer]) => {
    if (!customer) {
      total_selected_payments.value = 0
      return
    }

    const selectedObjects = payments?.filter((p) =>
      selected.includes(p.name)
    )

    total_selected_payments.value = selectedObjects.reduce(
      (sum, p) => sum + Number(p.unallocated_amount || 0),
      0
    )
  },
  { deep: true }
)

    // Total Selected Invoice
watch(
  [selected_invoices, outstanding_invoices, customer_name],
  ([selected, invoices, customer]) => {
    if (!customer) {
      total_selected_invoices.value = 0
      return
    }

    const selectedObjects = invoices?.filter((inv) =>
      selected.includes(inv.name)
    )

    total_selected_invoices.value = selectedObjects.reduce(
      (sum, inv) => sum + Number(inv.outstanding_amount || 0),
      0
    )
  },
  { deep: true }
)

    // Total selected_mpesa_payments
watch(
  [selected_mpesa_payments, mpesa_payments, customer_name],
  ([selected, payments, customer]) => {
    if (!customer) {
      total_selected_mpesa_payments.value = 0
      return
    }

    const selectedObjects = payments?.filter((p) =>
      selected.includes(p.name)
    )

    total_selected_mpesa_payments.value = selectedObjects.reduce(
      (sum, p) => sum + Number(p.unallocated_amount || 0),
      0
    )
  },
  { deep: true }
)

watch(customer_name, async (newCustomer, oldCustomer) => {
  console.log('customer changed:', newCustomer)
  // مسح التحديدات القديمة
  selected_invoices.value = []
  selected_payments.value = []
  selected_mpesa_payments.value = []

  if (!newCustomer) {
    outstanding_invoices.value = []
    unallocated_payments.value = []
    return
  }

  // جلب الفواتير والادا شدہات غير المخصصة تلقائيًا
  await get_outstanding_invoices()
  await getUnallocatedPayments()
}, { immediate: false })


    onMounted(async () => {
      // ✨ استدعي من الـ store (بدل checkActiveShift)
      const isOpen = await shiftStore.checkActiveShift()
      console.log("isOpen", isOpen)
      // if (!isOpen) {
      //   console.log("isOpen", isOpen)
      //   showOpenShiftModal.value = true
      // }
      pos_profiles_list.value = shiftStore.pos_profiles_list
      console.log("shiftStore.pos_profiles_list",shiftStore.pos_profiles_list)
    })

</script>
<style scoped>
/* Footer customization */
.theme-dark .v-data-table-footer tr{
  background: rgb(30, 30, 30) !important;
  color: rgb(255, 255, 255) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
}
</style>
