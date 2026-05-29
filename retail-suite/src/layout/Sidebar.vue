<!-- Sidebar.vue -->

<template>
 <aside
      :class="isDark ? 'theme-dark' : 'theme-light'"
      class="sticky max-h-screen top-0 side-container flex flex-row w-auto flex-shrink-0 pl-2 pr-1 py-2 z-50"
    >
    <div
      class="flex flex-col items-center py-3 flex-shrink-0 w-16 rounded-3xl transition-colors duration-300"
      :style="{
        backgroundColor: primaryColor,
        transition: 'background-color 0.3s ease'
      }"
    >
      <!-- Application Logo -->
      <router-link
        to="/pos"
        class="flex items-center justify-center h-10 w-10 rounded-full transition-all duration-200 hover:scale-110"
        :style="{
          backgroundColor: lightenColor(primaryColor, 40),
          color: primaryColor,
          transition: 'all 0.3s ease'
        }"
      >
        <AppLogo />
      </router-link>

      <!-- Navigation Menu -->
      <ul class="flex flex-col space-y-1 mt-4">
        <!-- POS Icon Menu Item -->
        <li>
          <router-link
            to="/pos"
            v-slot="{ isActive }"
            class="flex items-center"
            @click.prevent="handleMenuClick('pos')"
          >
            <span
              class="flex items-center justify-center h-10 w-10 rounded-2xl transition-all duration-200"
              :class="getMenuClass('pos', isActive)"
              :style="getMenuStyle('pos', isActive)"
              title="Point of Sale"
            >
              <PosIcon />
            </span>
          </router-link>
        </li>

        <!-- Return Menu Item -->
        <li>
          <a
            href="#"
            class="flex items-center"
            @click.prevent="handleMenuClick('return')"
          >
            <span
              class="flex items-center justify-center h-10 w-10 rounded-2xl transition-colors duration-200"
              :class="getMenuClass('return', isActive)"
              :style="getMenuStyle('return', isActive)"
              title="Returns & Refunds"
            >
              <ReturnIcon />
            </span>
          </a>
        </li>

        <!-- Payment Menu Item -->
        <li>
          <router-link
            to="/payment"
            class="flex items-center"
            #default="{ isActive }"
          >
            <span
              class="flex items-center justify-center h-10 w-10 rounded-2xl transition-all duration-200"
              :class="getMenuClass('/payment', isActive)"
              :style="getMenuStyle('/payment', isActive)"
              title="payment"
            >
              <CashIcon />
            </span>
          </router-link>
        </li>

        <!-- Inventory Menu Item -->
        <li>
          <router-link
            to="/inventory"
            class="flex items-center"
            #default="{ isActive }"
          >
            <span
              class="flex items-center justify-center h-10 w-10 rounded-2xl transition-all duration-200"
              :class="getMenuClass('/inventory', isActive)"
              :style="getMenuStyle('/inventory', isActive)"
              title="Inventory Management"
            >
              <InventoryIcon />
            </span>
          </router-link>
        </li>
        <!-- Shifts Menu Item -->
        <li>
          <router-link
            to="/staff-dashboard"
            class="flex items-center"
            #default="{ isActive }"
          >
            <span
              class="flex items-center justify-center h-10 w-10 rounded-2xl transition-all duration-200"
              :class="getMenuClass('/staff-dashboard', isActive)"
              :style="getMenuStyle('/staff-dashboard', isActive)"
              title="Shifts & Staff Management"
            >
              <ShiftsIcon />
            </span>
          </router-link>
        </li>

         <!-- accounting Menu -->
         <li>
            <router-link
              to="/accounting-dashboard"
              class="sidebar-link"
              #default="{ isActive }">

            <span
              class="flex items-center justify-center h-10 w-10 rounded-2xl transition-all duration-200"
              :class="getMenuClass('/accounting-dashboard', isActive)"
              :style="getMenuStyle('/accounting-dashboard', isActive)"
              title="Accounting"
             >
            <AccountingIcon class="w-12 h-12" />
            </span>
          </router-link>
         </li>

        <!-- Archive Menu Item -->
        <li>
          <router-link
            to="/archive"
            class="flex items-center"
            #default="{ isActive }"
          >
            <span
              class="flex items-center justify-center h-10 w-10 rounded-2xl transition-all duration-200"
              :class="getMenuClass('/archive', isActive)"
              :style="getMenuStyle('/archive', isActive)"
              title="Archive & History"
            >
              <ArchiveIcon />
            </span>
          </router-link>
        </li>

        <!-- Settings Menu Item -->
        <li>
          <router-link
            to="/settings"
            class="flex items-center"
            #default="{ isActive }"
          >
            <span
              class="flex items-center justify-center h-10 w-10 rounded-2xl transition-all duration-200"
              :class="getMenuClass('/settings', isActive)"
              :style="getMenuStyle('/settings', isActive)"
              title="System Settings"
            >
              <SettingsIcon />
            </span>
          </router-link>
        </li>

      </ul>

        <!-- GitHub Link -->
        <a
          href="https://github.com/galaxlabs/retail-suite"
          target="_blank"
          rel="noopener noreferrer"
          class="mt-auto flex items-center justify-center h-10 w-10 focus:outline-none transition-colors duration-200"
          :style="{
            color: lightenColor(primaryColor, 30),
            transition: 'color 0.3s ease'
          }"
          title="View on GitHub"
        >
          <InfoIcon />
        </a>
    </div>
  </aside>
