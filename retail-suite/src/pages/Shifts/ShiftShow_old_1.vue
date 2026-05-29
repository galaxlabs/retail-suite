<!-- ShiftShow.vue — Enhanced Analytics Dashboard -->
<template>


    <!-- ═══════════════════════════════════════════
         LOADING
    ════════════════════════════════════════════ -->
    <div v-if="loading" class="ss-loader">
      <div class="ss-loader__ring"></div>
      <span class="ss-loader__text">جاري التحميل...</span>
    </div>

    <!-- ═══════════════════════════════════════════
         MAIN CONTENT
    ════════════════════════════════════════════ -->
    <div v-else-if="shift" class="ss-root">

      <!-- ── HEADER ─────────────────────────────── -->
      <header class="ss-header">
        <div class="ss-header__left">
          <button class="ss-back-btn" @click="goBack">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
            رجوع
          </button>
          <div class="ss-header__title-group">
            <h1 class="ss-header__title">الوردية #{{ shift.id || shift.name }}</h1>
            <div class="ss-badge" :class="shift.status === 'open' ? 'ss-badge--open' : 'ss-badge--closed'">
              <span class="ss-badge__dot"></span>
              {{ shift.status === 'open' ? 'مفتوحة' : 'مغلقة' }}
            </div>
          </div>
          <div class="ss-header__meta">
            <span>{{ formatDate(shift.period_start_date) }}</span>
            <span class="ss-sep">→</span>
            <span>{{ shift.period_end_date ? formatDate(shift.period_end_date) : 'الآن' }}</span>
          </div>
        </div>
        <div class="ss-header__actions">
          <button class="ss-btn ss-btn--ghost" @click="printShiftReport">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
            طباعة
          </button>
          <button v-if="shift.status === 'open'" class="ss-btn ss-btn--danger" @click="showCloseShiftModal = true">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            إغلاق الوردية
          </button>
        </div>
      </header>

      <!-- ── KPI STRIP ──────────────────────────── -->
      <section class="ss-kpi-strip">

        <div class="ss-kpi ss-kpi--primary">
          <div class="ss-kpi__icon ss-kpi__icon--green">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
          </div>
          <div class="ss-kpi__body">
            <span class="ss-kpi__label">إجمالي المبيعات</span>
            <span class="ss-kpi__value">{{ formatCurrency(shift.total_sales, currencyCode, locale) }}</span>
            <span class="ss-kpi__sub">{{ invoices.length }} فاتورة</span>
          </div>
        </div>

        <div class="ss-kpi">
          <div class="ss-kpi__icon ss-kpi__icon--blue">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>
          </div>
          <div class="ss-kpi__body">
            <span class="ss-kpi__label">رصيد الافتتاح</span>
            <span class="ss-kpi__value">{{ formatCurrency(shift.opening_cash, currencyCode, locale) }}</span>
            <span class="ss-kpi__sub">{{ shift.opened_by_name || '—' }}</span>
          </div>
        </div>

        <div class="ss-kpi" v-if="shift.status === 'closed'">
          <div class="ss-kpi__icon ss-kpi__icon--purple">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
          </div>
          <div class="ss-kpi__body">
            <span class="ss-kpi__label">رصيد الإغلاق</span>
            <span class="ss-kpi__value">{{ formatCurrency(shift.closing_cash, currencyCode, locale) }}</span>
            <span class="ss-kpi__sub">{{ shift.closed_by_name || '—' }}</span>
          </div>
        </div>

        <div class="ss-kpi">
          <div class="ss-kpi__icon ss-kpi__icon--cyan">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <div class="ss-kpi__body">
            <span class="ss-kpi__label">متوسط الفاتورة</span>
            <span class="ss-kpi__value">{{ formatCurrency(avgInvoice, currencyCode, locale) }}</span>
            <span class="ss-kpi__sub">{{ salesInvoicesCount }} فاتورة مبيعات</span>
          </div>
        </div>

        <div class="ss-kpi">
          <div class="ss-kpi__icon ss-kpi__icon--orange">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h2l.4 2M7 13h10l4-8H5.4"/><circle cx="9" cy="19" r="1"/><circle cx="20" cy="19" r="1"/></svg>
          </div>
          <div class="ss-kpi__body">
            <span class="ss-kpi__label">إجمالي الكميات</span>
            <span class="ss-kpi__value">{{ totalQty }}</span>
            <span class="ss-kpi__sub">صنف مباع</span>
          </div>
        </div>

        <div class="ss-kpi" v-if="returnInvoicesCount > 0">
          <div class="ss-kpi__icon ss-kpi__icon--red">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/></svg>
          </div>
          <div class="ss-kpi__body">
            <span class="ss-kpi__label">واپسیاں</span>
            <span class="ss-kpi__value ss-kpi__value--red">{{ formatCurrency(totalReturns, currencyCode, locale) }}</span>
            <span class="ss-kpi__sub">{{ returnInvoicesCount }} واپسی</span>
          </div>
        </div>

        <div class="ss-kpi" v-if="shift.status === 'closed'">
          <div class="ss-kpi__icon" :class="cashDifference === 0 ? 'ss-kpi__icon--green' : cashDifference > 0 ? 'ss-kpi__icon--blue' : 'ss-kpi__icon--red'">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
          </div>
          <div class="ss-kpi__body">
            <span class="ss-kpi__label">الفارق النقدي</span>
            <span class="ss-kpi__value" :class="cashDifference < 0 ? 'ss-kpi__value--red' : cashDifference > 0 ? 'ss-kpi__value--green' : ''">
              {{ cashDifference >= 0 ? '+' : '' }}{{ formatCurrency(cashDifference, currencyCode, locale) }}
            </span>
            <span class="ss-kpi__sub">{{ cashDifference === 0 ? 'متوازن' : cashDifference > 0 ? 'فائض' : 'عجز' }}</span>
          </div>
        </div>

      </section>

      <!-- ── ANALYTICS ROW ──────────────────────── -->
      <section class="ss-analytics-row">

        <!-- Payment breakdown bar -->
        <div class="ss-card ss-analytics-payments">
          <div class="ss-card__header">
            <h2 class="ss-card__title">توزيع طرق الدفع</h2>
          </div>
          <div class="ss-payment-bars">
            <div v-for="pm in paymentBreakdown" :key="pm.mode_of_payment" class="ss-payment-bar-item">
              <div class="ss-payment-bar-item__top">
                <span class="ss-payment-bar-item__name">{{ pm.mode_of_payment }}</span>
                <span class="ss-payment-bar-item__val">{{ formatCurrency(pm.expected_amount, currencyCode, locale) }}</span>
              </div>
              <div class="ss-payment-bar-item__track">
                <div class="ss-payment-bar-item__fill" :style="{ width: pm.pct + '%', background: pm.color }"></div>
              </div>
              <div class="ss-payment-bar-item__pct">{{ pm.pct }}%</div>
            </div>
            <p v-if="!paymentBreakdown.length" class="ss-empty">ادائیگیاں موجود نہیں</p>
          </div>
        </div>

        <!-- Hourly sales mini chart -->
        <div class="ss-card ss-analytics-hourly">
          <div class="ss-card__header">
            <h2 class="ss-card__title">المبيعات حسب الساعة</h2>
          </div>
          <div class="ss-hourly-chart" v-if="hourlySales.length">
            <div
              v-for="h in hourlySales"
              :key="h.hour"
              class="ss-hourly-bar"
              :title="`${h.hour}:00 — ${formatCurrency(h.total, currencyCode, locale)}`"
            >
              <div class="ss-hourly-bar__fill" :style="{ height: h.pct + '%' }"></div>
              <span class="ss-hourly-bar__label">{{ h.hour }}</span>
            </div>
          </div>
          <p v-else class="ss-empty" style="padding: 14px">لا توجد بيانات</p>
        </div>

        <!-- Staff performance -->
        <div class="ss-card ss-analytics-staff">
          <div class="ss-card__header">
            <h2 class="ss-card__title">أداء الكاشيرية</h2>
          </div>
          <div class="ss-staff-list">
            <div v-for="(s, idx) in staffPerformance" :key="s.owner" class="ss-staff-item">
              <div class="ss-staff-item__rank">#{{ idx + 1 }}</div>
              <div class="ss-staff-item__avatar">{{ initials(s.owner) }}</div>
              <div class="ss-staff-item__info">
                <span class="ss-staff-item__name">{{ s.fullName || s.owner }}</span>
                <span class="ss-staff-item__sub">{{ s.count }} فاتورة</span>
              </div>
              <div class="ss-staff-item__sales">{{ formatCurrency(s.total, currencyCode, locale) }}</div>
            </div>
            <p v-if="!staffPerformance.length" class="ss-empty">لا توجد بيانات</p>
          </div>
        </div>

      </section>

      <!-- ── TABS ───────────────────────────────── -->
      <section class="ss-tabs-section">
        <div class="ss-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="ss-tab"
            :class="{ 'ss-tab--active': activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
            <span class="ss-tab__badge">{{ tab.count }}</span>
          </button>
        </div>
      </section>

      <!-- ── INVOICES TABLE ─────────────────────── -->
      <section v-show="activeTab === 'invoices'" class="ss-table-section">
        <div class="ss-card">

          <div class="ss-table-toolbar">
            <div class="ss-search">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input v-model="invoiceSearch" class="ss-search__input" placeholder="بحث بالفاتورة، العميل، الكاشير..." />
              <button v-if="invoiceSearch" class="ss-search__clear" @click="invoiceSearch = ''">✕</button>
            </div>
            <div class="ss-filters">
              <select v-model="invoiceStatusFilter" class="ss-select">
                <option value="">كل الحالات</option>
                <option value="Paid">ادا شدہ</option>
                <option value="Return">واپسی</option>
                <option value="Draft">مسودہ</option>
                <option value="credit note issued">کریڈٹ نوٹ</option>
                <option value="partly paid">جزوی ادائیگی</option>
                <option value="unpaid">غیر ادا شدہ</option>


              </select>
              <select v-model="invoicePaymentFilter" class="ss-select">
                <option value="">كل طرق الدفع</option>
                <option v-for="pm in uniquePaymentMethods" :key="pm" :value="pm">{{ pm }}</option>
              </select>
              <select v-model="invoiceSortBy" class="ss-select">
                <option value="date_desc">الأحدث أولاً</option>
                <option value="date_asc">الأقدم أولاً</option>
                <option value="total_desc">الأعلى قيمة</option>
                <option value="total_asc">الأقل قيمة</option>
              </select>
            </div>
            <div class="ss-table-meta">
              <span class="ss-table-meta__count">{{ filteredInvoices.length }} نتيجة</span>
              <button class="ss-btn ss-btn--ghost ss-btn--sm" @click="exportInvoices">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                تصدير
              </button>
            </div>
          </div>

          <div class="ss-table-wrap">
            <table class="ss-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th class="ss-th-sort" @click="setSortInvoice('name')">الفاتورة</th>
                  <th class="ss-th-sort" @click="setSortInvoice('posting_date')">التاريخ والوقت</th>
                  <th>العميل</th>
                  <th class="ss-th-sort" @click="setSortInvoice('grand_total')">الإجمالي</th>
                  <th>الكمية</th>
                  <th>الدفع</th>
                  <th>الكاشير</th>
                  <th>الحالة</th>
                  <th>إجراءات</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(inv, idx) in paginatedInvoices"
                  :key="inv.name"
                  class="ss-tr"
                  :class="{ 'ss-tr--return': flt(inv.total) < 0 }"
                >
                  <td class="ss-td-num">{{ invoicePageOffset + idx + 1 }}</td>
                  <td>
                    <button class="ss-link" @click="viewInvoice(inv.name)">{{ inv.name }}</button>
                  </td>
                  <td class="ss-td-muted">{{ formatDate(inv.posting_date) }} {{ formatTime(inv.posting_time) }}</td>
                  <td>{{ inv.customer_name || 'زبون عادي' }}</td>
                  <td class="ss-td-amount" :class="flt(inv.grand_total) < 0 ? 'ss-td-amount--neg' : ''">
                    {{ formatCurrency(inv.total, currencyCode, locale) }}
                  </td>
                  <td class="ss-td-muted">{{ inv.total_qty || '—' }}</td>
                  <!-- <td>
                    <span class="ss-chip ss-chip--info">{{ inv.payment_method || getInvoicePrimaryPayment(inv) }}</span>
                  </td> -->
                  <td>
  <div style="display:flex;flex-wrap:wrap;gap:3px;">
    <template v-if="inv.all_payments && inv.all_payments.length">
      <span
        v-for="(p, pi) in getUniquePayments(inv)"
        :key="pi"
        class="ss-chip"
        :class="p.source === 'payment_entry' ? 'ss-chip--warning' : 'ss-chip--info'"
        :title="p.source === 'payment_entry' ? 'Payment Entry: ' + p.payment_entry : 'POS'"
      >
        {{ p.mode_of_payment }}
      </span>
    </template>
    <span v-else class="ss-chip ss-chip--info">
      {{ inv.payment_method || '—' }}
    </span>
  </div>
