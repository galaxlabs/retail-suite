<!-- Settings.vue -->
<template>

    <div :class="isDark ? 'theme-dark' : 'theme-light'">
      <!-- Header -->
      <header
          class="mx-3 mt-1 sticky top-0 z-10 rounded-xl shadow-sm"
          :style="{
            background: 'var(--card-bg)',
            borderBottom: '1px solid var(--card-border)'
          }"
        >
        <div class="px-4 py-3 flex justify-between items-center">
          <div class="flex items-center gap-3">
              <SettingsIcon class="w-8 h-8" :style="{color: primaryColor}" />
              <h1 class="text-lg font-bold" :style="{ color: 'var(--text-main)' }">Settings</h1>
            </div>
            <button
              @click="saveAllSettings"
              :style="{background: primaryColor}"
              class="hover:bg-cyan-600 text-white px-6 py-2 rounded-lg transition-colors duration-200 font-medium flex items-center gap-2"
              :disabled="isSaving"
            >
              <SaveIcon class="w-5 h-5" />
              {{ isSaving ? "Saving..." : "Save Changes" }}
            </button>
          </div>
      </header>

      <!-- Main Content -->
      <main class="flex flex-1 ml-6 mr-6 overflow-hidden">
      <!-- Sidebar Navigation -->
      <aside
        class="my-8 w-64 min-h-screen rounded-xl shadow-sm overflow-y-auto"
        style="background: var(--sidebar-bg); border: 1px solid var(--sidebar-border);"
      >
        <nav class="p-4 space-y-2">

          <button
            v-for="category in settingsCategories"
            :key="category.id"
            @click="activeCategory = category.id"
            class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition border-l-4"
            :style="
              activeCategory === category.id
                ? `
                  background: var(--nav-active-bg);
                  color: var(--nav-active-color);
                  border-color: var(--nav-active-border);
                `
                : `
                  background: transparent;
                  color: var(--nav-item-color);
                  border-color: transparent;
                `
            "
            @mouseover="e => {
              if (activeCategory !== category.id) {
                e.currentTarget.style.background = 'var(--nav-item-hover-bg)'
              }
            }"
            @mouseleave="e => {
              if (activeCategory !== category.id) {
                e.currentTarget.style.background = 'transparent'
              }
            }"
          >
            <component :is="category.icon" class="w-5 h-5" />
            <span>{{ category.name }}</span>
          </button>

        </nav>
      </aside>

        <!-- Settings Content -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-8 space-y-6">
            <!-- Store Settings -->
            <div
              v-if="activeCategory === 'store'"
              class="rounded-lg shadow-sm p-8"
              style="background: var(--section-bg); border: 1px solid var(--card-border);"
            >
              <h2 class="text-2xl font-bold mb-6" style="color: var(--text-main)">
                Store Information
              </h2>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

                <!-- Store Name -->
                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Store Name
                  </label>
                  <input
                    v-model="settings.store.name"
                    type="text"
                    placeholder="Your Store Name"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

                <!-- Address -->
                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Store Address
                  </label>
                  <input
                    v-model="settings.store.address"
                    type="text"
                    placeholder="Store Address"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

                <!-- Phone -->
                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Phone Number
                  </label>
                  <input
                    v-model="settings.store.phone"
                    type="tel"
                    placeholder="+1 (555) 000-0000"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

                <!-- Email -->
                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Email
                  </label>
                  <input
                    v-model="settings.store.email"
                    type="email"
                    placeholder="store@example.com"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

                <!-- Tax ID -->
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Commercial Registration Number
                  </label>
                  <input
                    v-model="settings.store.taxId"
                    type="text"
                    placeholder="Commercial Registration Number"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

              </div>
            </div>
            <!-- Receipt Settings -->
            <div
              v-if="activeCategory === 'receipt'"
              class="rounded-lg shadow-sm p-8"
              style="background: var(--card-bg); border: 1px solid var(--card-border);"
            >
              <h2 class="text-2xl font-bold mb-6" style="color: var(--text-main)">
                Receipt Settings
              </h2>

              <div class="space-y-4">

                <!-- Show Logo -->
                <div
                  class="flex items-center justify-between p-4 rounded-lg"
                  style="background: var(--info-bg); border: 1px solid var(--info-border);"
                >
                  <div>
                    <label class="text-sm font-medium" style="color: var(--text-sub)">
                      Show Store Logo on Receipt
                    </label>
                    <p class="text-xs mt-1" style="color: var(--text-muted)">
                      Display your store logo on printed receipts
                    </p>
                  </div>
                  <ToggleSwitch v-model="settings.receipt.showLogo" />
                </div>

                <!-- Thank You -->
                <div
                  class="flex items-center justify-between p-4 rounded-lg"
                  style="background: var(--info-bg); border: 1px solid var(--info-border);"
                >
                  <div>
                    <label class="text-sm font-medium" style="color: var(--text-sub)">
                      Show Thank You Message
                    </label>
                    <p class="text-xs mt-1" style="color: var(--text-muted)">
                      Add a thank you message at the bottom of receipts
                    </p>
                  </div>
                  <ToggleSwitch v-model="settings.receipt.showThankYou" />
                </div>

                <!-- Footer Message -->
                <div class="space-y-2">
                  <label class="block text-sm font-medium" style="color: var(--text-sub)">
                    Custom Footer Message
                  </label>
                  <textarea
                    v-model="settings.receipt.footerMessage"
                    rows="3"
                    placeholder="Thank you for your business!"
                    class="w-full px-4 py-2 rounded-lg transition resize-none"
                    style="
                      background: var(--textarea-bg);
                      border: 1px solid var(--textarea-border);
                      color: var(--text-main);
                    "
                  ></textarea>
                </div>

                <!-- Receipt Size -->
                <div class="space-y-2">
                  <label class="block text-sm font-medium" style="color: var(--text-sub)">
                    Receipt Size
                  </label>
                  <select
                    v-model="settings.receipt.size"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--select-bg);
                      border: 1px solid var(--select-border);
                      color: var(--text-main);
                    "
                  >
                    <option value="80mm">80mm (Thermal)</option>
                    <option value="58mm">58mm (Small)</option>
                    <option value="a4">A4 (Standard)</option>
                  </select>
                </div>

              </div>
            </div>

            <!-- Tax & Pricing -->
            <div
              v-if="activeCategory === 'pricing'"
              class="rounded-lg shadow-sm p-8"
              style="background: var(--card-bg); border: 1px solid var(--card-border);"
            >
              <h2 class="text-2xl font-bold mb-6" style="color: var(--text-main)">
                Tax & Pricing
              </h2>

              <div class="space-y-4">

                <!-- Enable Tax -->
                <div
                  class="flex items-center justify-between p-4 rounded-lg"
                  style="background: var(--info-bg); border: 1px solid var(--info-border);"
                >
                  <div>
                    <label class="text-sm font-medium" style="color: var(--text-sub)">
                      Enable Tax Calculation
                    </label>
                    <p class="text-xs mt-1" style="color: var(--text-muted)">
                      Automatically calculate tax on transactions
                    </p>
                  </div>
                  <ToggleSwitch v-model="settings.pricing.enableTax" />
                </div>

                <!-- Tax Fields -->
                <div
                  v-if="settings.pricing.enableTax"
                  class="grid grid-cols-1 md:grid-cols-2 gap-6"
                >

                  <div>
                    <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                      Tax Rate (%)
                    </label>
                    <input
                      v-model.number="settings.pricing.taxRate"
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      placeholder="10"
                      class="w-full px-4 py-2 rounded-lg transition"
                      style="
                        background: var(--input-bg);
                        border: 1px solid var(--input-border);
                        color: var(--text-main);
                      "
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                      Tax Name
                    </label>
                    <input
                      v-model="settings.pricing.taxName"
                      type="text"
                      placeholder="VAT, GST, etc."
                      class="w-full px-4 py-2 rounded-lg transition"
                      style="
                        background: var(--input-bg);
                        border: 1px solid var(--input-border);
                        color: var(--text-main);
                      "
                    />
                  </div>

                </div>

                <!-- Currency -->
                <div class="space-y-2">
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Currency
                  </label>
                  <select
                    v-model="settings.pricing.currency"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--select-bg);
                      border: 1px solid var(--select-border);
                      color: var(--text-main);
                    "
                  >
                    <option value="EGP">Egyptian Pound (£)</option>
                    <option value="USD">US Dollar ($)</option>
                    <option value="EUR">Euro (€)</option>
                    <option value="SAR">Saudi Riyal (﷼)</option>
                  </select>
                </div>

                <!-- Price List -->
                <div class="space-y-2">
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Price List
                  </label>
                  <select
                    v-model="settings.pricing.price_list"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--select-bg);
                      border: 1px solid var(--select-border);
                      color: var(--text-main);
                    "
                  >
                    <option value="Standard Selling">Standard Selling</option>
                  </select>
                </div>

                <!-- Round Prices -->
                <div
                  class="flex items-center justify-between p-4 rounded-lg"
                  style="background: var(--info-bg); border: 1px solid var(--info-border);"
                >
                  <div>
                    <label class="text-sm font-medium" style="color: var(--text-sub)">
                      Round Prices
                    </label>
                    <p class="text-xs mt-1" style="color: var(--text-muted)">
                      Round prices to the nearest whole number
                    </p>
                  </div>
                  <ToggleSwitch v-model="settings.pricing.roundPrices" />
                </div>

              </div>
            </div>

            <!-- Appearance -->
            <div
              v-if="activeCategory === 'appearance'"
              class="rounded-lg shadow-sm p-8"
              style="background: var(--card-bg); border: 1px solid var(--card-border);"
            >
              <h2 class="text-2xl font-bold mb-6" style="color: var(--text-main)">
                Appearance
              </h2>

              <!-- Theme Selection -->
              <div class="mb-8">
                <label class="block text-sm font-medium mb-4" style="color: var(--text-sub)">
                  Theme
                </label>

                <div class="grid grid-cols-2 gap-4">

                  <!-- Light -->
                  <div
                    @click="settings.appearance.theme = 'light'"
                    class="cursor-pointer border-2 rounded-lg p-4 text-center transition"
                    :style="
                      settings.appearance.theme === 'light'
                        ? `border: 2px solid var(--choice-active-border); background: var(--choice-active-bg);`
                        : `border: 2px solid var(--choice-border);`
                    "
                  >
                    <SunIcon class="w-8 h-8 mx-auto mb-2 text-yellow-500" />
                    <span class="text-sm font-medium" style="color: var(--text-main)">
                      Light Mode
                    </span>
                  </div>

                  <!-- Dark -->
                  <div
                    @click="settings.appearance.theme = 'dark'"
                    class="cursor-pointer border-2 rounded-lg p-4 text-center transition"
                    :style="
                      settings.appearance.theme === 'dark'
                        ? `border: 2px solid var(--choice-active-border); background: var(--choice-active-bg);`
                        : `border: 2px solid var(--choice-border);`
                    "
                  >
                    <MoonIcon class="w-8 h-8 mx-auto mb-2" style="color: var(--text-sub)" />
                    <span class="text-sm font-medium" style="color: var(--text-main)">
                      Dark Mode
                    </span>
                  </div>

                </div>
              </div>

              <!-- Primary Color -->
              <div class="mb-8">
                <label class="block text-sm font-medium mb-4" style="color: var(--text-sub)">
                  Primary Color
                </label>

                <div class="flex flex-wrap gap-3">
                  <div
                    v-for="color in colorOptions"
                    :key="color.value"
                    @click="settings.appearance.primaryColor = color.value"
                    class="w-12 h-12 rounded-full cursor-pointer border-4 shadow-md transition hover:scale-110"
                    :class="color.class"
                    :style="
                      settings.appearance.primaryColor === color.value
                        ? `outline: 3px solid var(--ring-color); outline-offset: 2px;`
                        : ''
                    "
                    :title="color.name"
                  ></div>
                </div>
              </div>

              <!-- Font Size -->
              <div
                class="flex items-center justify-between p-4 rounded-lg"
                style="background: var(--info-bg); border: 1px solid var(--info-border);"
              >
                <div>
                  <label class="text-sm font-medium" style="color: var(--text-sub)">
                    Font Size
                  </label>
                  <p class="text-xs mt-1" style="color: var(--text-muted)">
                    Choose your preferred font size
                  </p>
                </div>

                <select
                  v-model="settings.appearance.fontSize"
                  class="px-3 py-2 rounded-lg transition"
                  style="
                    background: var(--select-bg);
                    border: 1px solid var(--select-border);
                    color: var(--text-main);
                  "
                >
                  <option value="small">Small</option>
                  <option value="normal">Normal</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>

            <!-- Printer Settings -->
            <div
              v-if="activeCategory === 'printer'"
              class="rounded-lg shadow-sm p-8"
              style="background: var(--card-bg); border: 1px solid var(--card-border);"
            >
              <h2 class="text-2xl font-bold mb-6" style="color: var(--text-main)">
                Printer Settings
              </h2>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Terminal Name
                  </label>
                  <input
                    v-model="settings.printer.terminalName"
                    type="text"
                    placeholder="Front Counter 1"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Printer Type
                  </label>
                  <select
                    v-model="settings.printer.type"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--select-bg);
                      border: 1px solid var(--select-border);
                      color: var(--text-main);
                    "
                  >
                    <option value="thermal">Thermal Printer</option>
                    <option value="inkjet">Inkjet Printer</option>
                    <option value="laser">Laser Printer</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Connection Type
                  </label>
                  <select
                    v-model="settings.printer.connectionType"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--select-bg);
                      border: 1px solid var(--select-border);
                      color: var(--text-main);
                    "
                  >
                    <option value="usb">USB / Local Bridge</option>
                    <option value="ethernet">Ethernet / LAN</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Printer Name
                  </label>
                  <input
                    v-model="settings.printer.name"
                    type="text"
                    placeholder="EPSON TM-T20"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Printer Host / IP
                  </label>
                  <input
                    v-model="settings.printer.host"
                    type="text"
                    placeholder="192.168.1.120"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Port
                  </label>
                  <input
                    v-model.number="settings.printer.port"
                    type="number"
                    placeholder="9100"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Paper Width (mm)
                  </label>
                  <input
                    v-model.number="settings.printer.paperWidth"
                    type="number"
                    placeholder="80"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-2" style="color: var(--text-sub)">
                    Copy Count
                  </label>
                  <input
                    v-model.number="settings.printer.copyCount"
                    type="number"
                    min="1"
                    step="1"
                    placeholder="1"
                    class="w-full px-4 py-2 rounded-lg transition"
                    style="
                      background: var(--input-bg);
                      border: 1px solid var(--input-border);
                      color: var(--text-main);
                    "
                  />
                </div>
              </div>

              <div class="space-y-4 pt-6" style="border-top: 1px solid var(--divider);">
                <div
                  class="flex items-center justify-between p-4 rounded-lg"
                  style="background: var(--info-bg); border: 1px solid var(--info-border);"
                >
                  <div>
                    <label class="text-sm font-medium" style="color: var(--text-sub)">
                      Auto Print
                    </label>
                    <p class="text-xs mt-1" style="color: var(--text-muted)">
                      Automatically print the receipt after saving an invoice
                    </p>
                  </div>
                  <ToggleSwitch v-model="settings.printer.autoPrint" />
                </div>

                <button
                  type="button"
                  @click="handleTestPrint"
                  class="w-full px-4 py-2 text-white rounded-lg font-medium transition flex items-center justify-center gap-2"
                  style="background: var(--btn-info)"
                >
                  <Printer class="w-5 h-5" />
                  Test Print
                </button>
              </div>
            </div>

            <!-- System Settings -->
            <div
              v-if="activeCategory === 'system'"
              class="rounded-lg shadow-sm p-8"
              style="background: var(--card-bg); border: 1px solid var(--card-border);"
            >
              <h2 class="text-2xl font-bold mb-6" style="color: var(--text-main)">
                System Settings
              </h2>

              <div class="space-y-4 mb-8">

                <!-- Row -->
                <div
                  class="flex items-center justify-between p-4 rounded-lg"
                  style="background: var(--item-bg); border: 1px solid var(--item-border);"
                >
                  <div>
                    <label class="text-sm font-medium" style="color: var(--text-sub)">
                      Sound Effects
                    </label>
                    <p class="text-xs mt-1" style="color: var(--text-muted)">
                      Enable click and transaction sounds
                    </p>
                  </div>
                  <ToggleSwitch v-model="settings.system.soundEffects" />
                </div>

                <!-- Row -->
                <div
                  class="flex items-center justify-between p-4 rounded-lg"
                  style="background: var(--item-bg); border: 1px solid var(--item-border);"
                >
                  <div>
                    <label class="text-sm font-medium" style="color: var(--text-sub)">
                      Show Scanner Status
                    </label>
                    <p class="text-xs mt-1" style="color: var(--text-muted)">
                      Display whether the scanner is connected
                    </p>
                  </div>
                  <ToggleSwitch v-model="settings.system.showScannerStatus" />
                </div>

                <!-- Row -->
                <div
                  class="flex items-center justify-between p-4 rounded-lg"
                  style="background: var(--item-bg); border: 1px solid var(--item-border);"
                >
                  <div>
                    <label class="text-sm font-medium" style="color: var(--text-sub)">
                      Automatic Backup
                    </label>
                    <p class="text-xs mt-1" style="color: var(--text-muted)">
                      Automatically save data daily
                    </p>
                  </div>
                  <ToggleSwitch v-model="settings.system.autoBackup" />
                </div>

                <!-- Input -->
                <div class="space-y-2 pt-4" style="border-top: 1px solid var(--divider);">
                  <label class="block text-sm font-medium" style="color: var(--text-sub)">
                    Items Per Page
                  </label>

                  <div class="flex items-center gap-2">
                    <input
                      v-model.number="settings.system.itemsPerPage"
                      type="number"
                      min="10"
                      max="100"
                      class="w-24 px-4 py-2 rounded-lg transition"
                      style="
                        background: var(--input-bg);
                        border: 1px solid var(--input-border);
                        color: var(--text-main);
                      "
                    />
                    <span class="text-sm" style="color: var(--text-muted)">
                      items per page
                    </span>
                  </div>
                </div>
              </div>

              <!-- Data Management -->
              <div class="pt-6" style="border-top: 1px solid var(--divider);">
                <h3 class="text-lg font-semibold mb-4" style="color: var(--text-main)">
                  Data Management
                </h3>

                <div
                  class="flex items-center justify-between p-4 rounded-lg mb-4"
                  style="background: var(--item-bg); border: 1px solid var(--item-border);"
                >
                  <div>
                    <label class="text-sm font-medium" style="color: var(--text-sub)">
                      Allow Sample Products
                    </label>
                    <p class="text-xs mt-1" style="color: var(--text-muted)">
                      Create sample/temporary products for testing
                    </p>
                  </div>
                  <ToggleSwitch v-model="settings.system.simpleData" />
                </div>

                <!-- Warning Box -->
                <div
                  class="rounded-lg p-4"
                  style="background: var(--warning-bg); border: 1px solid var(--warning-border);"
                >
