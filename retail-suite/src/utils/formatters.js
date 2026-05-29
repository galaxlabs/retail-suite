// Utility functions for formatting data across the application

/**
 * Format price to Indonesian Rupiah currency
 * @param {number} price - The price to format
 * @param {string} currency - Currency code (default: 'IDR')
 * @param {string} locale - Locale string (default: 'id-ID')
 * @returns {string} Formatted price string
 */

import { useShiftStore } from "../stores/shift"
import { useSettingsStore } from "../stores/settings"

export const formatDuration = (startTime, endTime) => {
  const start = new Date(startTime)
  const end = endTime ? new Date(endTime) : new Date()

  const duration = end.getTime() - start.getTime()

  const hours = Math.floor(duration / (1000 * 60 * 60))
  const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((duration % (1000 * 60)) / 1000)
  return `${hours}h ${minutes}m ${seconds}s`
}


// Form state
export const formatPrice = (price, currency) => {
  try {
    const shiftStore = useShiftStore()
    const settingsStore = useSettingsStore()
    const currentCurrency = currency || shiftStore?.pos_profile?.currency || settingsStore?.settings?.store?.currency || 'PKR'

    const currencyMap = {
      'SAR': { locale: 'en-SA', symbol: 'ر.س' },
      'USD': { locale: 'en-US', symbol: '$' },
      'EGP': { locale: 'en-EG', symbol: 'E£' },
      'AED': { locale: 'en-AE', symbol: 'د.إ' },
      'GBP': { locale: 'en-GB', symbol: '£' },
      'PKR': { locale: 'en-PK', symbol: 'Rs' }
    }


    const { locale } = currencyMap[currentCurrency] || { locale: 'en-US' }

    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currentCurrency,
      currencyDisplay: 'symbol',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price || 0)

  } catch (error) {
    console.error('Error formatting price:', error)
    const safePrice = (price || 0).toLocaleString('en-US')
    return String(currentCurrency || 'PKR') + ' ' + safePrice
  }
}

/**
 * Format number with thousand separators
 * @param {number} number - The number to format
 * @param {string} locale - Locale string (default: 'id-ID')
 * @returns {string} Formatted number string
 */
export const formatNumber = (number, locale = 'id-ID') => {
  try {
    return new Intl.NumberFormat(locale).format(number || 0)
  } catch (error) {
    console.error('Error formatting number:', error)
    return (number || 0).toString()
  }
}

/**
 * Format short price for display (e.g., 1000000 -> 1M)
 * @param {number} price - The price to format
 * @returns {string} Formatted short price string
 */
export const formatShortPrice = (price) => {
  if (!price) return '0'

  if (price >= 1000000000) {
    return `${(price / 1000000000).toFixed(1)}B`
  } else if (price >= 1000000) {
    return `${(price / 1000000).toFixed(1)}M`
  } else if (price >= 1000) {
    return `${(price / 1000).toFixed(1)}K`
  }

  return price.toString()
}

/**
 * Format date with various options
 * @param {Date|string|number} date - The date to format
 * @param {object} options - Formatting options
 * @returns {string} Formatted date string
 */
export const formatDate = (date, options = {}) => {
  if (!date) return ''

  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    timeZone: settingsStore?.settings?.system?.timeZone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
  }

  const formatOptions = { ...defaultOptions, ...options }

  try {
    const locale = options.locale || settingsStore?.settings?.store?.locale || 'en-US'
    return new Date(date).toLocaleDateString(locale, formatOptions)
  } catch (error) {
    console.error('Error formatting date:', error)
    return new Date(date).toString()
  }
}

/**
 * Format date for display in receipts
 * @param {Date|string|number} date - The date to format
 * @returns {string} Formatted receipt date string
 */
