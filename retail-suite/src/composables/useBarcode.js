// composables/useBarcode.js

import { ref, computed } from 'vue'
import { searchProductByBarcode, searchProduct } from '@/api/api'

export const useBarcode = () => {
    // ✅ حیثیت
    const scannedBarcodes = ref([])
    const scanHistory = ref([])
    const scannerStats = ref({
        totalScans: 0,
        successfulScans: 0,
        failedScans: 0,
        averageConfidence: 0,
        averageResponseTime: 0
    })

    const lastScanTime = ref(null)
    const isScannerActive = ref(false)

    // ✅ الحقول المحسوبة
    const successRate = computed(() => {
        if (scannerStats.value.totalScans === 0) return 0
        return ((scannerStats.value.successfulScans / scannerStats.value.totalScans) * 100).toFixed(1)
    })

    const failureRate = computed(() => {
        if (scannerStats.value.totalScans === 0) return 0
        return ((scannerStats.value.failedScans / scannerStats.value.totalScans) * 100).toFixed(1)
    })

    // ✅ معالجة الباركود الناجح
    const recordSuccessfulScan = (barcode, product, confidence, responseTime) => {
        scannerStats.value.totalScans++
        scannerStats.value.successfulScans++

        // اپ ڈیٹ کریں متوسط الثقة
        const totalConfidence =
            scannerStats.value.averageConfidence * (scannerStats.value.successfulScans - 1) + confidence
        scannerStats.value.averageConfidence = totalConfidence / scannerStats.value.successfulScans

        // اپ ڈیٹ کریں متوسط وقت الاستجابة
        const totalTime =
            scannerStats.value.averageResponseTime * (scannerStats.value.successfulScans - 1) + responseTime
        scannerStats.value.averageResponseTime = totalTime / scannerStats.value.successfulScans

        // شامل کریں للسجل
        const scanRecord = {
            barcode,
            itemCode: product.item_code,
            itemName: product.item_name,
            quantity: product.actual_qty,
            price: product.rate,
            timestamp: new Date(),
            confidence,
            responseTime,
            status: 'success'
        }

        scanHistory.value.unshift(scanRecord)
        scannedBarcodes.value.push(barcode)
        lastScanTime.value = new Date()
        isScannerActive.value = true

        // امحفوظ کریں آخر 100 scan فقط
        if (scanHistory.value.length > 100) {
            scanHistory.value.pop()
        }

        console.log('✅ Scan recorded:', scanRecord)
    }

    // ✅ معالجة الباركود الفاشل
    const recordFailedScan = (barcode, reason) => {
        scannerStats.value.totalScans++
        scannerStats.value.failedScans++

        const failureRecord = {
            barcode,
            timestamp: new Date(),
            reason,
            status: 'failed'
        }

        scanHistory.value.unshift(failureRecord)
        lastScanTime.value = new Date()

        console.warn('❌ Scan failed:', failureRecord)
    }

    // ✅ التلاش کریں عن الباركود
    const searchBarcode = async (barcode, posProfile, priceList) => {
        const startTime = Date.now()

        try {
            const result = await searchProductByBarcode(barcode, posProfile, priceList)
            const responseTime = Date.now() - startTime

            if (result.success) {
                recordSuccessfulScan(barcode, result.product, 95, responseTime)
                return {
                    success: true,
                    product: result.product,
                    responseTime
                }
            } else {
                recordFailedScan(barcode, result.message)
                return {
                    success: false,
                    message: result.message,
                    responseTime
                }
            }

        } catch (error) {
            const responseTime = Date.now() - startTime
            recordFailedScan(barcode, error.message)

            return {
                success: false,
                message: error.message,
                responseTime
            }
        }
    }

    // ✅ التلاش کریں المتقدم
    const advancedSearch = async (searchTerm, posProfile, priceList) => {
        const startTime = Date.now()

        try {
            const result = await searchProduct(searchTerm, posProfile, priceList)
            const responseTime = Date.now() - startTime

            return {
                success: result.success,
                results: result.results,
                count: result.count,
                responseTime
            }

        } catch (error) {
            return {
                success: false,
                results: [],
                count: 0,
                message: error.message
            }
        }
    }

    // ✅ الحصول على سجل المسحات
    const getScanHistory = (limit = 10) => {
        return scanHistory.value.slice(0, limit)
    }

    // ✅ الحصول على إحصائيات مفصلة
    const getDetailedStats = () => {
        return {
            ...scannerStats.value,
            successRate: parseFloat(successRate.value),
            failureRate: parseFloat(failureRate.value),
            lastScanTime: lastScanTime.value,
            isScannerActive: isScannerActive.value,
            totalScannedBarcodes: scannedBarcodes.value.length,
            uniqueBarcodes: new Set(scannedBarcodes.value).size
        }
    }

    // ✅ ایکسپورٹ الإحصائيات
    const exportStats = () => {
        const stats = getDetailedStats()
        const csv = `
      Barcode Stats Report
      Date: ${new Date().toLocaleString()}

      Total Scans: ${stats.totalScans}
      Successful: ${stats.successfulScans}
      Failed: ${stats.failedScans}
      Success Rate: ${stats.successRate}%

      Average Confidence: ${stats.averageConfidence.toFixed(1)}%
      Average Response Time: ${stats.averageResponseTime.toFixed(0)}ms

      Unique Barcodes Scanned: ${stats.uniqueBarcodes}

      Recent Scans:
      ${scanHistory.value.slice(0, 20).map(s =>
            `${s.timestamp.toLocaleTimeString()} - ${s.barcode} - ${s.status}`
        ).join('\n')}
    `

        return csv
    }

    // ✅ إعادة تعيين الإحصائيات
    const resetStats = () => {
        scannerStats.value = {
            totalScans: 0,
            successfulScans: 0,
            failedScans: 0,
            averageConfidence: 0,
            averageResponseTime: 0
        }
        scanHistory.value = []
        scannedBarcodes.value = []
        lastScanTime.value = null
        isScannerActive.value = false

        console.log('🔄 Scanner stats reset')
    }

    // ✅ پرنٹ کریں الإحصائيات
    const printStats = () => {
        const stats = getDetailedStats()
        console.log(`
      ╔════════════════════════════════════════════╗
      ║         BARCODE SCANNER STATISTICS         ║
      ╠════════════════════════════════════════════╣
      ║ Total Scans:              ${stats.totalScans.toString().padEnd(20)} ║
      ║ Successful Scans:         ${stats.successfulScans.toString().padEnd(20)} ║
      ║ Failed Scans:             ${stats.failedScans.toString().padEnd(20)} ║
      ║ Success Rate:             ${(stats.successRate + '%').padEnd(20)} ║
      ║ Failure Rate:             ${(stats.failureRate + '%').padEnd(20)} ║
      ╠════════════════════════════════════════════╣
      ║ Average Confidence:       ${(stats.averageConfidence.toFixed(1) + '%').padEnd(20)} ║
      ║ Avg Response Time:        ${(stats.averageResponseTime.toFixed(0) + 'ms').padEnd(20)} ║
      ║ Unique Barcodes:          ${stats.uniqueBarcodes.toString().padEnd(20)} ║
      ║ Scanner Active:           ${(stats.isScannerActive ? 'Yes' : 'No').padEnd(20)} ║
      ║ Last Scan:                ${(stats.lastScanTime ? stats.lastScanTime.toLocaleTimeString() : 'Never').padEnd(20)} ║
      ╚════════════════════════════════════════════╝
    `)
    }

    return {
        // حیثیت
        scannedBarcodes,
        scanHistory,
        scannerStats,
        lastScanTime,
        isScannerActive,

        // الحقول المحسوبة
        successRate,
        failureRate,

        // الدوال
        recordSuccessfulScan,
        recordFailedScan,
        searchBarcode,
        advancedSearch,
        getScanHistory,
        getDetailedStats,
        exportStats,
        resetStats,
        printStats
    }
}