</td>

                  <td class="ss-td-muted">{{ inv.cashier_name }}</td>
                  <td>
                    <span class="ss-chip" :class="getStatusClass(inv)">{{ getStatusLabel(inv) }}</span>
                  </td>
                  <td>
                    <div class="ss-row-actions">
                      <button class="ss-icon-btn" title="عرض" @click="viewInvoice(inv.name)">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                      </button>
                      <button class="ss-icon-btn ss-icon-btn--green" title="طباعة" @click="printInvoice(inv.name)">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!filteredInvoices.length">
                  <td colspan="10" class="ss-empty-row">لا توجد نتائج مطابقة</td>
                </tr>
              </tbody>
              <tfoot v-if="filteredInvoices.length">
                <tr class="ss-tfoot">
                  <td colspan="4" class="ss-tfoot__label">الإجمالي ({{ filteredInvoices.length }} فاتورة)</td>
                  <td class="ss-tfoot__val">{{ formatCurrency(filteredInvoicesTotal, currencyCode, locale) }}</td>
                  <td>{{ filteredInvoicesQty }}</td>
                  <td colspan="4"></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <div class="ss-pagination" v-if="invoiceTotalPages > 1">
            <button class="ss-page-btn" :disabled="invoicePage === 1" @click="invoicePage--">‹</button>
            <button
              v-for="p in invoiceTotalPages"
              :key="p"
              class="ss-page-btn"
              :class="{ 'ss-page-btn--active': p === invoicePage }"
              @click="invoicePage = p"
            >{{ p }}</button>
            <button class="ss-page-btn" :disabled="invoicePage === invoiceTotalPages" @click="invoicePage++">›</button>
          </div>

        </div>
      </section>

      <!-- ── TRANSACTIONS TABLE ──────────────────── -->
      <section v-show="activeTab === 'transactions'" class="ss-table-section">
        <div class="ss-card">

          <div class="ss-table-toolbar">
            <div class="ss-search">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input v-model="txSearch" class="ss-search__input" placeholder="بحث في المعاملات..." />
              <button v-if="txSearch" class="ss-search__clear" @click="txSearch = ''">✕</button>
            </div>
            <div class="ss-filters">
              <select v-model="txTypeFilter" class="ss-select">
                <option value="">كل الأنواع</option>
                <option value="in">وارد</option>
                <option value="out">صادر</option>
              </select>
              <select v-model="txPaymentFilter" class="ss-select">
                <option value="">كل طرق الدفع</option>
                <option v-for="pm in uniquePaymentMethods" :key="pm" :value="pm">{{ pm }}</option>
              </select>
            </div>
            <div class="ss-table-meta">
              <span class="ss-table-meta__count ss-table-meta__count--green">↑ {{ formatCurrency(txTotalIn, currencyCode, locale) }}</span>
              <span class="ss-table-meta__count ss-table-meta__count--red">↓ {{ formatCurrency(txTotalOut, currencyCode, locale) }}</span>
            </div>
          </div>

          <div class="ss-table-wrap">
            <table class="ss-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>النوع</th>
                  <th>الوصف</th>
                  <th>طريقة الدفع</th>
                  <th>المبلغ</th>
                  <th>التاريخ</th>
                  <th>بواسطة</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(tx, idx) in filteredTransactions"
                  :key="idx"
                  class="ss-tr"
                  :class="tx.type === 'out' ? 'ss-tr--out' : ''"
                >
                  <td class="ss-td-num">{{ idx + 1 }}</td>
                  <td>
                    <div class="ss-tx-type" :class="tx.type === 'in' ? 'ss-tx-type--in' : 'ss-tx-type--out'">
                      <svg v-if="tx.type === 'in'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
                      <svg v-else width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>
                      {{ tx.type === 'in' ? 'وارد' : 'صادر' }}
                    </div>
                  </td>
                  <td>{{ tx.description }}</td>
                  <td><span class="ss-chip ss-chip--info">{{ tx.mode_of_payment }}</span></td>
                  <td class="ss-td-amount" :class="tx.type === 'in' ? 'ss-td-amount--pos' : 'ss-td-amount--neg'">
                    {{ tx.type === 'in' ? '+' : '−' }}{{ formatCurrency(tx.amount, currencyCode, locale) }}
                  </td>
                  <td class="ss-td-muted">{{ formatDate(tx.created_at) }}</td>
                  <td class="ss-td-muted">{{ tx.user_name }}</td>
                </tr>
                <tr v-if="!filteredTransactions.length">
                  <td colspan="7" class="ss-empty-row">لا توجد معاملات</td>
                </tr>
              </tbody>
              <tfoot v-if="filteredTransactions.length">
                <tr class="ss-tfoot">
                  <td colspan="4" class="ss-tfoot__label">الصافي</td>
                  <td class="ss-tfoot__val" :class="txNet >= 0 ? '' : 'ss-td-amount--neg'">
                    {{ txNet >= 0 ? '+' : '−' }}{{ formatCurrency(Math.abs(txNet), currencyCode, locale) }}
                  </td>
                  <td colspan="2"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </section>

      <!-- ── PAYMENTS RECONCILIATION TABLE ────────── -->
      <section v-show="activeTab === 'payments'" class="ss-table-section">
        <div class="ss-card">

          <div class="ss-table-toolbar">
            <div class="ss-search">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input v-model="pmSearch" class="ss-search__input" placeholder="بحث في طرق الدفع..." />
            </div>
          </div>

          <div class="ss-table-wrap">
            <table class="ss-table">
              <thead>
                <tr>
                  <th>طريقة الدفع</th>
                  <th>الرصيد الافتتاحي</th>
                  <th>المتوقع</th>
                  <th>الفعلي</th>
                  <th>الفارق</th>
                  <th>نسبة الفارق</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pm in filteredPayments" :key="pm.mode_of_payment" class="ss-tr">
                  <td><span class="ss-chip ss-chip--info">{{ pm.mode_of_payment }}</span></td>
                  <td class="ss-td-muted">{{ formatCurrency(pm.opening_amount || 0, currencyCode, locale) }}</td>
                  <td>{{ formatCurrency(pm.expected_amount || 0, currencyCode, locale) }}</td>
                  <td>{{ formatCurrency(pm.closing_amount || 0, currencyCode, locale) }}</td>
                  <td>
                    <span :class="(pm.difference||0) < 0 ? 'ss-td-amount--neg' : (pm.difference||0) > 0 ? 'ss-td-amount--pos' : 'ss-td-muted'">
                      {{ (pm.difference||0) >= 0 ? '+' : '' }}{{ formatCurrency(pm.difference || 0, currencyCode, locale) }}
                    </span>
                  </td>
                  <td>
                    <div style="display:flex;align-items:center;gap:6px">
                      <div class="ss-diff-bar">
                        <div class="ss-diff-bar__fill" :style="{ width: Math.min(Math.abs(pmDiffPct(pm)),100)+'%', background: (pm.difference||0)<0?'var(--ss-red)':'var(--ss-green)' }"></div>
                      </div>
                      <span class="ss-diff-pct">{{ pmDiffPct(pm) }}%</span>
                    </div>
                  </td>
                </tr>
                <tr v-if="!filteredPayments.length">
                  <td colspan="6" class="ss-empty-row">لا توجد بيانات</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
      <!-- Tab جديد: مشاكل التسوية -->
