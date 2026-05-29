// stores/settings.js
import { defineStore } from "pinia";
import { reactive, watch } from "vue";
import { toRaw } from "vue";

const ALLOWED_CURRENCIES = [
  { code: "SAR", label: "Saudi Riyal", symbol: "﷼", locale: "en-SA" },
  { code: "USD", label: "US Dollar", symbol: "$", locale: "en-US" },
  { code: "EGP", label: "Egyptian Pound", symbol: "E£", locale: "en-EG" },
  { code: "AED", label: "UAE Dirham", symbol: "د.إ", locale: "en-AE" },
  { code: "GBP", label: "British Pound", symbol: "£", locale: "en-GB" },
  { code: "PKR", label: "Pakistani Rupee", symbol: "Rs", locale: "en-PK" },
];

const getCurrencyConfig = (currency) =>
  ALLOWED_CURRENCIES.find((item) => item.code === currency) || ALLOWED_CURRENCIES[0];

const normalizeCurrencyCode = (currency) => getCurrencyConfig(currency).code;

export const useSettingsStore = defineStore("settings", () => {
  const createDefaultSettings = () => ({
    store: {
      name: "",
      address: "",
      phone: "+62 812 3456 7890",
      email: "store@tailwindpos.com",
      taxId: "112233123",
      currencyCode: 'PKR',
      locale:'en-PK',
    },
    receipt: {
      showLogo: true,
      showThankYou: true,
      footerMessage: "Thank you for your visit!",
      size: "80mm",
    },
    pricing: {
      enableTax: false,
      taxRate: 10,
      taxName: "VAT",
      currency: "SAR",
      price_list: "Standard Selling"
    },
    appearance: {
      theme: "light",
      language: "en",
      primaryColor: "#06b6d4",
      fontSize: "sm"
    },
    printer: {
      terminalName: "",
      name: "",
      type: "thermal",
      connectionType: "usb",
      host: "",
      port: 9100,
      paperWidth: 80,
      copyCount: 1,
      autoPrint: true,
    },
    system: {
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Karachi',
      autoBackup: true,
      soundEffects: true,
      showScannerStatus: true,
      simpleData: true,
    },
  });

  const normalizeSettings = (incoming = {}) => {
    const defaults = createDefaultSettings();
    const normalized = { ...defaults };

    Object.entries(incoming || {}).forEach(([key, value]) => {
      if (
        value &&
        typeof value === "object" &&
        !Array.isArray(value) &&
        normalized[key] &&
        typeof normalized[key] === "object" &&
        !Array.isArray(normalized[key])
      ) {
        normalized[key] = { ...normalized[key], ...value };
      } else {
        normalized[key] = value;
      }
    });

    const pricingCurrency = normalizeCurrencyCode(normalized.pricing?.currency || normalized.store?.currencyCode);
    const storeCurrency = pricingCurrency;
    const storeCurrencyConfig = getCurrencyConfig(storeCurrency);

    normalized.store = {
      ...defaults.store,
      ...(normalized.store || {}),
      currencyCode: storeCurrency,
      locale: storeCurrencyConfig.locale,
    };
    normalized.pricing = {
      ...defaults.pricing,
      ...(normalized.pricing || {}),
      currency: pricingCurrency,
    };

    normalized.printer = {
      ...defaults.printer,
      ...(incoming?.printer || {}),
    };

    normalized.printer.terminalName =
      normalized.printer.terminalName || normalized.printer.name || "";
    normalized.printer.name = normalized.printer.name || normalized.printer.printerName || "";
    normalized.printer.connectionType =
      normalized.printer.connectionType || (normalized.printer.host ? "ethernet" : "usb");
    normalized.printer.paperWidth =
      Number(normalized.printer.paperWidth ?? normalized.printer.width ?? 80) || 80;
    normalized.printer.copyCount =
      Number(normalized.printer.copyCount ?? normalized.printer.copies ?? 1) || 1;
    normalized.printer.autoPrint =
      normalized.printer.autoPrint ?? normalized.printer.autoprint ?? true;
    normalized.printer.port = Number(normalized.printer.port ?? 9100) || 9100;

    return normalized;
  };

  const currencyOptions = ALLOWED_CURRENCIES;

  const settings = reactive(createDefaultSettings());

  const applyCurrencySettings = (currency) => {
    const config = getCurrencyConfig(currency);
    settings.store.currencyCode = config.code;
    settings.store.locale = config.locale;
    settings.pricing.currency = config.code;
    return config;
  };

  // ✅ تحويل Hex تک HSL
  const hexToHsl = (hex) => {
    let r = parseInt(hex.slice(1, 3), 16) / 255;
    let g = parseInt(hex.slice(3, 5), 16) / 255;
    let b = parseInt(hex.slice(5, 7), 16) / 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
        case g: h = ((b - r) / d + 2) / 6; break;
        case b: h = ((r - g) / d + 4) / 6; break;
      }
    }

    return {
      h: Math.round(h * 360),
      s: Math.round(s * 100),
      l: Math.round(l * 100)
    };
  };

  // ✅ تحويل HSL تک Hex
  const hslToHex = (h, s, l) => {
    s /= 100;
    l /= 100;
    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));

    const toHex = x => {
      const hex = Math.round(255 * f(x)).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    };

    return `#${toHex(0)}${toHex(8)}${toHex(4)}`.toUpperCase();
  };

  // ✅ حساب الدرجات الصحيحة وتطبيقها
  const generateAndApplyColorShades = (hexColor) => {
    const hsl = hexToHsl(hexColor);

    // خريطة Lightness لكل درجة
    const lightnessMap = {
      50: 95,    // خفيف جداً
      100: 90,   // خفيف
      200: 80,   // خفيف متوسط
      300: 70,   // متوسط خفيف
      400: 60,   // متوسط
      500: 50,   // الأساسي
      600: 45,   // داكن قليل
      700: 35,   // داكن
      800: 25,   // داكن جداً
      900: 15    // شديد الداكن
    };

    // حساب كل درجة وتطبيقها على CSS variables
    Object.entries(lightnessMap).forEach(([level, targetL]) => {
      const hexShade = hslToHex(hsl.h, hsl.s, targetL);
      document.documentElement.style.setProperty(
        `--primary-${level}`,
        hexShade
      );
    });

    console.log("✅ Color shades applied:", hexColor);
  };

  // Load settings from localStorage
  const loadSettings = () => {
    try {
      const savedSettings = localStorage.getItem("tailwind-pos-settings");
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        Object.assign(settings, normalizeSettings(parsed));
        // تطبيق الألوان عند التحميل
        generateAndApplyColorShades(settings.appearance.primaryColor);
        console.log("✅ Settings loaded from localStorage");
      } else {
        console.log("ℹ️ No saved settings found, using defaults");
        saveSettings();
      }
    } catch (error) {
      console.error("❌ Failed to load settings:", error);
    }
  };

  // Save settings to localStorage
  const saveSettings = () => {
    try {
      const settingsToSave = normalizeSettings(toRaw(settings));
      const color = settings.appearance.primaryColor;

      // تطبيق الألوان قبل المحفوظ کریں
      generateAndApplyColorShades(color);

      localStorage.setItem(
        "tailwind-pos-settings",
        JSON.stringify(settingsToSave)
      );
      console.log("✅ Settings saved to localStorage");
      return true;
    } catch (error) {
      console.error("❌ Failed to save settings:", error);
      return false;
    }
  };

  // use to Update Seeting
  const updateSettings = (newSettings) => {
    try {
      Object.assign(settings, newSettings);
      saveSettings();
      console.log("✅ Settings updated successfully");
      return true;
    } catch (error) {
      console.error("❌ Failed to update settings:", error);
      return false;
    }
  };

  const syncStoreIdentityFromCompany = (companyDoc = {}, posProfile = {}) => {
    const currentName = String(settings.store.name || "").trim();
    const currentAddress = String(settings.store.address || "").trim();
    const currentLogo = String(settings.store.logoUrl || "").trim();

    const companyName = companyDoc.company_name || companyDoc.name || posProfile.company || "";
    const companyLogo = companyDoc.default_letter_head || companyDoc.logo || posProfile.company_logo || "";

    if (!currentName && companyName) settings.store.name = companyName;
    if (!currentAddress && posProfile.warehouse) settings.store.address = posProfile.warehouse;
    if (!currentLogo && companyLogo) settings.store.logoUrl = companyLogo;

    if (!settings.pricing.price_list && posProfile.selling_price_list) {
      settings.pricing.price_list = posProfile.selling_price_list;
    }

    saveSettings();
  };

  // إعادة تعيين الإعدادات تک القيم پہلے سے طے شدہة
  const resetSettings = () => {
    try {
      Object.assign(settings, createDefaultSettings());
      saveSettings();
      console.log("✅ Settings reset to defaults");
      return true;
    } catch (error) {
      console.error("❌ Failed to reset settings:", error);
      return false;
    }
  };

  // ✅ مراقبة التغييرات والمحفوظ کریں التلقائي
  watch(
    () => settings.appearance.primaryColor,
    (newColor) => {
      console.log("⚡ Color changed to:", newColor);
      generateAndApplyColorShades(newColor);
      saveSettings();
    }
  );

  return {
    settings,
    loadSettings,
    saveSettings,
    updateSettings,
    resetSettings,
    applyCurrencySettings,
    syncStoreIdentityFromCompany,
    currencyOptions,
    generateAndApplyColorShades,
  };
});
