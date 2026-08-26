class DashboardApp {
    constructor() {
        this.cacheDOM();
        this.checkAuth();
        this.bindEvents();
        
        // Initial Load
        this.loadBalance();
        this.loadPayments();
    }

    cacheDOM() {
        this.dom = {
            logoutBtn: document.getElementById('logout-btn'),
            merchantNameEl: document.getElementById('merchant-name'),
            availableEl: document.getElementById('available-balance'),
            pendingEl: document.getElementById('pending-balance'),
            countEl: document.getElementById('payment-count'),
            tbody: document.getElementById('payments-tbody'),
            tableEmpty: document.getElementById('table-empty'),
            tableLoading: document.getElementById('table-loading'),
            resultsCount: document.getElementById('results-count'),
            prevPageBtn: document.getElementById('prev-page'),
            nextPageBtn: document.getElementById('next-page'),
            pageInfo: document.getElementById('page-info'),
            successRateEl: document.getElementById('success-rate'),
            webhookRateEl: document.getElementById('webhook-rate'),
            volumeChartEl: document.getElementById('volume-chart-container'),
            volumeLabelsEl: document.getElementById('volume-chart-labels'),
            exportBtn: document.getElementById('export-csv-btn'),
            exportModal: document.getElementById('export-modal'),
            closeExportModalBtn: document.getElementById('close-export-modal-btn'),
            exportStartDate: document.getElementById('export-start-date'),
            exportEndDate: document.getElementById('export-end-date'),
            confirmExportBtn: document.getElementById('confirm-export-btn'),
        };
    }

    checkAuth() {
        if (!SwiftPayAPI.getToken()) {
            window.location.href = 'landingpage.html';
        }
    }

    bindEvents() {
        if (this.dom.logoutBtn) {
            this.dom.logoutBtn.addEventListener('click', () => {
                SwiftPayAPI.clearToken();
                window.location.href = 'landingpage.html';
            });
        }

        const applyFilters = () => {
            DashboardState.updateFilters({
                status: this.dom.filterStatus ? this.dom.filterStatus.value : '',
                min_amount: this.dom.filterMinAmount ? this.dom.filterMinAmount.value : '',
                max_amount: this.dom.filterMaxAmount ? this.dom.filterMaxAmount.value : '',
                start_date: this.dom.filterStartDate ? this.dom.filterStartDate.value : '',
                end_date: this.dom.filterEndDate ? this.dom.filterEndDate.value : ''
            });
            this.loadPayments();
        };

        if (this.dom.filterStatus) this.dom.filterStatus.addEventListener('change', applyFilters);
        if (this.dom.filterMinAmount) this.dom.filterMinAmount.addEventListener('change', applyFilters);
        if (this.dom.filterMaxAmount) this.dom.filterMaxAmount.addEventListener('change', applyFilters);
        if (this.dom.filterStartDate) this.dom.filterStartDate.addEventListener('change', applyFilters);
        if (this.dom.filterEndDate) this.dom.filterEndDate.addEventListener('change', applyFilters);

        if (this.dom.sortAmountBtn) {
            this.dom.sortAmountBtn.addEventListener('click', () => {
                const current = DashboardState.get().filters.ordering;
                DashboardState.updateFilters({ ordering: current === 'amount' ? '-amount' : 'amount' });
                this.loadPayments();
            });
        }

        if (this.dom.sortDateBtn) {
            this.dom.sortDateBtn.addEventListener('click', () => {
                const current = DashboardState.get().filters.ordering;
                DashboardState.updateFilters({ ordering: current === 'created_at' ? '-created_at' : 'created_at' });
                this.loadPayments();
            });
        }

        if (this.dom.exportBtn) {
            this.dom.exportBtn.addEventListener('click', () => {
                if (this.dom.exportModal) {
                    this.dom.exportModal.classList.remove('hidden');
                    this.dom.exportModal.classList.add('flex');
                }
            });
        }
        
        if (this.dom.closeExportModalBtn) {
            this.dom.closeExportModalBtn.addEventListener('click', () => {
                if (this.dom.exportModal) {
                    this.dom.exportModal.classList.add('hidden');
                    this.dom.exportModal.classList.remove('flex');
                }
            });
        }
        
        if (this.dom.confirmExportBtn) {
            this.dom.confirmExportBtn.addEventListener('click', () => this.exportCSV());
        }

        if (this.dom.prevPageBtn) {
            this.dom.prevPageBtn.addEventListener('click', () => {
                const state = DashboardState.get();
                if (state.currentPage > 1) {
                    DashboardState.setPage(state.currentPage - 1);
                    this.loadPayments();
                }
            });
        }
        
        if (this.dom.nextPageBtn) {
            this.dom.nextPageBtn.addEventListener('click', () => {
                const state = DashboardState.get();
                if (state.currentPage < state.numPages) {
                    DashboardState.setPage(state.currentPage + 1);
                    this.loadPayments();
                }
            });
        }

        if (this.dom.tbody) {
            this.dom.tbody.addEventListener('click', (e) => this.handleRowClick(e));
        }
    }

    // handleFilterClick removed in favor of table header filters

    handleRowClick(e) {
        const row = e.target.closest('tr[data-payment-id]');
        if (!row) return;

        const paymentId = row.dataset.paymentId;
        DashboardState.toggleRow(paymentId);
        this.renderPayments();
    }

    async loadPayments() {
        const state = DashboardState.get();
        if(this.dom.tbody) this.dom.tbody.innerHTML = '';
        if(this.dom.tableEmpty) this.dom.tableEmpty.classList.add('hidden');
        if(this.dom.tableLoading) this.dom.tableLoading.classList.remove('hidden');

        try {
            const params = { page: state.currentPage, ...state.filters };
            const qs = new URLSearchParams(Object.entries(params).filter(([_, v]) => v));
            const data = await SwiftPayAPI.request(`/payments/?${qs.toString()}`);
            DashboardState.setPayments(data);
            this.renderPayments();
        } catch (err) {
            console.error('Failed to load payments:', err);
            if(this.dom.tbody) this.dom.tbody.innerHTML = '';
            if(this.dom.tableEmpty) this.dom.tableEmpty.classList.remove('hidden');
        } finally {
            if(this.dom.tableLoading) this.dom.tableLoading.classList.add('hidden');
        }
    }

    async loadBalance() {
        try {
            const balance = await SwiftPayAPI.request('/merchants/balance/');
            DashboardState.setBalance(balance);
            this.renderBalance();
        } catch (err) {
            console.error('Failed to load balance:', err);
        }
    }

    renderBalance() {
        const state = DashboardState.get();
        if (!state.balance) return;

        const b = state.balance;
        if(this.dom.merchantNameEl) this.dom.merchantNameEl.textContent = b.merchant_name || 'Merchant';
        if(this.dom.availableEl) this.dom.availableEl.textContent = Components.formatCurrency(b.available_balance, b.currency);
        if(this.dom.pendingEl) this.dom.pendingEl.textContent = Components.formatCurrency(b.pending_balance, b.currency);
    }

    renderPayments() {
        const state = DashboardState.get();
        if(!this.dom.tbody) return;
        
        this.dom.tbody.innerHTML = '';

        if (state.payments.length === 0) {
            this.renderEmptyState();
            return;
        }

        this.updatePaginationUI(state);
        this.renderStats(state);
        
        state.payments.forEach(payment => {
            const row = Components.createPaymentRow(payment);
            this.dom.tbody.appendChild(row);

            if (state.expandedRows.has(payment.id)) {
                this.appendDetailRow(payment);
            }
        });
    }

    renderEmptyState() {
        if(this.dom.tableEmpty) this.dom.tableEmpty.classList.remove('hidden');
        if(this.dom.resultsCount) this.dom.resultsCount.textContent = '0 payments';
        if(this.dom.pageInfo) this.dom.pageInfo.textContent = 'Page 1 of 1';
        if(this.dom.prevPageBtn) this.dom.prevPageBtn.disabled = true;
        if(this.dom.nextPageBtn) this.dom.nextPageBtn.disabled = true;
        if(this.dom.successRateEl) this.dom.successRateEl.textContent = '--';
        if(this.dom.webhookRateEl) this.dom.webhookRateEl.textContent = '--';
        if(this.dom.volumeChartEl) this.dom.volumeChartEl.innerHTML = '';
        if(this.dom.volumeLabelsEl) this.dom.volumeLabelsEl.innerHTML = '';
        if(this.dom.todayEl) this.dom.todayEl.textContent = '0';
    }

    updatePaginationUI(state) {
        if(this.dom.tableEmpty) this.dom.tableEmpty.classList.add('hidden');
        if(this.dom.resultsCount) this.dom.resultsCount.textContent = `${state.totalCount} payment${state.totalCount !== 1 ? 's' : ''}`;
        if(this.dom.pageInfo) this.dom.pageInfo.textContent = `Page ${state.currentPage} of ${state.numPages}`;
        if(this.dom.prevPageBtn) this.dom.prevPageBtn.disabled = state.currentPage <= 1;
        if(this.dom.nextPageBtn) this.dom.nextPageBtn.disabled = state.currentPage >= state.numPages;
    }

    renderStats(state) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        let todayCount = 0;
        let successCount = 0;

        const dailyVolumes = {};
        for(let i=6; i>=0; i--) {
            const d = new Date(today);
            d.setDate(d.getDate() - i);
            dailyVolumes[d.toLocaleDateString('en-US', {weekday: 'short'})] = 0;
        }

        state.payments.forEach(p => {
            const pDate = new Date(p.created_at);
            if (pDate >= today) todayCount++;
            if (p.status === 'SETTLED') successCount++;
            
            const pDay = pDate.toLocaleDateString('en-US', {weekday: 'short'});
            if(dailyVolumes[pDay] !== undefined && p.status !== 'FAILED') {
                dailyVolumes[pDay] += parseFloat(p.amount);
            }
        });
        
        if(this.dom.countEl) this.dom.countEl.textContent = state.totalCount || 0;
        
        if(this.dom.successRateEl) {
            if (state.totalCount === 0) {
                this.dom.successRateEl.textContent = '--';
            } else {
                const rate = ((state.totalSuccessCount / state.totalCount) * 100).toFixed(1);
                this.dom.successRateEl.textContent = `${rate}%`;
            }
        }
        
        if(this.dom.webhookRateEl) {
            this.dom.webhookRateEl.textContent = 'Metrics Unavailable';
        }

        this.renderVolumeChart(dailyVolumes);
    }

    renderVolumeChart(dailyVolumes) {
        if(!this.dom.volumeChartEl || !this.dom.volumeLabelsEl) return;
        
        this.dom.volumeChartEl.innerHTML = '';
        this.dom.volumeLabelsEl.innerHTML = '';
        
        const maxVol = Math.max(...Object.values(dailyVolumes), 100);
        
        Object.entries(dailyVolumes).forEach(([day, vol], idx) => {
            const heightPct = Math.max((vol / maxVol) * 100, 5);
            const isToday = idx === 6;
            
            const barContainer = document.createElement('div');
            barContainer.className = 'flex-1 flex flex-col items-center gap-1 h-full justify-end group/bar';
            
            const tooltip = document.createElement('span');
            tooltip.className = `text-[10px] opacity-0 group-hover/bar:opacity-100 transition-opacity duration-200 ${isToday ? 'text-primary font-medium' : 'text-secondary'}`;
            tooltip.textContent = Components.formatCurrency(vol).replace('.00', '');
            
            const bar = document.createElement('div');
            bar.className = `w-full rounded-t-sm transition-all ${isToday ? 'bg-primary' : 'bg-primary-container/20 hover:bg-primary-container/50'}`;
            bar.style.height = `${heightPct}%`;
            
            barContainer.appendChild(tooltip);
            barContainer.appendChild(bar);
            this.dom.volumeChartEl.appendChild(barContainer);
            
            const labelSpan = document.createElement('span');
            labelSpan.textContent = day;
            if (idx !== 0 && idx !== 6) {
                labelSpan.className = 'opacity-0';
            }
            this.dom.volumeLabelsEl.appendChild(labelSpan);
        });
    }

    async appendDetailRow(payment) {
        if(!this.dom.tbody) return;
        
        const detailTr = document.createElement('tr');
        detailTr.className = 'detail-row';
        detailTr.dataset.detailFor = payment.id;
        const td = document.createElement('td');
        td.colSpan = 4;
        td.className = 'p-0';
        detailTr.appendChild(td);

        td.innerHTML = '<div class="p-8 text-center text-secondary"><div class="inline-block w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin mr-2 align-middle"></div>Loading payment details...</div>';
        
        const paymentRow = this.dom.tbody.querySelector(`tr[data-payment-id="${payment.id}"]`);
        if (paymentRow && paymentRow.nextSibling) {
            this.dom.tbody.insertBefore(detailTr, paymentRow.nextSibling);
        } else {
            this.dom.tbody.appendChild(detailTr);
        }

        const detailsNode = Components.createDetailContent(payment, []);
        if (paymentRow && paymentRow.nextSibling) {
            this.dom.tbody.insertBefore(detailsNode, detailTr);
            detailTr.remove();
        }
    }

    async exportCSV() {
        if (this.dom.confirmExportBtn) {
            this.dom.confirmExportBtn.textContent = 'Downloading...';
            this.dom.confirmExportBtn.disabled = true;
        }
        
        try {
            const startDate = this.dom.exportStartDate ? this.dom.exportStartDate.value : '';
            const endDate = this.dom.exportEndDate ? this.dom.exportEndDate.value : '';
            
            const params = { export: 'csv' };
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;
            const qs = new URLSearchParams(params).toString();
            
            const blob = await SwiftPayAPI.request(`/payments/?${qs}`, { responseType: 'blob' });
            
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `payments_export_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            
            if (this.dom.exportModal) {
                this.dom.exportModal.classList.add('hidden');
                this.dom.exportModal.classList.remove('flex');
            }
            Components.showToast('Export successful!', 'success');
        } catch (err) {
            Components.showToast(err.message, 'error');
        } finally {
            if (this.dom.confirmExportBtn) {
                this.dom.confirmExportBtn.textContent = 'Download CSV';
                this.dom.confirmExportBtn.disabled = false;
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.Dashboard = new DashboardApp();
});