<section v-show="activeTab === 'issues'" class="ss-table-section">
  <div class="ss-card">

    <!-- ملخص سريع -->
    <div v-if="shift.reconciliation_issues?.length" class="ss-alert ss-alert--warning">
      ⚠️ يوجد {{ shift.reconciliation_issues.length }} فاتورة بها فروقات في الدفع
    </div>

    <div class="ss-table-wrap">
      <table class="ss-table">
        <thead>
          <tr>
            <th>الفاتورة</th>
            <th>العميل</th>
            <th>إجمالي الفاتورة</th>
            <th>مجموع الدفعات</th>
            <th>الفارق</th>
            <th>النوع</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="issue in shift.reconciliation_issues" :key="issue.invoice" class="ss-tr">
            <td>
              <button class="ss-link" @click="viewInvoice(issue.invoice)">
                {{ issue.invoice }}
              </button>
            </td>
            <td>{{ issue.customer }}</td>
            <td>{{ formatCurrency(issue.invoice_total, currencyCode, locale) }}</td>
            <td>{{ formatCurrency(issue.total_collected, currencyCode, locale) }}</td>
            <td>
              <span :class="issue.issue_type === 'overpaid' ? 'ss-td-amount--pos' : 'ss-td-amount--neg'">
                {{ issue.difference > 0 ? '-' : '+' }}
                {{ formatCurrency(Math.abs(issue.difference), currencyCode, locale) }}
              </span>
            </td>
            <td>
              <span class="ss-chip" :class="issue.issue_type === 'overpaid' ? 'ss-chip--success' : 'ss-chip--danger'">
                {{ issue.issue_type === 'overpaid' ? 'دفع زائد' : 'دفع ناقص' }}
              </span>
            </td>
          </tr>

          <!-- الدفعات غير المخصصة -->
          <tr v-if="shift.unallocated_payments?.length">
            <td colspan="6" style="background:var(--warning-bg);padding:6px 12px;font-size:11px;color:var(--warning-border);font-weight:600;">
              ⚠️ دفعات غير مخصصة لأي فاتورة ({{ shift.unallocated_payments.length }})
            </td>
          </tr>
          <tr v-for="pe in shift.unallocated_payments" :key="pe.payment_entry" class="ss-tr ss-tr--return">
            <td>{{ pe.payment_entry }}</td>
            <td>{{ pe.party_name || pe.party }}</td>
            <td>{{ formatCurrency(pe.paid_amount, currencyCode, locale) }}</td>
            <td>—</td>
            <td class="ss-td-amount--neg">
              {{ formatCurrency(pe.unallocated_amount, currencyCode, locale) }}
            </td>
            <td><span class="ss-chip ss-chip--warning">غير مخصصة</span></td>
          </tr>

          <tr v-if="!shift.reconciliation_issues?.length && !shift.unallocated_payments?.length">
            <td colspan="6" class="ss-empty-row">✅ لا توجد فروقات، كل الدفعات متطابقة</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>
      <!-- bottom padding -->
      <div style="height:24px"></div>

      <!-- ── CLOSE SHIFT MODAL ───────────────────── -->
      <Teleport to="body">
        <div v-if="showCloseShiftModal" class="ss-modal-overlay" @click="closeModal">
          <div class="ss-modal" @click.stop>
            <div class="ss-modal__header">
              <h2 class="ss-modal__title">إغلاق الوردية</h2>
              <button class="ss-modal__close" @click="closeModal">✕</button>
            </div>
            <div class="ss-modal__body">
              <div class="ss-field">
                <label class="ss-label">النقد الفعلي في الدرج</label>
                <input type="number" v-model.number="closeShiftData.closing_cash" class="ss-input" placeholder="0.00" step="0.01" min="0" />
                <small class="ss-hint">المتوقع: {{ formatCurrency(expectedCash, currencyCode, locale) }}</small>
              </div>
              <div v-if="modalDifference !== 0" class="ss-diff-alert" :class="modalDifference > 0 ? 'ss-diff-alert--surplus' : 'ss-diff-alert--deficit'">
                <strong>{{ modalDifference > 0 ? '⬆ فائض' : '⬇ عجز' }}</strong>
                <span>{{ formatCurrency(Math.abs(modalDifference), currencyCode, locale) }}</span>
              </div>
              <div v-else-if="closeShiftData.closing_cash > 0" class="ss-diff-alert ss-diff-alert--balanced">
                <strong>✓ متوازن تماماً</strong>
              </div>
              <div class="ss-field">
                <label class="ss-label">ملاحظات الإغلاق (اختياري)</label>
                <textarea v-model="closeShiftData.closing_notes" class="ss-textarea" rows="3" placeholder="أي ملاحظات..."></textarea>
              </div>
            </div>
            <div class="ss-modal__footer">
              <button class="ss-btn ss-btn--ghost" @click="closeModal">إلغاء</button>
              <button class="ss-btn ss-btn--danger" :disabled="closingShift" @click="confirmCloseShift">
                {{ closingShift ? 'جاري الإغلاق...' : 'تأكيد الإغلاق' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

    </div>

    <!-- NO DATA -->
    <div v-else class="ss-loader">
      <span class="ss-loader__text">لا توجد بيانات للوردية</span>
    </div>


</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import StatsCard from '@/layout/StatsCard.vue'
import { getShiftDetails } from '../../composables/shift'
import { formatCurrency } from '@/utils/formatters'
import { useSettingsStore } from "@/stores/settings"

const settingsStore = useSettingsStore()
const currencyCode = settingsStore?.settings?.store?.currencyCode || "PKR"
const locale       = settingsStore?.settings?.store?.locale || "en-PK"

const route  = useRoute()
const router = useRouter()

// ─── State ──────────────────────────────────────────
const shift               = ref(null)
const loading             = ref(false)
const closingShift        = ref(false)
const showCloseShiftModal = ref(false)
const closeShiftData      = ref({ closing_cash: 0, closing_notes: '' })
const activeTab           = ref('invoices')

// Invoices table
const invoiceSearch        = ref('')
const invoiceStatusFilter  = ref('')
const invoicePaymentFilter = ref('')
const invoiceSortBy        = ref('date_desc')
const invoicePage          = ref(1)
const INVOICE_PAGE_SIZE    = 15

// Transactions table
const txSearch        = ref('')
const txTypeFilter    = ref('')
const txPaymentFilter = ref('')

// Payments table
const pmSearch = ref('')

// ─── Helpers ─────────────────────────────────────────
const flt = (v) => parseFloat(v) || 0

const formatDate = (d) => {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString('ar-EG', { day: '2-digit', month: '2-digit', year: 'numeric' }) }
  catch { return d }
}
const formatTime = (t) => {
  if (!t) return ''
  try { return String(t).substring(0, 5) } catch { return '' }
}
const initials = (name) => {
  if (!name) return '؟'
  return name.split(/[\s@._-]/).map(p => p[0]).filter(Boolean).join('').substring(0, 2).toUpperCase()
}

// ─── Core computed ────────────────────────────────────
const invoices     = computed(() => shift.value?.invoices     || [])
const transactions = computed(() => shift.value?.transactions || [])
const payments     = computed(() => shift.value?.payments     || [])

const salesInvoicesCount = computed(() => invoices.value.filter(i => flt(i.grand_total) >= 0).length)
const returnInvoicesCount= computed(() => invoices.value.filter(i => flt(i.grand_total) < 0).length)
const totalReturns       = computed(() => invoices.value.filter(i => flt(i.grand_total) < 0).reduce((s, i) => s + Math.abs(flt(i.grand_total)), 0))
const totalQty           = computed(() => invoices.value.reduce((s, i) => s + flt(i.total_qty), 0))
const avgInvoice         = computed(() => {
  const sales = invoices.value.filter(i => flt(i.grand_total) > 0)
  return sales.length ? sales.reduce((s, i) => s + flt(i.grand_total), 0) / sales.length : 0
})

const expectedCash   = computed(() => flt(shift.value?.opening_cash) + flt(shift.value?.total_cash_collected))
const cashDifference = computed(() => {
  if (!shift.value || shift.value.status !== 'closed') return 0
  return flt(shift.value.closing_cash) - expectedCash.value
})
const modalDifference = computed(() => flt(closeShiftData.value.closing_cash) - expectedCash.value)

// ─── Payment breakdown ────────────────────────────────
  const COLORS = ['#3b82f6','#10b981','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#f97316']
  const paymentBreakdown = computed(() => {
    const list  = payments.value.filter(p => flt(p.expected_amount) > 0)
    const total = list.reduce((s, p) => s + flt(p.expected_amount), 0) || 1
    return list.map((p, i) => ({
      ...p,
      pct:   Math.round(flt(p.expected_amount) / total * 100),
      color: COLORS[i % COLORS.length]
    }))
  })

// ─── Hourly sales ──────────────────────────────────────
const hourlySales = computed(() => {
  const map = {}
  invoices.value.forEach(inv => {
    if (!inv.posting_time) return
    const h = parseInt(String(inv.posting_time).split(':')[0]) || 0
    map[h] = (map[h] || 0) + flt(inv.grand_total)
  })
  const hours = Object.entries(map).filter(([, v]) => v > 0).map(([h, v]) => ({ hour: +h, total: v })).sort((a,b)=>a.hour-b.hour)
  const max   = Math.max(...hours.map(h => h.total)) || 1
  return hours.map(h => ({ ...h, pct: Math.round(h.total / max * 100) }))
})

// ─── Staff performance ────────────────────────────────
const staffPerformance = computed(() => {
  return (shift.value?.staff_performance || [])
    .map(s => ({
      owner:    s.user_id,
      fullName: s.name,
      count:    s.invoices_count,
      total:    s.total_sales,
    }))
    .sort((a, b) => b.total - a.total)
})

// ─── Unique payment methods ────────────────────────────
// const uniquePaymentMethods = computed(() => {
//   const set = new Set()
//   invoices.value.forEach(inv => {
//     if (inv.payment_method) set.add(inv.payment_method)
//     ;(inv.payments || []).forEach(p => p.mode_of_payment && set.add(p.mode_of_payment))
//   })
//   payments.value.forEach(p => p.mode_of_payment && set.add(p.mode_of_payment))
//   return [...set]
// })
const uniquePaymentMethods = computed(() => {
  const set = new Set()
  invoices.value.forEach(inv => {
    if (inv.payment_method) set.add(inv.payment_method)
    ;(inv.all_payments || inv.payments || []).forEach(p => {
      p.mode_of_payment && set.add(p.mode_of_payment)
    })
  })
  payments.value.forEach(p => p.mode_of_payment && set.add(p.mode_of_payment))
  return [...set]
})
// ─── Tabs ─────────────────────────────────────────────
const tabs = computed(() => [
  { key: 'invoices',     label: 'الفواتير',           count: invoices.value.length },
  { key: 'transactions', label: 'المعاملات النقدية',   count: transactions.value.length },
  { key: 'payments',     label: 'مقارنة الدفع',       count: payments.value.length },
  { key:   'issues',     label: 'مشاكل التسوية',      count: shift.value?.reconciliation_issues?.length || 0,
    alert: shift.value?.has_issues   // لتلوين الـ tab باللون الأحمر
  },
])

// ─── Invoice helpers ──────────────────────────────────
const getInvoicePrimaryPayment = (inv) => inv.payments?.[0]?.mode_of_payment || '—'

const getStatusLabel = (inv) => {
  if (flt(inv.grand_total) < 0) return 'واپسی'
  const s = (inv.status || '').toLowerCase()
  return ({ paid: 'ادا شدہ',unpaid: 'غیر ادا شدہ', 'partly paid': 'جزوی ادائیگی', return: 'واپسی', draft: 'مسودہ', cancelled: 'منسوخ', 'credit note issued': 'کریڈٹ نوٹ' })[s] || inv.status || '—'
}
const getStatusClass = (inv) => {
  if (flt(inv.grand_total) < 0) return 'ss-chip--warning'
  const s = (inv.status || '').toLowerCase()
  return ({ paid: 'ss-chip--success',unpaid: 'ss-chip--muted', 'partly paid': 'ss-chip--info', return: 'ss-chip--warning', draft: 'ss-chip--muted', cancelled: 'ss-chip--danger', 'credit note issued': 'ss-chip--info' })[s] || 'ss-chip--info'
}

// ─── Invoice table filtering / sorting / pagination ───
const filteredInvoices = computed(() => {
  let list = [...invoices.value]
  const q = invoiceSearch.value.trim().toLowerCase()
  if (q) list = list.filter(i =>
    (i.name || '').toLowerCase().includes(q) ||
    (i.customer || '').toLowerCase().includes(q) ||
    (i.owner || '').toLowerCase().includes(q)
  )
  if (invoiceStatusFilter.value) {
    list = list.filter(i => {
      if (invoiceStatusFilter.value === 'Return') return flt(i.grand_total) < 0
      return (i.status || '').toLowerCase() === invoiceStatusFilter.value.toLowerCase()
    })
  }
  if (invoicePaymentFilter.value) {
  list = list.filter(i =>
    i.payment_method === invoicePaymentFilter.value ||
    (i.all_payments || i.payments || []).some(
      p => p.mode_of_payment === invoicePaymentFilter.value
    )
  )
}
  // if (invoicePaymentFilter.value) {
  //   list = list.filter(i =>
  //     i.payment_method === invoicePaymentFilter.value ||
  //     (i.payments || []).some(p => p.mode_of_payment === invoicePaymentFilter.value)
  //   )
  // }
  const [field, dir] = invoiceSortBy.value.split('_')
  list.sort((a, b) => {
    const av = field === 'total' ? flt(a.grand_total) : (String(a.posting_date || '') + String(a.posting_time || ''))
    const bv = field === 'total' ? flt(b.grand_total) : (String(b.posting_date || '') + String(b.posting_time || ''))
    return dir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1)
  })
  return list
})