export const formatReceiptDate = (date) => {
  return formatDate(date, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

/**
 * Format date for file names (safe for file systems)
 * @param {Date|string|number} date - The date to format
 * @returns {string} Safe filename date string
 */
export const formatDateForFilename = (date = new Date()) => {
  try {
    return new Date(date).toISOString().slice(0, 19).replace(/[:.]/g, '-')
  } catch (error) {
    console.error('Error formatting date for filename:', error)
    return 'unknown-date'
  }
}

/**
 * Format time ago (relative time)
 * @param {Date|string|number} date - The date to format
 * @returns {string} Relative time string
 */
export const formatTimeAgo = (date) => {
  if (!date) return ''

  const now = new Date()
  const past = new Date(date)
  const diffInSeconds = Math.floor((now - past) / 1000)

  const intervals = [
    { label: 'year', seconds: 31536000 },
    { label: 'month', seconds: 2592000 },
    { label: 'week', seconds: 604800 },
    { label: 'day', seconds: 86400 },
    { label: 'hour', seconds: 3600 },
    { label: 'minute', seconds: 60 },
    { label: 'second', seconds: 1 }
  ]

  for (const interval of intervals) {
    const count = Math.floor(diffInSeconds / interval.seconds)
    if (count > 0) {
      return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`
    }
  }

  return 'just now'
}

/**
 * Format percentage
 * @param {number} value - The value to format as percentage
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value, decimals = 1) => {
  if (!value && value !== 0) return '0%'

  try {
    return `${value.toFixed(decimals)}%`
  } catch (error) {
    console.error('Error formatting percentage:', error)
    return '0%'
  }
}

/**
 * Format phone number (Indonesian format)
 * @param {string} phone - The phone number to format
 * @returns {string} Formatted phone number
 */
export const formatPhone = (phone) => {
  if (!phone) return ''

  // Remove all non-digit characters
  const cleaned = phone.replace(/\D/g, '')

  // Indonesian phone number formatting
  if (cleaned.startsWith('62')) {
    // International format
    const number = cleaned.slice(2)
    return `+62 ${number.slice(0, 3)} ${number.slice(3, 7)} ${number.slice(7)}`
  } else if (cleaned.startsWith('0')) {
    // Local format
    const number = cleaned.slice(1)
    return `0${number.slice(0, 3)}-${number.slice(3, 7)}-${number.slice(7)}`
  }

  return phone
}

/**
 * Format file size
 * @param {number} bytes - The size in bytes
 * @returns {string} Formatted file size string
 */
export const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'

  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))

  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

/**
 * Format quantity with unit
 * @param {number} quantity - The quantity to format
 * @param {string} unit - The unit (default: 'pcs')
 * @returns {string} Formatted quantity string
 */
export const formatQuantity = (quantity, unit = 'pcs') => {
  if (!quantity && quantity !== 0) return '0 pcs'

  const formattedQty = formatNumber(quantity)
  return `${formattedQty} ${unit}`
}

/**
 * Capitalize first letter of each word
 * @param {string} str - The string to capitalize
 * @returns {string} Capitalized string
 */
export const capitalizeWords = (str) => {
  if (!str) return ''

  return str
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

/**
 * Truncate text with ellipsis
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length (default: 50)
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return ''

  if (text.length <= maxLength) return text

  return text.slice(0, maxLength).trim() + '...'
}

/**
 * Generate receipt number
 * @param {string} prefix - Prefix for receipt number (default: 'TW')
 * @returns {string} Generated receipt number
 */
export const generateReceiptNo = (prefix = 'TW') => {
  const timestamp = Date.now().toString().slice(-6)
  const random = Math.floor(Math.random() * 100).toString().padStart(2, '0')
  return `${prefix}${timestamp}${random}`
}

/**
 * Generate transaction ID
 * @param {string} prefix - Prefix for transaction ID (default: 'TXN')
 * @returns {string} Generated transaction ID
 */
export const generateTransactionId = (prefix = 'TXN') => {
  const timestamp = Date.now()
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
  return `${prefix}${timestamp}${random}`
}

/**
 * Format stock status
 * @param {number} stock - Current stock level
 * @param {number} lowStockThreshold - Low stock threshold (default: 10)
 * @returns {object} Stock status object
 */
export const formatStockStatus = (stock, lowStockThreshold = 10) => {
  const stockLevel = stock || 0

  if (stockLevel === 0) {
    return {
      status: 'out-of-stock',
      text: 'Out of Stock',
      color: 'red',
      badgeClass: 'bg-red-100 text-red-800'
    }
  } else if (stockLevel < lowStockThreshold) {
    return {
      status: 'low-stock',
      text: 'Low Stock',
      color: 'yellow',
      badgeClass: 'bg-yellow-100 text-yellow-800'
    }
  } else {
    return {
      status: 'in-stock',
      text: 'In Stock',
      color: 'green',
      badgeClass: 'bg-green-100 text-green-800'
    }
  }
}

/**
 * Format payment method
 * @param {string} method - Payment method code
 * @returns {string} Formatted payment method name
 */
export const formatPaymentMethod = (method) => {
  const methods = {
    'cash': 'Cash',
    'card': 'Credit/Debit Card',
    'digital': 'Digital Wallet',
    'transfer': 'Bank Transfer',
    'qris': 'QRIS'
  }

  return methods[method] || capitalizeWords(method || 'cash')
}

/**
 * Parse and clean cash input
 * @param {string} input - Raw cash input
 * @returns {number} Cleaned numeric value
 */
export const parseCashInput = (input) => {
  if (!input) return 0

  // Remove currency symbols and separators
  const cleaned = input.toString().replace(/[^\d]/g, '')
  return parseInt(cleaned) || 0
}

export const get_currency_symbol = (currency) => {
  const symbols = {
    EGP: '£',
    USD: '$',
    SAR: '﷼',
    AED: 'د.إ',
    GBP: '£',
    PKR: 'Rs'
  };

  return symbols[currency] || currency; // fallback لو العملة مش موجودة
};

/**
 * Format cash input for display
 * @param {number} amount - Cash amount
 * @param {boolean} isFocused - Whether input is focused
 * @returns {string} Formatted cash input
 */
export const formatCashInput = (amount, isFocused = false) => {
  if (!amount && amount !== 0) return ''

  if (isFocused) {
    return amount.toString()
  }

  return formatNumber(amount)
}

/**
 * Validate and sanitize product data
 * @param {object} product - Product data
 * @returns {object} Sanitized product data
 */
export const sanitizeProductData = (product) => {
  return {
    name: (product.name || '').trim(),
    description: (product.description || '').trim(),
    price: Math.max(0, parseFloat(product.rate) || 0),
    stock: Math.max(0, parseInt(product.stock) || 0),
    category: (product.category || '').trim(),
    image: (product.image || '').trim()
  }
}

/**
 * Calculate discount amount
 * @param {number} subtotal - Subtotal amount
 * @param {number} discountRate - Discount rate percentage
 * @returns {number} Discount amount
 */
export const calculateDiscount = (subtotal, discountRate) => {
  if (!subtotal || !discountRate) return 0
  return Math.round(subtotal * (discountRate / 100))
}

/**
 * Calculate tax amount
 * @param {number} subtotal - Subtotal amount
 * @param {number} taxRate - Tax rate percentage
 * @returns {number} Tax amount
 */
export const calculateTax = (subtotal, taxRate) => {
  if (!subtotal || !taxRate) return 0
  return Math.round(subtotal * (taxRate / 100))
}

/**
 * Format currency for different locales
 * @param {number} amount - Amount to format
 * @param {string} currencyCode - Currency code (USD, EUR, etc.)
 * @param {string} locale - Locale string
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, currencyCode = 'USD', locale = 'en-US') => {
  const currencyMap = {
    'SAR': { locale: 'en-SA', symbol: '﷼' },
    'USD': { locale: 'en-US', symbol: '$' },
    'EGP': { locale: 'en-EG', symbol: 'E£' },
    'AED': { locale: 'en-AE', symbol: 'د.إ' },
    'GBP': { locale: 'en-GB', symbol: '£' }
  }


  const config = currencyMap[currencyCode] || { locale, symbol: '' }

  try {
    // استخدم Intl فقط كرقم، بدون currency
    const number = new Intl.NumberFormat(config.locale, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0);

    // ركب الرمز اللي انت عايزه
    return `${number}${config.symbol}`;
  } catch (error) {
    return `${amount}${config.symbol}`;
  }
}

/**
 * Get category color class
 * @param {string} category - Product category
 * @returns {string} CSS class for category badge
 */
export const getCategoryColorClass = (category) => {
  const colorMap = {
    'coffee': 'bg-amber-100 text-amber-800',
    'tea': 'bg-green-100 text-green-800',
    'food': 'bg-yellow-100 text-yellow-800',
    'pastry': 'bg-pink-100 text-pink-800',
    'cold drinks': 'bg-blue-100 text-blue-800',
    'dessert': 'bg-purple-100 text-purple-800',
    'snacks': 'bg-orange-100 text-orange-800',
    'beverages': 'bg-cyan-100 text-cyan-800'
  }

  const key = (category || '').toLowerCase().trim()
  return colorMap[key] || 'bg-gray-100 text-gray-800'
}

/**
 * Format business hours
 * @param {string} openTime - Opening time (24h format)
 * @param {string} closeTime - Closing time (24h format)
 * @returns {string} Formatted business hours
 */
export const formatBusinessHours = (openTime, closeTime) => {
  if (!openTime || !closeTime) return 'Hours not set'

  const formatTime = (time) => {
    const [hours, minutes] = time.split(':')
    const hour24 = parseInt(hours)
    const hour12 = hour24 === 0 ? 12 : hour24 > 12 ? hour24 - 12 : hour24
    const period = hour24 < 12 ? 'AM' : 'PM'
    return `${hour12}:${minutes} ${period}`
  }

  return `${formatTime(openTime)} - ${formatTime(closeTime)}`
}

/**
 * Export utility for creating downloadable files
 * @param {object} data - Data to export
 * @param {string} filename - File name
 * @param {string} type - File type (json, csv, txt)
 * @returns {void} Triggers download
 */
export const exportToFile = (data, filename, type = 'json') => {
  let content, mimeType

  switch (type.toLowerCase()) {
    case 'json':
      content = JSON.stringify(data, null, 2)
      mimeType = 'application/json'
      filename = filename.endsWith('.json') ? filename : `${filename}.json`
      break

    case 'csv':
      if (Array.isArray(data) && data.length > 0) {
        const headers = Object.keys(data[0]).join(',')
        const rows = data.map(row => Object.values(row).join(','))
        content = [headers, ...rows].join('\n')
      } else {
        content = ''
      }
      mimeType = 'text/csv'
      filename = filename.endsWith('.csv') ? filename : `${filename}.csv`
      break

    case 'txt':
      content = typeof data === 'string' ? data : JSON.stringify(data, null, 2)
      mimeType = 'text/plain'
      filename = filename.endsWith('.txt') ? filename : `${filename}.txt`
      break

    default:
      throw new Error(`Unsupported export type: ${type}`)
  }

  try {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Export failed:', error)
    throw error
  }
}

/**
 * Import utility for reading uploaded files
 * @param {File} file - File to read
 * @param {string} type - Expected file type
 * @returns {Promise} Promise resolving to file content
 */
export const importFromFile = (file, type = 'json') => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (event) => {
      try {
        const content = event.target.result

        switch (type.toLowerCase()) {
          case 'json':
            resolve(JSON.parse(content))
            break

          case 'csv':
            const lines = content.split('\n')
            const headers = lines[0].split(',')
            const data = lines.slice(1).map(line => {
              const values = line.split(',')
              return headers.reduce((obj, header, index) => {
                obj[header.trim()] = values[index]?.trim()
                return obj
              }, {})
            })
            resolve(data)
            break

          case 'txt':
            resolve(content)
            break

          default:
            reject(new Error(`Unsupported import type: ${type}`))
        }
      } catch (error) {
        reject(error)
      }
    }

    reader.onerror = () => reject(new Error('File reading failed'))
    reader.readAsText(file)
  })
}

/**
 * Debounce function for performance optimization
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait) => {
  let timeout

  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }

    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function for performance optimization
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export const throttle = (func, limit) => {
  let inThrottle

  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * Deep clone an object
 * @param {any} obj - Object to clone
 * @returns {any} Cloned object
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (typeof obj === 'object') {
    const cloned = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key])
      }
    }
    return cloned
  }
}

/**
 * Check if object is empty
 * @param {object} obj - Object to check
 * @returns {boolean} True if empty
 */
export const isEmpty = (obj) => {
  if (!obj) return true
  if (Array.isArray(obj)) return obj.length === 0
  if (typeof obj === 'object') return Object.keys(obj).length === 0
  return !obj
}

/**
 * Generate random ID
 * @param {number} length - Length of ID (default: 8)
 * @returns {string} Random ID
 */
export const generateId = (length = 8) => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''

  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }

  return result
}

export const formatDateTime12h = (dateTime) => {
  const d = new Date(dateTime);

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');

  let hours = d.getHours();
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');

  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // إذا الساعة 0 خليها 12
  hours = String(hours).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds} ${ampm}`;
}
export const formatDateTime24h = (dateTime) => {
  const d = new Date(dateTime);

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}
// Default export object
export default {
  formatPrice,
  formatNumber,
  formatShortPrice,
  formatDate,
  formatReceiptDate,
  formatDateForFilename,
  formatTimeAgo,
  formatPercentage,
  formatPhone,
  formatFileSize,
  formatQuantity,
  capitalizeWords,
  truncateText,
  generateReceiptNo,
  generateTransactionId,
  formatStockStatus,
  formatPaymentMethod,
  parseCashInput,
  formatCashInput,
  sanitizeProductData,
  calculateDiscount,
  calculateTax,
  formatCurrency,
  getCategoryColorClass,
  formatBusinessHours,
  exportToFile,
  importFromFile,
  debounce,
  throttle,
  deepClone,
  isEmpty,
  generateId
}