<!-- Actions Grid -->
<div class="grid grid-cols-2 gap-3">

  <button
    @click="creatSampleItems"
    class="flex items-center gap-2.5 px-4 py-3 rounded-xl text-sm font-medium text-white transition hover:opacity-90 active:scale-95"
    :style="{ background: primaryColor }"
  >
    <Sparkles class="w-4 h-4" />
    Create Sample Data
  </button>

  <button
    @click="exportData"
    class="flex items-center gap-2.5 px-4 py-3 rounded-xl text-sm font-medium transition hover:opacity-90 active:scale-95"
    style="background: var(--item-bg); border: 1px solid var(--item-border); color: var(--text-sub);"
  >
    <Download class="w-4 h-4" />
    Export Data
  </button>

  <button
    @click="deleteSampleItems"
    class="flex items-center gap-2.5 px-4 py-3 rounded-xl text-sm font-medium transition hover:opacity-90 active:scale-95"
    style="background: var(--item-bg); border: 1px solid var(--item-border); color: var(--text-sub);"
  >
    <Trash2 class="w-4 h-4" />
    Delete Sample Items
  </button>

  <button
    @click="clearAllData"
    class="flex items-center gap-2.5 px-4 py-3 rounded-xl text-sm font-medium text-red-500 transition hover:bg-red-50 dark:hover:bg-red-950/30 active:scale-95"
    style="background: var(--item-bg); border: 1px solid var(--item-border);"
  >
    <RotateCcw class="w-4 h-4" />
    Reset All Data
  </button>