const filteredInvoicesTotal = computed(() => filteredInvoices.value.reduce((s, i) => s + flt(i.grand_total), 0))
const filteredInvoicesQty   = computed(() => filteredInvoices.value.reduce((s, i) => s + flt(i.total_qty), 0))
const invoiceTotalPages     = computed(() => Math.max(1, Math.ceil(filteredInvoices.value.length / INVOICE_PAGE_SIZE)))
const invoicePageOffset     = computed(() => (invoicePage.value - 1) * INVOICE_PAGE_SIZE)
const paginatedInvoices     = computed(() => filteredInvoices.value.slice(invoicePageOffset.value, invoicePageOffset.value + INVOICE_PAGE_SIZE))

const setSortInvoice = (field) => {
  const map = { name: 'date', posting_date: 'date', grand_total: 'total' }
  const f   = map[field] || field
  const [cur, dir] = invoiceSortBy.value.split('_')
  invoiceSortBy.value = cur === f ? `${f}_${dir === 'asc' ? 'desc' : 'asc'}` : `${f}_desc`
  invoicePage.value = 1
}

// ─── Transaction table ────────────────────────────────
const filteredTransactions = computed(() => {
  let list = [...transactions.value]
  const q = txSearch.value.trim().toLowerCase()
  if (q) list = list.filter(t =>
    (t.description || '').toLowerCase().includes(q) ||
    (t.user_name || '').toLowerCase().includes(q) ||
    (t.mode_of_payment || '').toLowerCase().includes(q)
  )
  if (txTypeFilter.value)    list = list.filter(t => t.type === txTypeFilter.value)
  if (txPaymentFilter.value) list = list.filter(t => t.mode_of_payment === txPaymentFilter.value)
  return list
})
const txTotalIn  = computed(() => filteredTransactions.value.filter(t => t.type === 'in').reduce((s, t) => s + flt(t.amount), 0))
const txTotalOut = computed(() => filteredTransactions.value.filter(t => t.type === 'out').reduce((s, t) => s + flt(t.amount), 0))
const txNet      = computed(() => txTotalIn.value - txTotalOut.value)

