const DashboardState = {
    filters: {
        status: '',
        min_amount: '',
        max_amount: '',
        start_date: '',
        end_date: '',
        ordering: '-created_at'
    },
    currentPage: 1,
    payments: [],
    totalCount: 0,
    totalSuccessCount: 0,
    numPages: 1,
    expandedRows: new Set(),
    balance: null,
    merchantName: '',

    get() { return this; },
    
    updateFilters(newFilters) {
        this.filters = { ...this.filters, ...newFilters };
        this.currentPage = 1;
        this.expandedRows.clear();
    },

    setPage(page) {
        this.currentPage = page;
        this.expandedRows.clear();
    },

    setPayments(data) {
        this.payments = data.results || [];
        this.totalCount = data.count || 0;
        this.totalSuccessCount = data.total_success_count || 0;
        this.numPages = data.num_pages || 1;
        this.currentPage = data.current_page || 1;
    },

    setBalance(data) {
        this.balance = data;
        this.merchantName = data.merchant_name || '';
    },

    toggleRow(paymentId) {
        if (this.expandedRows.has(paymentId)) {
            this.expandedRows.delete(paymentId);
        } else {
            this.expandedRows.add(paymentId);
        }
    },

    isRowExpanded(paymentId) {
        return this.expandedRows.has(paymentId);
    }
};