</div>
                </div>
              </div>
            </div>
            <div
              v-if="activeCategory === 'keyboard Shortcuts'"
              class="rounded-lg shadow-sm p-8"
              style="
                background: var(--card-bg);
                border: 1px solid var(--card-border);
              ">
              <h3
                class="text-lg font-semibold mb-4"
                style="color: var(--text-main)">
                Keyboard Shortcuts
              </h3>
              <div class="space-y-2">
                <div
                  v-for="shortcut in keyboardShortcuts" :key="shortcut.id"
                  class="flex items-center justify-between p-3 rounded-lg"
                  style="
                    background: var(--item-bg);
                    border: 1px solid var(--item-border);
                  ">
                  <span
                    class="font-medium"
                    style="color: var(--text-sub)"
                  >
                  {{ shortcut.action }}
                  </span>
                  <kbd
                      class="px-2 py-1 rounded-md text-sm font-mono"
                      style="background: var(--kbd-bg); color: var(--text-main)"
                    >
                      {{ shortcut.key }}
                    </kbd>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
    <!-- Confirm Modal -->
    <!-- <ConfirmModal
      :show="confirmModal.show"
      :type="confirmModal.type"
      :doc-name="confirmModal.docName"
      :loading="confirmModal.loading"
      @confirm="onConfirmOk"
      @cancel="onConfirmCancel"
    /> -->