// ─── Payments table ───────────────────────────────────
const filteredPayments = computed(() => {
  const q = pmSearch.value.trim().toLowerCase()
  return q ? payments.value.filter(p => (p.mode_of_payment || '').toLowerCase().includes(q)) : payments.value
})
const pmDiffPct = (pm) => {
  const exp = flt(pm.expected_amount)
  return exp ? Math.round(((pm.difference || 0) / exp) * 100) : 0
}

// ─── Actions ──────────────────────────────────────────
const loadShiftData = async (id) => {
  try {
    loading.value = true
    shift.value = await getShiftDetails(id)
    console.log("shift.value",shift.value)
  } catch (e) {
    console.error('Failed to load shift:', e)
  } finally {
    loading.value = false
  }
}

const goBack       = () => router.push('/shifts')
const viewInvoice  = (name) => router.push(`/invoices/${name}`)
const printInvoice = (id) => console.log('Print invoice:', id)
const printShiftReport = () => window.print()
const exportInvoices   = () => console.log('Export invoices')

const closeModal = () => {
  showCloseShiftModal.value = false
  closeShiftData.value = { closing_cash: 0, closing_notes: '' }
}
const confirmCloseShift = async () => {
  if (closingShift.value) return
  try {
    closingShift.value = true
    // TODO: await closeShiftAPI(shift.value.id, closeShiftData.value)
    shift.value.status         = 'closed'
    shift.value.closing_cash   = closeShiftData.value.closing_cash
    shift.value.closing_notes  = closeShiftData.value.closing_notes
    shift.value.closed_at      = new Date().toISOString()
    shift.value.closed_by_name = 'Current User'
    closeModal()
  } catch (e) {
    console.error('Failed to close shift:', e)
  } finally {
    closingShift.value = false
  }
}

