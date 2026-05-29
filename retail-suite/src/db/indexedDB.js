import { openDB } from 'idb'

let dbInstance = null

export async function initDB() {
  if (dbInstance) return dbInstance

  dbInstance = await openDB('RetailSuite', 3, {
    upgrade(db) {
      // جدول السےتجات
      if (!db.objectStoreNames.contains('products')) {
        db.createObjectStore('products', { keyPath: 'id' })
      }

      // جدول الإعدادات
      if (!db.objectStoreNames.contains('settings')) {
        db.createObjectStore('settings', { keyPath: 'key' })
      }

      // جدول الشيفتات
      if (!db.objectStoreNames.contains('shifts')) {
        const shiftsStore = db.createObjectStore('shifts', { keyPath: 'id' })
        shiftsStore.createIndex('date', 'startTime')
        shiftsStore.createIndex('userId', 'userId')
        shiftsStore.createIndex('status', 'status')
      }

        // جدول الانوائسز    
        if (!db.objectStoreNames.contains('invoices')) {
            const invoicesStore = db.createObjectStore('invoices', { keyPath: 'id' })
            invoicesStore.createIndex('date', 'date')
            invoicesStore.createIndex('customerId', 'customerId')
            invoicesStore.createIndex('status', 'status')
        }
    }
  })

  return dbInstance
}