</template>
<script setup>
import MainLayout             from "@/layout/MainLayout.vue";
import { useShiftStore }      from "../stores/shift";
import { useProductsStore }   from "../stores/products";
import { useSettingsStore }   from "../stores/settings";
import { buildSampleReceipt, printReceipt } from '@/services/printer'
import SaveIcon               from "@/components/icons/SaveIcon.svg";
import SunIcon                from "@/components/icons/SunIcon.svg";
import MoonIcon               from "@/components/icons/MoonIcon.svg";
import SettingsIcon           from "@/components/icons/SettingsIcon.svg";
import ToggleSwitch           from "@/components/toggles/ToggleSwitch.vue";
import { useDark, useToggle } from "@vueuse/core";
import { ref, reactive, onMounted, computed, watch } from "vue";
import { Sparkles, Download, Trash2, RotateCcw, Printer } from 'lucide-vue-next'
import { toast } from "frappe-ui";
import { useConfirm } from '@/composables/useConfirm'
const { confirm } = useConfirm()
const isDark = useDark({
  selector: "html",
  attribute: "class",
  valueDark: "dark",
  valueLight: "",
});
const toggleDark = useToggle(isDark);
const activeCategory = ref("store");
const isSaving = ref(false);

// Stores
const shiftsStore   = useShiftStore();
const productsStore = useProductsStore();
const settingsStore = useSettingsStore();