const getUniquePayments = (inv) => {
  const all = inv.all_payments || inv.payments || []
  const seen = new Set()
  return all.filter(p => {
    const key = `${p.mode_of_payment}-${p.source}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}
onMounted(() => loadShiftData(route.params.id))
</script>

<style scoped>
/* ══════════════════════════════════════
   CSS TOKENS
══════════════════════════════════════ */
.ss-root {
  --ss-green:  #10b981;
  --ss-blue:   #3b82f6;
  --ss-purple: #8b5cf6;
  --ss-cyan:   #06b6d4;
  --ss-orange: #f97316;
  --ss-red:    #ef4444;
  --ss-yellow: #f59e0b;
}

/* ══════════════════════════════════════
   LOADER
══════════════════════════════════════ */
.ss-loader { display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:60px 0; }
.ss-loader__ring { width:32px;height:32px;border-radius:50%;border:3px solid var(--card-border);border-top-color:var(--focus-ring);animation:ss-spin .7s linear infinite; }
.ss-loader__text { font-size:13px;color:var(--text-muted); }
@keyframes ss-spin { to{transform:rotate(360deg)} }

/* ══════════════════════════════════════
   ROOT
══════════════════════════════════════ */
.ss-root { display:flex;flex-direction:column;gap:0;direction:rtl; }

/* ══════════════════════════════════════
   HEADER
══════════════════════════════════════ */
.ss-header { display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;padding:10px 12px;margin:8px 8px 0;border-radius:10px;background:var(--card-bg);border:1px solid var(--card-border);position:sticky;top:0;z-index:20; }
.ss-header__left { display:flex;align-items:center;gap:10px;flex-wrap:wrap; }
.ss-header__title-group { display:flex;align-items:center;gap:8px; }
.ss-header__title { font-size:15px;font-weight:700;color:var(--text-main);margin:0; }
.ss-header__meta { font-size:11px;color:var(--text-muted);display:flex;align-items:center;gap:4px; }
.ss-sep { opacity:.4; }
.ss-header__actions { display:flex;align-items:center;gap:6px; }

/* ══════════════════════════════════════
   BADGE
══════════════════════════════════════ */
.ss-badge { display:inline-flex;align-items:center;gap:5px;padding:2px 10px;border-radius:999px;font-size:11px;font-weight:600; }
.ss-badge__dot { width:6px;height:6px;border-radius:50%; }
.ss-badge--open { background:var(--icon-bg-green);color:var(--icon-color-green); }
.ss-badge--open .ss-badge__dot { background:var(--icon-color-green);animation:ss-pulse 1.8s infinite; }
.ss-badge--closed { background:var(--warning-bg);color:var(--warning-border); }
.ss-badge--closed .ss-badge__dot { background:var(--warning-border); }
@keyframes ss-pulse { 0%,100%{opacity:1}50%{opacity:.4} }

/* ══════════════════════════════════════
   BUTTONS
══════════════════════════════════════ */
.ss-btn { display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;border:none;transition:opacity .15s,transform .1s; }
.ss-btn:active { transform:scale(.97); }
.ss-btn--ghost { background:var(--item-bg);color:var(--text-main);border:1px solid var(--card-border); }
.ss-btn--ghost:hover { background:var(--nav-item-hover-bg); }
.ss-btn--danger { background:#ef4444;color:#fff; }
.ss-btn--danger:hover { background:#dc2626; }
.ss-btn--sm { padding:4px 10px;font-size:11px; }
.ss-btn:disabled { opacity:.5;cursor:not-allowed; }
.ss-back-btn { display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:6px;border:none;background:transparent;color:var(--text-muted);font-size:12px;cursor:pointer;transition:all .15s; }
.ss-back-btn:hover { background:var(--nav-item-hover-bg);color:var(--text-main); }

/* ══════════════════════════════════════
   KPI STRIP
══════════════════════════════════════ */
.ss-kpi-strip { display:flex;flex-wrap:wrap;gap:8px;padding:8px 8px 0; }
.ss-kpi { flex:1 1 150px;display:flex;align-items:center;gap:10px;padding:12px 14px;border-radius:10px;background:var(--card-bg);border:1px solid var(--card-border);transition:transform .15s,box-shadow .15s; }
.ss-kpi:hover { transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.08); }
.ss-kpi--primary { border-color:rgba(16,185,129,.3); }
.ss-kpi__icon { width:36px;height:36px;border-radius:9px;display:flex;align-items:center;justify-content:center;flex-shrink:0; }
.ss-kpi__icon--green  { background:rgba(16,185,129,.12);color:#10b981; }
.ss-kpi__icon--blue   { background:rgba(59,130,246,.12);color:#3b82f6; }
.ss-kpi__icon--purple { background:rgba(139,92,246,.12);color:#8b5cf6; }
.ss-kpi__icon--cyan   { background:rgba(6,182,212,.12);color:#06b6d4; }
.ss-kpi__icon--orange { background:rgba(249,115,22,.12);color:#f97316; }
.ss-kpi__icon--red    { background:rgba(239,68,68,.12);color:#ef4444; }
.ss-kpi__body { display:flex;flex-direction:column;gap:1px;min-width:0; }
.ss-kpi__label { font-size:10px;color:var(--text-muted);font-weight:500;white-space:nowrap; }
.ss-kpi__value { font-size:15px;font-weight:700;color:var(--text-main);white-space:nowrap; }
.ss-kpi__value--red   { color:#ef4444; }
.ss-kpi__value--green { color:#10b981; }
.ss-kpi__sub { font-size:10px;color:var(--text-muted); }

/* ══════════════════════════════════════
   ANALYTICS ROW
══════════════════════════════════════ */
.ss-analytics-row { display:grid;grid-template-columns:1.5fr 1fr 1.5fr;gap:8px;padding:8px 8px 0; }
@media(max-width:900px){ .ss-analytics-row{grid-template-columns:1fr 1fr} .ss-analytics-staff{grid-column:1/-1} }
@media(max-width:600px){ .ss-analytics-row{grid-template-columns:1fr} }

/* ══════════════════════════════════════
   CARD
══════════════════════════════════════ */
.ss-card { background:var(--card-bg);border:1px solid var(--card-border);border-radius:10px;overflow:hidden; }
.ss-card__header { padding:10px 14px 0; }
.ss-card__title { font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin:0 0 8px; }

/* ══════════════════════════════════════
   PAYMENT BARS
══════════════════════════════════════ */
.ss-payment-bars { padding:0 14px 14px;display:flex;flex-direction:column;gap:10px; }
.ss-payment-bar-item__top { display:flex;justify-content:space-between;margin-bottom:3px; }
.ss-payment-bar-item__name { font-size:11px;color:var(--text-sub);font-weight:500; }
.ss-payment-bar-item__val  { font-size:11px;color:var(--text-main);font-weight:700; }
.ss-payment-bar-item__track { height:6px;border-radius:3px;background:var(--item-bg);overflow:hidden; }
.ss-payment-bar-item__fill { height:100%;border-radius:3px;transition:width .6s cubic-bezier(.4,0,.2,1); }
.ss-payment-bar-item__pct { font-size:10px;color:var(--text-muted);text-align:left;margin-top:1px; }

/* ══════════════════════════════════════
   HOURLY CHART
══════════════════════════════════════ */
.ss-hourly-chart { padding:0 14px 14px;display:flex;align-items:flex-end;gap:3px;height:90px; }
.ss-hourly-bar { flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:3px;height:100%;cursor:default; }
.ss-hourly-bar__fill { width:100%;border-radius:3px 3px 0 0;background:var(--focus-ring);opacity:.65;transition:height .5s ease;min-height:3px; }
.ss-hourly-bar:hover .ss-hourly-bar__fill { opacity:1; }
.ss-hourly-bar__label { font-size:9px;color:var(--text-muted); }

/* ══════════════════════════════════════
   STAFF LIST
══════════════════════════════════════ */
.ss-staff-list { padding:0 14px 14px;display:flex;flex-direction:column;gap:8px; }
.ss-staff-item { display:grid;align-items:center;grid-template-columns:20px 30px 1fr auto;gap:8px; }
.ss-staff-item__rank   { font-size:10px;font-weight:700;color:var(--text-muted);text-align:center; }
.ss-staff-item__avatar { width:28px;height:28px;border-radius:50%;background:var(--info-bg);color:var(--focus-ring);font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;border:1px solid var(--info-border); }
.ss-staff-item__info   { display:flex;flex-direction:column;gap:1px;min-width:0; }
.ss-staff-item__name   { font-size:11px;font-weight:600;color:var(--text-main);overflow:hidden;white-space:nowrap;text-overflow:ellipsis; }
.ss-staff-item__sub    { font-size:10px;color:var(--text-muted); }
.ss-staff-item__sales  { font-size:12px;font-weight:700;color:var(--focus-ring);white-space:nowrap; }

/* ══════════════════════════════════════
   TABS
══════════════════════════════════════ */
.ss-tabs-section { padding:8px 8px 0; }
.ss-tabs { display:flex;gap:2px;background:var(--card-bg);border:1px solid var(--card-border);border-radius:10px;padding:4px; }
.ss-tab { flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:6px 12px;border-radius:7px;border:none;font-size:12px;font-weight:600;color:var(--text-muted);cursor:pointer;background:transparent;transition:all .2s;white-space:nowrap; }
.ss-tab:hover { color:var(--text-main);background:var(--item-bg); }
.ss-tab--active { background:var(--focus-ring) !important;color:#fff !important; }
.ss-tab__badge { font-size:10px;font-weight:700;padding:1px 6px;border-radius:99px;min-width:18px;text-align:center;background:var(--item-bg);color:var(--text-muted); }
.ss-tab--active .ss-tab__badge { background:rgba(255,255,255,.25);color:#fff; }

/* ══════════════════════════════════════
   TABLE SECTION
══════════════════════════════════════ */
.ss-table-section { padding:8px 8px 0; }
.ss-table-toolbar { display:flex;align-items:center;flex-wrap:wrap;gap:8px;padding:10px 12px;border-bottom:1px solid var(--card-border); }
.ss-search { display:flex;align-items:center;gap:6px;background:var(--input-bg);border:1px solid var(--input-border);border-radius:7px;padding:5px 10px;flex:1;min-width:160px; }
.ss-search__input { border:none;background:transparent;outline:none;font-size:12px;color:var(--text-main);width:100%; }
.ss-search__input::placeholder { color:var(--text-muted); }
.ss-search__clear { background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:11px;padding:0 2px; }
.ss-filters { display:flex;gap:6px;flex-wrap:wrap; }
.ss-select { background:var(--input-bg);border:1px solid var(--input-border);border-radius:7px;padding:5px 8px;font-size:11px;color:var(--text-main);outline:none;cursor:pointer; }
.ss-table-meta { display:flex;align-items:center;gap:8px;margin-right:auto; }
.ss-table-meta__count { font-size:11px;color:var(--text-muted);font-weight:600; }
.ss-table-meta__count--green { color:#10b981; }
.ss-table-meta__count--red   { color:#ef4444; }

.ss-table-wrap { overflow-x:auto; }
.ss-table { width:100%;border-collapse:collapse;font-size:12px; }
.ss-table thead th { padding:8px 12px;text-align:right;font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.03em;background:var(--item-bg);border-bottom:1px solid var(--card-border);white-space:nowrap; }
.ss-th-sort { cursor:pointer;user-select:none; }
.ss-th-sort:hover { color:var(--text-main); }
.ss-table tbody td { padding:8px 12px;color:var(--text-main);border-bottom:1px solid var(--card-border);vertical-align:middle; }
.ss-tr { transition:background .1s; }
.ss-tr:hover td { background:var(--nav-item-hover-bg); }
.ss-tr--return td { background:rgba(239,68,68,.03); }
.ss-tr--return:hover td { background:rgba(239,68,68,.06); }
.ss-tr--out td { background:rgba(239,68,68,.02); }
.ss-td-num    { color:var(--text-muted)!important;font-size:11px;width:32px;text-align:center; }
.ss-td-muted  { color:var(--text-muted)!important; }
.ss-td-amount { font-weight:700; }
.ss-td-amount--neg { color:#ef4444!important; }
.ss-td-amount--pos { color:#10b981!important; }
.ss-tfoot td   { padding:8px 12px;font-weight:700;font-size:12px;background:var(--item-bg)!important;color:var(--text-main)!important; }
.ss-tfoot__label { color:var(--text-muted)!important;text-transform:uppercase;font-size:11px;letter-spacing:.03em; }
.ss-empty-row  { text-align:center;color:var(--text-muted);padding:24px!important;font-size:12px; }
.ss-empty      { font-size:12px;color:var(--text-muted);text-align:center;padding:12px 0; }

/* ══════════════════════════════════════
   CHIPS
══════════════════════════════════════ */
.ss-chip         { display:inline-block;padding:2px 8px;border-radius:99px;font-size:10px;font-weight:600;white-space:nowrap; }
.ss-chip--info   { background:var(--info-bg);color:var(--focus-ring);border:1px solid var(--info-border); }
.ss-chip--success{ background:var(--icon-bg-green);color:var(--icon-color-green); }
.ss-chip--warning{ background:var(--warning-bg);color:var(--warning-border); }
.ss-chip--danger { background:rgba(239,68,68,.1);color:#ef4444; }
.ss-chip--muted  { background:var(--item-bg);color:var(--text-muted);border:1px solid var(--card-border); }

/* ══════════════════════════════════════
   TX TYPE
══════════════════════════════════════ */
.ss-tx-type      { display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:99px;font-size:10px;font-weight:700; }
.ss-tx-type--in  { background:rgba(16,185,129,.1);color:#10b981; }
.ss-tx-type--out { background:rgba(239,68,68,.1);color:#ef4444; }

/* ══════════════════════════════════════
   DIFF BAR
══════════════════════════════════════ */
.ss-diff-bar      { display:inline-block;width:60px;height:5px;background:var(--item-bg);border-radius:3px;overflow:hidden;vertical-align:middle; }
.ss-diff-bar__fill{ height:100%;border-radius:3px; }
.ss-diff-pct      { font-size:10px;color:var(--text-muted); }

/* ══════════════════════════════════════
   LINKS & ICON BTNS
══════════════════════════════════════ */
.ss-link { background:none;border:none;cursor:pointer;padding:0;color:var(--focus-ring);font-weight:600;font-size:12px; }
.ss-link:hover { text-decoration:underline; }
.ss-row-actions   { display:flex;gap:3px; }
.ss-icon-btn      { width:24px;height:24px;border-radius:5px;border:none;display:flex;align-items:center;justify-content:center;cursor:pointer;background:transparent;color:var(--focus-ring);transition:background .12s; }
.ss-icon-btn:hover { background:var(--info-bg); }
.ss-icon-btn--green { color:var(--icon-color-green); }
.ss-icon-btn--green:hover { background:var(--icon-bg-green); }

/* ══════════════════════════════════════
   PAGINATION
══════════════════════════════════════ */
.ss-pagination { display:flex;justify-content:center;align-items:center;gap:3px;padding:10px;border-top:1px solid var(--card-border); }
.ss-page-btn { width:28px;height:28px;border-radius:6px;border:1px solid var(--card-border);background:var(--item-bg);color:var(--text-muted);cursor:pointer;font-size:12px;font-weight:600;display:flex;align-items:center;justify-content:center;transition:all .15s; }
.ss-page-btn:hover:not(:disabled) { background:var(--focus-ring);color:#fff;border-color:var(--focus-ring); }
.ss-page-btn--active { background:var(--focus-ring)!important;color:#fff!important;border-color:var(--focus-ring)!important; }
.ss-page-btn:disabled { opacity:.3;cursor:not-allowed; }

/* ══════════════════════════════════════
   MODAL
══════════════════════════════════════ */
.ss-modal-overlay { position:fixed;inset:0;z-index:100;background:rgba(0,0,0,.55);backdrop-filter:blur(2px);display:flex;align-items:center;justify-content:center;padding:16px; }
.ss-modal { width:100%;max-width:440px;border-radius:14px;overflow:hidden;background:var(--card-bg);border:1px solid var(--card-border);box-shadow:0 24px 60px rgba(0,0,0,.25);animation:ss-modal-in .2s cubic-bezier(.4,0,.2,1); }
@keyframes ss-modal-in { from{opacity:0;transform:translateY(16px) scale(.97)} to{opacity:1;transform:none} }
.ss-modal__header { display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid var(--card-border); }
.ss-modal__title  { font-size:15px;font-weight:700;color:var(--text-main);margin:0; }
.ss-modal__close  { width:28px;height:28px;border-radius:6px;border:none;background:transparent;color:var(--text-muted);cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center; }
.ss-modal__close:hover { background:var(--item-bg); }
.ss-modal__body   { padding:16px 18px;display:flex;flex-direction:column;gap:14px; }
.ss-modal__footer { display:flex;gap:8px;padding:12px 18px;border-top:1px solid var(--card-border); }
.ss-modal__footer .ss-btn { flex:1;justify-content:center;padding:8px; }

/* ══════════════════════════════════════
   FORM
══════════════════════════════════════ */
.ss-field    { display:flex;flex-direction:column;gap:4px; }
.ss-label    { font-size:11px;font-weight:600;color:var(--text-sub); }
.ss-hint     { font-size:11px;color:var(--text-muted); }
.ss-input,.ss-textarea { background:var(--input-bg);border:1px solid var(--input-border);border-radius:8px;padding:8px 12px;font-size:13px;color:var(--text-main);outline:none;width:100%;box-sizing:border-box;transition:border-color .15s; }
.ss-input:focus,.ss-textarea:focus { border-color:var(--focus-ring); }
.ss-textarea { resize:vertical;font-family:inherit; }

/* ══════════════════════════════════════
   DIFF ALERT
══════════════════════════════════════ */
.ss-diff-alert          { display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border-radius:8px;font-size:12px; }
.ss-diff-alert--surplus { background:rgba(16,185,129,.1);color:#10b981;border:1px solid rgba(16,185,129,.2); }
.ss-diff-alert--deficit { background:rgba(239,68,68,.1);color:#ef4444;border:1px solid rgba(239,68,68,.2); }
.ss-diff-alert--balanced{ background:rgba(16,185,129,.08);color:#10b981;border:1px solid rgba(16,185,129,.15); }

/* ══════════════════════════════════════
   PRINT
══════════════════════════════════════ */
@media print {
  .ss-header__actions,.ss-tabs-section,.ss-btn { display:none!important; }
  .ss-table-section { display:block!important; }
}
</style>
