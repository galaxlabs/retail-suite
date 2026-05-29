import qz from "qz-tray";
import { useSettingsStore } from "@/stores/settings";
import { formatPrice } from "@/utils/formatters";

let connectionPromise = null;
let securityReady = false;

const qzCertificateUrl = import.meta.env.VITE_QZ_CERT_URL?.trim();
const qzSignatureUrl = import.meta.env.VITE_QZ_SIGNATURE_URL?.trim();

const connectQz = async () => {
  if (qz.websocket.isActive()) {
    return true;
  }

  if (!connectionPromise) {
    connectionPromise = qz.websocket.connect({ retries: 2, delay: 250 }).finally(() => {
      connectionPromise = null;
    });
  }

  return connectionPromise;
};

const setupQzSecurity = () => {
  if (securityReady) {
    return;
  }

  if (qzCertificateUrl) {
    qz.security.setCertificatePromise(async () => {
      const response = await fetch(qzCertificateUrl, { credentials: "include" });
      if (!response.ok) {
        throw new Error(`Failed to load QZ certificate (${response.status})`);
      }
      return response.text();
    });
  }

  if (qzSignatureUrl) {
    qz.security.setSignaturePromise(async (dataToSign) => {
      const response = await fetch(qzSignatureUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ data: dataToSign }),
      });

      if (!response.ok) {
        throw new Error(`Failed to sign QZ request (${response.status})`);
      }

      return response.text();
    });
  }

  securityReady = true;
};

const resolvePrinterProfile = () => {
  const settingsStore = useSettingsStore();
  const printer = settingsStore.settings?.printer || {};

  const paperWidth = Number(printer.paperWidth ?? printer.width ?? 80) || 80;
  const copyCount = Math.max(1, Number(printer.copyCount ?? printer.copies ?? 1) || 1);
  const connectionType = (printer.connectionType || (printer.host ? "ethernet" : "usb")).toLowerCase();
  const printerName = printer.name || printer.printerName || printer.terminalName || "Retail Printer";
  const terminalName = printer.terminalName || printer.name || "POS Terminal";
  const host = printer.host || "";
  const port = Number(printer.port ?? 9100) || 9100;
  const autoPrint = printer.autoPrint ?? printer.autoprint ?? true;
  const useQzTray = printer.useQzTray ?? printer.qzEnabled ?? false;

  return {
    raw: printer,
    paperWidth,
    copyCount,
    connectionType,
    printerName,
    terminalName,
    host,
    port,
    useQzTray,
    autoPrint,
  };
};

const getPrintTarget = (profile) => {
  if (profile.connectionType === "ethernet") {
    return {
      host: profile.host,
      port: profile.port,
      name: profile.printerName,
    };
  }

  return profile.printerName;
};