const settings = computed(() => settingsStore.settings);
const primaryColor = computed(() => settings.value?.appearance?.primaryColor || '#06b6d4')
const settingsCategories = [
  { id: "store", name: "Store Info", icon: "StoreIcon" },
  { id: "receipt", name: "Receipt", icon: "ReceiptIcon" },
  { id: "pricing", name: "Pricing & Tax", icon: "DollarIcon" },
  { id: "appearance", name: "Appearance", icon: "PaletteIcon" },
  { id: "system", name: "System", icon: "CogIcon" },
  { id: "printer", name: "Printer", icon: "Printer" },
  { id: "keyboard Shortcuts", name: "Keyboard Shortcuts", icon: "KeyboardIcon" }
];

const colorOptions = [
  { name: "Ocean Blue", value: "#0a7ea4", class: "bg-[#0a7ea4]" },
  { name: "Deep Teal", value: "#1a9b8e", class: "bg-[#1a9b8e]" },
  { name: "Chocolate Mauve", value: "#5C3A3B", class: "bg-[#5C3A3B]" },
  { name: "Teal", value: "#14b8a6", class: "bg-teal-500" },
  { name: "Petrol", value: "#0f766e", class: "bg-teal-700" },
  { name: "Emerald", value: "#059669", class: "bg-emerald-600" },
  { name: "Steel", value: "#2563eb", class: "bg-blue-600" },
  { name: "Cyan", value: "#06b6d4", class: "bg-cyan-500" },
  { name: "Blue", value: "#0084ff", class: "bg-blue-500" },
  { name: "Powder Blue", value: "#B0E0E6", class: "bg-[#B0E0E6]" },
  { name: "Midnight Petrol", value: "#0b3a3f", class: "bg-[#0b3a3f]" },
  { name: "Graphite", value: "#111827", class: "bg-gray-900" },
  { name: "Royal Indigo", value: "#1e1b4b", class: "bg-indigo-950" },
  { name: "Gold", value: "#D4AF37", class: "bg-[#D4AF37]" },
  { name: "Amber", value: "#FFB300", class: "bg-[#FFB300]" },
  { name: "Mustard", value: "#E1AD01", class: "bg-[#E1AD01]" },
  { name: "Green", value: "#10b981", class: "bg-green-500" },
  { name: "Purple", value: "#a855f7", class: "bg-purple-500" },
  { name: "Pink", value: "#ec4899", class: "bg-pink-500" },
  { name: "Orange", value: "#f97316", class: "bg-orange-500" },
  { name: "Red", value: "#ef4444", class: "bg-red-500" },
  { name: "Indigo", value: "#6366f1", class: "bg-indigo-500" },
  { name: "RockStar", value: "#f49e00", class: "bg-[#f49e00]" },
  { name: "Dusty Rose", value: "#A1797A", class: "bg-[#A1797A]" },
  { name: "Black", value: "#161a1f", class: "bg-[#161a1f]" }
];
const keyboardShortcuts = ref([
  { id: 1, action: 'إتمام البيع', key: 'Enter' },
  { id: 2, action: 'إلغاء المعاملة', key: 'Esc' },
  { id: 3, action: 'بحث السريع', key: 'Ctrl + F' },
  { id: 4, action: 'جديد', key: 'Ctrl + N' },
  { id: 5, action: 'حفظ', key: 'Ctrl + S' },
  { id: 6, action: 'طباعة', key: 'Ctrl + P' }
])