</template>
<script setup>
import { useSettingsStore } from '@/stores/settings'
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import PosIcon from '@/components/icons/PosIcon.svg'
import InventoryIcon from '@/components/icons/InventoryIcon2.svg'
import CashIcon from '@/components/icons/DollarIcon.svg'
import ArchiveIcon from '@/components/icons/ArchiveIcon.svg'
import SettingsIcon from '@/components/icons/SettingsIcon.svg'
import ReturnIcon from '@/components/icons/ReturnIcon.svg'
import InfoIcon from '@/components/icons/InfoIcon.svg'
import AppLogo from '@/components/icons/AppLogo.svg'
import InvoiceLogo from '@/components/icons/InvoiceIcon.svg'
import ShiftsIcon from '@/components/icons/shifts.svg'
import ShoppingCartIcon from '@/components/icons/ShoppingCartIcon.svg'
import AccountingIcon from '@/components/icons/AccountingIcon.svg'
import {
  Package,
  BarChart3,
  ShoppingCart,
  ArrowRightLeft,
  Scale,
  FileText,
  ArrowRight,
  FileCheck,
  Users,
  Truck
} from 'lucide-vue-next'


  const props = defineProps( {
    activeMenu: {
      type: String,
      default: 'pos'
    }
  })
  const emit = defineEmits( ['menu-change'])

    const router = useRouter()
    const settingsStore = useSettingsStore()

    // ✅ الحصول على الإعدادات سے Store مباشرة
    const settings = computed(() => settingsStore.settings)

    // متغير محلي لتتبع اللون والـ Theme
    const primaryColor = computed(() => {
      return settings.value?.appearance?.primaryColor || '#06b6d4'
    })

    const theme = computed(() => {
      return settings.value?.appearance?.theme || 'light'
    })

    const isDark    = computed(() => settings.value?.appearance?.theme !== 'light')
    // تطبيق الـ Theme على الـ DOM
    const applyTheme = () => {
      try {
        const color = primaryColor.value
        const themeValue = theme.value

        // console.log('✨ Applying theme:', { color, theme: themeValue })

        document.documentElement.style.setProperty('--primary-color', color)
        document.documentElement.setAttribute('data-theme', themeValue)
      } catch (error) {
        console.error('❌ Error applying theme:', error)
      }
    }

    // ✅ مراقبة تغييرات localStorage سے صفحات أخرى
    const handleStorageChange = (event) => {
      if (event.key === 'tailwind-pos-settings' || !event.key) {
        console.log('🔔 localStorage changed from another tab/window!')

        // إعادة تحميل الإعدادات سے localStorage
        settingsStore.loadSettings()

        // تطبيق الـ Theme النیا
        setTimeout(() => {
          applyTheme()
        }, 100)
      }
    }

    onMounted(() => {


      // تحميل الإعدادات سے localStorage
      settingsStore.loadSettings()

      // تطبيق الـ Theme الأولي
      applyTheme()

      // ✅ الاستماع لأحداث storage (سے صفحات أخرى)
      window.addEventListener('storage', handleStorageChange)

      // ✅ مراقبة اللون الأساسي (سے نفس الصفحة)
      watch(
        () => primaryColor.value,
        (newColor) => {
          applyTheme()
        }
      )

      // ✅ مراقبة الـ Theme (سے نفس الصفحة)
      watch(
        () => theme.value,
        (newTheme) => {
          console.log('🌙 Theme changed:', newTheme)
          applyTheme()
        }
      )
    })

    onUnmounted(() => {
      // ✅ إزالة event listener عند بند کریں المكون
      window.removeEventListener('storage', handleStorageChange)
      console.log('👋 Sidebar unmounted')
    })

    // Convert hex to RGB
    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
      return result
        ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
          }
        : null
    }

    // Lighten color by percentage
    const lightenColor = (hex, percent) => {
      const rgb = hexToRgb(hex)
      if (!rgb) return hex

      const factor = 1 + percent / 100
      const r = Math.min(255, Math.round(rgb.r * factor))
      const g = Math.min(255, Math.round(rgb.g * factor))
      const b = Math.min(255, Math.round(rgb.b * factor))

      return `rgb(${r}, ${g}, ${b})`
    }

    // Get menu item classes
    const getMenuClass = (menuItem, isActive = false) => {
      const isActive_ = props.activeMenu === menuItem || isActive
      if (isActive_) {
        return 'shadow-lg text-white'
      }
      return 'text-opacity-70 hover:text-opacity-100'
    }

    // Get menu item styles
    const getMenuStyle = (menuItem, isActive = false) => {
      const isActive_ = props.activeMenu === menuItem || isActive
      const currentColor = primaryColor.value

      if (isActive_) {
        return {
          backgroundColor: lightenColor(currentColor, 20),
          transition: 'all 0.2s ease'
        }
      }
      return {
        backgroundColor: lightenColor(currentColor, -10),
        color: 'rgba(255, 255, 255, 0.7)',
        transition: 'all 0.2s ease'
      }
    }

    // Handle menu click
    const handleMenuClick = (menuItem) => {
      console.log('📍 Menu clicked:', menuItem)
      emit('menu-change', menuItem)
    }

</script>

<style scoped>
/* Smooth transitions */
a, span, div {
  transition: all 0.2s ease-in-out;
}

/* Focus states */
a:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.5);
  border-radius: 1rem;
}

/* Active menu item pulse effect */
.shadow-lg {
  animation: pulse-shadow 2s infinite;
}

@keyframes pulse-shadow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(103, 232, 249, 0.4);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(103, 232, 249, 0);
  }
}
</style>
