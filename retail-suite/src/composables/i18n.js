
// i18n.js -- Simple reactive translations for POS app
import { reactive } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const translations = {
  en: {
    // POS
    pos: 'Point of Sale',
    retail: 'Retail',
    wholesale: 'Wholesale',
    purchase: 'Purchase',
    search: 'Search by name, code, or category',
    signOut: 'Sign Out',
    cartEmpty: 'Cart Empty',
    noItems: 'No items found',
    loading: 'Loading items...',
    noMatch: 'No matching items',
    addToCart: 'Add to Cart',
    outOfStock: 'Out of Stock',
    limitedQty: 'Limited quantity',
    available: 'Available',
    // Cart
    total: 'TOTAL',
    subtotal: 'Subtotal',
    tax: 'Tax',
    discount: 'Discount',
    change: 'CHANGE',
    insufficient: 'INSUFFICIENT',
    exactAmount: 'EXACT AMOUNT',
    partialPayment: 'Partial Payment',
    completeSale: 'COMPLETE SALE',
    createReceipt: 'CREATE RECEIPT',
    needMore: 'NEED',
    more: 'MORE',
    cash: 'Cash',
    paymentMethod: 'Payment Method',
    clearCart: 'Clear Cart',
    remove: 'Remove',
    clear: 'Clear',
    exact: 'Exact',
    // Customer
    customer: 'Customer',
    selectCustomer: 'Select Customer',
    walkInCustomer: 'Walk-in Customer',
    createNewCustomer: '+ Create New Customer',
    supplier: 'Supplier',
    selectSupplier: 'Select Supplier',
    // Shift
    openShift: 'Open Shift',
    closeShift: 'Close Shift',
    shiftRequired: 'Please open a shift before starting sales transactions.',
    // Price
    priceList: 'Price List',
    warehouse: 'Warehouse',
    reload: 'Reload',
    items: 'items',
    item: 'item',
    inCart: 'in cart',
  },
  ur: {
    // POS
    pos: 'سیلز پوائنٹ',
    retail: 'ریٹیل',
    wholesale: 'ہول سیل',
    purchase: 'خریداری',
    search: 'نام، کوڈ یا کیٹیگری سے تلاش کریں',
    signOut: 'سائن آؤٹ',
    cartEmpty: 'کارٹ خالی ہے',
    noItems: 'کوئی چیز نہیں ملی',
    loading: 'لوڈ ہو رہا ہے...',
    noMatch: 'کوئی مماثل چیز نہیں',
    addToCart: 'کارٹ میں شامل کریں',
    outOfStock: 'اسٹاک ختم',
    limitedQty: 'محدود مقدار',
    available: 'دستیاب',
    // Cart
    total: 'کل',
    subtotal: 'ذیلی کل',
    tax: 'ٹیکس',
    discount: 'رعایت',
    change: 'باقی رقم',
    insufficient: 'رقم کم ہے',
    exactAmount: 'پوری رقم',
    partialPayment: 'جزوی ادائیگی',
    completeSale: 'فروخت مکمل کریں',
    createReceipt: 'رسید بنائیں',
    needMore: 'مزید',
    more: 'درکار',
    cash: 'نقد',
    paymentMethod: 'ادائیگی کا طریقہ',
    clearCart: 'کارٹ خالی کریں',
    remove: 'ہٹائیں',
    clear: 'صاف کریں',
    exact: 'پورا',
    // Customer
    customer: 'کسٹمر',
    selectCustomer: 'کسٹمر منتخب کریں',
    walkInCustomer: 'واک ان کسٹمر',
    createNewCustomer: '+ نیا کسٹمر',
    supplier: 'سپلائر',
    selectSupplier: 'سپلائر منتخب کریں',
    // Shift
    openShift: 'شفٹ کھولیں',
    closeShift: 'شفٹ بند کریں',
    shiftRequired: 'براہ کرم سیلز شروع کرنے سے پہلے شفٹ کھولیں۔',
    // Price
    priceList: 'قیمت کی فہرست',
    warehouse: 'گودام',
    reload: 'دوبارہ لوڈ',
    items: 'اشیاء',
    item: 'چیز',
    inCart: 'کارٹ میں',
  }
}

// Reactive translation function
export const useI18n = () => {
  const settingsStore = useSettingsStore()
  
  const t = (key) => {
    const lang = getLanguage()
    return translations[lang]?.[key] || translations.en?.[key] || key
  }
  
  const getLanguage = () => {
    return settingsStore.settings?.language || 'en'
  }
  
  const setLanguage = (lang) => {
    if (settingsStore.settings) {
      settingsStore.settings.language = lang
      settingsStore.saveSettings()
    }
    localStorage.setItem('app-language', lang)
  }
  
  const toggleLanguage = () => {
    const current = getLanguage()
    setLanguage(current === 'en' ? 'ur' : 'en')
  }
  
  return { t, getLanguage, setLanguage, toggleLanguage }
}

export default useI18n