const handleTestPrint = async () => {
  try {
    await printReceipt(buildSampleReceipt(), { force: true })
    toast.success('Test receipt sent to printer')
  } catch (error) {
    console.error('Test print failed:', error)
    toast.error(error.message || 'Test print failed')
  }
}

watch(
  () => settings.value,
  () => {
    console.log("⚡ Settings changed, auto-saving...");
    // تطبيق الـ Theme من settingsStore
    const theme = settingsStore.settings.appearance.theme;
    if (theme === "dark") {
      isDark.value = true;
      document.documentElement.classList.add("dark");
    } else {
      isDark.value = false;
      document.documentElement.classList.remove("dark");
    }
    settingsStore.saveSettings();
  },
  { deep: true, debounce: 500 }
);

const saveAllSettings = async () => {
  const ok = await confirm({
    type: 'submit',
    title: 'حفظ الإعدادات',
    message: 'هل تريد حفظ التغييرات؟',
    confirmLabel: 'حفظ',
  })
  if (!ok) return

  isSaving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    settingsStore.saveSettings()
  } catch (error) {
    console.error('Failed to save settings:', error)
  } finally {
    isSaving.value = false
  }
}

    // تصدير البيانات
    const exportData = () => {
      try {
        const data = {
          settings: settingsStore.settings,
          exportDate: new Date().toISOString(),
          version: "1.0",
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], {
          type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `tailwind-pos-backup-${new Date()
          .toISOString()
          .slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        toast.success('تم تصدير البيانات بنجاح!')
      } catch (error) {
        console.error("Failed to export data:", error);
      }
    };

    // حذف جميع البيانات
    const clearAllData = async () => {
        const confirmed = await confirm({
            type: 'delete',
            title: 'حذف جميع البيانات',
            message: 'هل أنت متأكد من حذف جميع البيانات؟ لا يمكن التراجع عن هذا الإجراء.',
            confirmLabel: 'حذف',
          })
          if (!confirmed) return
        try {
          localStorage.clear();
          settingsStore.resetSettings();
        } catch (error) {
          console.error("Failed to clear data:", error);
        }
    };

    const creatSampleItems = async () => {
    const confirmed = await confirm({
        type: 'info',
        title: 'إنشاء عناصر تجريبية',
        message: 'هل تريد إنشاء عناصر تجريبية للتجربة بشكل متوسط؟',
        confirmLabel: 'إنشاء',
      })
      if (!confirmed) return
      try {
        await productsStore.createSampleData();
      } catch (error) {
        console.error("Failed to create sample items:", error);
      }
    };

    const deleteSampleItems = async () => {
        const confirmed = await confirm({
            type: 'delete',
            title: 'حذف العناصر التجريبية',
            message: 'هل أنت متأكد من حذف جميع العناصر التجريبية؟',
            confirmLabel: 'حذف',
          })
          if (!confirmed) return
        try {
          await productsStore.deleteSampleData();
        } catch (error) {
          console.error("Failed to delete sample items:", error);
        }

    };

    onMounted(() => {
      settingsStore.loadSettings();
    });
</script>

<style scoped>
/* Custom styles for settings page */
.bg-gray-50 {
  background-color: #f8fafc;
}

/* Focus states */
input:focus,
select:focus,
textarea:focus {
  outline: none;
}

/* Toggle switch animation */
.transition-transform {
  transition: transform 0.2s ease;
}

/* Color picker hover effects */
.cursor-pointer:hover {
  transform: scale(1.06);
}

/* Responsive grid adjustments */
@media (max-width: 768px) {
  .lg\:col-span-1 {
    grid-column: span 1;
  }

  .lg\:col-span-3 {
    grid-column: span 1;
  }
}
</style>