const buildReceiptHtml = (receiptData, profile) => {
  const summary = receiptData?.summary || {};
  const items = receiptData?.items || [];
  const invoiceNo = receiptData?.invoiceNo || receiptData?.invoiceId || "TEMP";
  const timestamp = receiptData?.timestamp ? new Date(receiptData.timestamp) : new Date();
  const dateText = timestamp.toLocaleDateString("en-GB");
  const timeText = timestamp.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
  const widthMm = profile.paperWidth || 80;

  const itemRows = items.map((item, index) => `
      <tr>
        <td style="padding: 2px 0; width: 24px; vertical-align: top;">${index + 1}.</td>
        <td style="padding: 2px 0; vertical-align: top;">
          <div style="font-weight: 600;">${item.item_name || item.item_code || "Item"}</div>
          <div style="font-size: 10px; color: #666;">${item.item_code || ""}</div>
        </td>
        <td style="padding: 2px 0; text-align: center; width: 36px; vertical-align: top;">${item.qty || 0}</td>
        <td style="padding: 2px 0; text-align: right; width: 80px; vertical-align: top;">${formatPrice(item.rate || 0)}</td>
        <td style="padding: 2px 0; text-align: right; width: 90px; vertical-align: top;">${formatPrice((item.qty || 0) * (item.rate || 0))}</td>
      </tr>
    `).join("");

  return `
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          @page {
            size: ${widthMm}mm auto;
            margin: 0;
          }
          html, body {
            width: ${widthMm}mm;
            margin: 0;
            padding: 0;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 11px;
            color: #111;
          }
          .receipt {
            width: ${widthMm}mm;
            padding: 8mm 6mm;
            box-sizing: border-box;
          }
          .center { text-align: center; }
          .muted { color: #666; }
          .divider {
            border-top: 1px dashed #999;
            margin: 8px 0;
          }
          table {
            width: 100%;
            border-collapse: collapse;
          }
          .summary-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin: 2px 0;
          }
          .summary-total {
            font-size: 13px;
            font-weight: 700;
          }
        </style>
      </head>
      <body>
        <div class="receipt">
          <div class="center">
            <div style="font-size: 16px; font-weight: 700; text-transform: uppercase;">${receiptData?.storeName || "Store"}</div>
            <div class="muted" style="margin-top: 4px;">${receiptData?.storeAddress || ""}</div>
            <div class="muted">${profile.terminalName || "POS Terminal"}</div>
          </div>

          <div class="divider"></div>

          <div class="summary-row"><span>Invoice</span><span>${invoiceNo}</span></div>
          <div class="summary-row"><span>Date</span><span>${dateText}</span></div>
          <div class="summary-row"><span>Time</span><span>${timeText}</span></div>
          <div class="summary-row"><span>Printer</span><span>${profile.printerName}</span></div>
          <div class="summary-row"><span>Copy</span><span>${profile.copyCount}</span></div>

          <div class="divider"></div>

          <table>
            <thead>
              <tr>
                <th style="padding: 2px 0; text-align: left;">#</th>
                <th style="padding: 2px 0; text-align: left;">Item</th>
                <th style="padding: 2px 0; text-align: center;">Qty</th>
                <th style="padding: 2px 0; text-align: right;">Price</th>
                <th style="padding: 2px 0; text-align: right;">Total</th>
              </tr>
            </thead>
            <tbody>
              ${itemRows}
            </tbody>
          </table>

          <div class="divider"></div>

          <div class="summary-row"><span>Subtotal</span><span>${formatPrice(summary.subtotal || 0)}</span></div>
          ${summary.tax > 0 ? `<div class="summary-row"><span>Tax</span><span>${formatPrice(summary.tax)}</span></div>` : ""}
          ${summary.discount > 0 ? `<div class="summary-row"><span>Discount</span><span>- ${formatPrice(summary.discount)}</span></div>` : ""}
          <div class="summary-row summary-total"><span>Total</span><span>${formatPrice(summary.total || 0)}</span></div>
          <div class="summary-row"><span>Cash</span><span>${formatPrice(summary.cash || 0)}</span></div>
          <div class="summary-row"><span>Change</span><span>${formatPrice(summary.change || 0)}</span></div>

          <div class="divider"></div>

          <div class="center muted">${receiptData?.footerMessage || "Thank you for your visit!"}</div>
        </div>
      </body>
    </html>
  `;
};

export const printReceipt = async (receiptData, options = {}) => {
  if (!receiptData) {
    throw new Error("Missing receipt data for printing");
  }

  const profile = resolvePrinterProfile();
  if (!options.force && profile.autoPrint === false) {
    return { skipped: true, reason: 'auto_print_disabled' };
  }
  if (!profile.useQzTray) {
    return { skipped: true, reason: 'qz_disabled' };
  }

  setupQzSecurity();
  const hadConnection = qz.websocket.isActive();

  try {
    await connectQz();

    const target = getPrintTarget(profile);
    const config = qz.configs.create(target, {
      copies: profile.copyCount,
      jobName: `${profile.terminalName || "POS"}-${receiptData.invoiceNo || receiptData.invoiceId || "receipt"}`,
      margins: 0,
      units: "mm",
    });

    const html = buildReceiptHtml(receiptData, profile);
    const payload = [{
      type: "raw",
      format: "html",
      flavor: "plain",
      data: html,
      options: {
        language: "escpos",
        dotDensity: "single",
        pageWidth: profile.paperWidth,
      },
    }];

    await qz.print(config, payload);
    return { success: true };
  } finally {
    if (!hadConnection && qz.websocket.isActive()) {
      await qz.websocket.disconnect().catch(() => {});
    }
  }
};

export const buildSampleReceipt = () => ({
  storeName: "Store",
  storeAddress: "",
  invoiceNo: `TEST-${Date.now().toString().slice(-6)}`,
  timestamp: new Date().toISOString(),
  items: [
    { item_code: "TEST-ITEM", item_name: "Thermal Print Test", qty: 1, rate: 1 },
  ],
  summary: {
    subtotal: 1,
    tax: 0,
    discount: 0,
    total: 1,
    cash: 1,
    change: 0,
  },
  footerMessage: "Test print completed",
});
