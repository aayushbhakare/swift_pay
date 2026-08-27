const Components = (() => {

    function formatCurrency(amount, currency = 'INR') {
        const num = parseFloat(amount);
        if (isNaN(num)) return '—';
        const locale = currency === 'INR' ? 'en-IN' : 'en-US';
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency,
        }).format(num);
    }

    function formatTime(iso) {
        if (!iso) return '—';
        const d = new Date(iso);
        const datePart = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const timePart = d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
        return `${datePart}, ${timePart}`;
    }

    function shortId(uuid) {
        if (!uuid) return '—';
        return 'tx_' + uuid.substring(0, 8);
    }

    function getStatusStyles(status) {
        const map = {
            'SETTLED': 'bg-[#dcfce7] text-[#166534]',
            'FAILED': 'bg-[#fee2e2] text-[#991b1b]',
            'CAPTURED': 'bg-[#fef9c3] text-[#854d0e]',
            'AUTHORIZED': 'bg-[#fef9c3] text-[#854d0e]',
            'INITIATED': 'bg-surface-dim/30 text-secondary',
        };
        return map[status] || 'bg-surface-dim/30 text-secondary';
    }

    function createStatusBadge(status) {
        const span = document.createElement('span');
        span.className = `${getStatusStyles(status)} px-2 py-0.5 rounded-full text-[10px] font-medium tracking-wide uppercase`;
        span.textContent = status;
        return span;
    }

    function createPaymentRow(payment) {
        const tr = document.createElement('tr');
        const isExpanded = DashboardState.isRowExpanded(payment.id);
        
        tr.className = isExpanded 
            ? 'bg-surface-container-low border-b border-outline-variant relative cursor-pointer'
            : 'border-b border-outline-variant hover:bg-surface-container-low cursor-pointer transition-colors group';
            
        tr.dataset.paymentId = payment.id;

        const idHtml = `<span class="font-code-sm text-code-sm bg-surface-dim/50 px-2 py-1 rounded text-secondary group-hover:text-on-surface transition-colors">${shortId(payment.id)}</span>`;

        tr.innerHTML = `
            <td class="p-4">${idHtml}</td>
            <td class="p-4 font-medium text-on-surface">${formatCurrency(payment.amount, payment.currency)}</td>
            <td class="p-4"></td>
            <td class="p-4 text-secondary">${formatTime(payment.created_at)}</td>
        `;
        
        tr.children[2].appendChild(createStatusBadge(payment.status));
        return tr;
    }

    const LIFECYCLE_STEPS = ['INITIATED', 'AUTHORIZED', 'CAPTURED', 'SETTLED'];

    function createTimeline(payment) {
        const container = document.createElement('div');
        container.className = 'flex items-center justify-between relative mb-8 mt-4 px-4';
        
        const isFailed = payment.status === 'FAILED';
        const currentIndex = LIFECYCLE_STEPS.indexOf(payment.status);
        const steps = isFailed ? [...LIFECYCLE_STEPS.slice(0, Math.max(currentIndex, 1)), 'FAILED'] : LIFECYCLE_STEPS;
        const iconMap = { INITIATED: '1', AUTHORIZED: '2', CAPTURED: '3', SETTLED: '4', FAILED: '!' };

        const stepsHtml = steps.map((step, i) => {
            let dotClass, labelClass = 'text-secondary';
            if (step === 'FAILED') {
                dotClass = 'bg-[#fee2e2] border-[#991b1b] text-[#991b1b]';
                labelClass = 'text-[#991b1b] font-medium';
            } else if (isFailed && i < steps.length - 1) {
                dotClass = 'bg-primary border-primary text-on-primary';
            } else {
                const stepIdx = LIFECYCLE_STEPS.indexOf(step);
                if (stepIdx < currentIndex) {
                    dotClass = 'bg-primary border-primary text-on-primary';
                } else if (stepIdx === currentIndex) {
                    dotClass = 'bg-primary-container border-primary text-on-primary-container ring-4 ring-primary-container/30';
                    labelClass = 'text-on-surface font-medium';
                } else {
                    dotClass = 'bg-surface border-outline-variant text-secondary';
                }
            }

            const icon = (dotClass.includes('bg-primary') && step !== 'FAILED' && LIFECYCLE_STEPS.indexOf(step) < currentIndex) 
                ? '<span class="material-symbols-outlined text-[14px]">check</span>' 
                : iconMap[step];

            return `
                <div class="timeline-step relative z-10 flex flex-col items-center gap-2 bg-surface-bright px-2 ${step === 'FAILED' ? 'step-failed' : ''}">
                    <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center font-label-md text-[10px] ${dotClass}">
                        ${icon}
                    </div>
                    <span class="timeline-label font-label-md text-[10px] uppercase tracking-wider ${labelClass}">${step === 'FAILED' ? 'Failed' : step}</span>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="absolute top-1/2 left-8 right-8 h-0.5 bg-outline-variant -translate-y-1/2 z-0"></div>
            ${stepsHtml}
        `;
        return container;
    }

    function createIdempotencyNotice(key) {
        if (!key) return null;
        const div = document.createElement('div');
        div.className = 'mt-4 p-3 bg-surface-container-low border border-outline-variant rounded-lg flex items-start gap-3 badge-idempotent'; // Added class for test
        div.innerHTML = `
            <span class="material-symbols-outlined text-secondary text-[20px]">lock</span>
            <p class="font-body-sm text-secondary">
                <strong class="text-on-surface font-medium">Idempotency Protected</strong> — This payment used key
                <code class="font-code-sm bg-surface-dim/50 px-1 rounded text-on-surface">${shortId(key)}</code>.
                Duplicate requests were safely ignored.
            </p>
        `;
        return div;
    }

    function createDetailContent(payment, webhookLogs) {
        const tr = document.createElement('tr');
        tr.className = 'bg-surface-container-lowest border-b border-outline-variant';
        
        const td = document.createElement('td');
        td.colSpan = 5;
        td.className = 'p-0';
        tr.appendChild(td);
        
        const div = document.createElement('div');
        div.className = 'p-gutter border-l-2 border-primary ml-4 mr-4 mb-4 bg-surface-bright rounded-r-lg mt-2 space-y-stack-lg';
        td.appendChild(div);

        // Section title
        const h3 = document.createElement('h4');
        h3.className = 'font-label-md text-secondary uppercase tracking-wider font-medium mb-4';
        h3.textContent = 'Payment Journey';
        div.appendChild(h3);
        div.appendChild(createTimeline(payment));
        const notice = createIdempotencyNotice(payment.idempotency_key);
        if (notice) div.appendChild(notice);

        return tr;
    }

    document.addEventListener('DOMContentLoaded', () => {
        const themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => {
                const isDark = document.documentElement.classList.toggle('dark');
                localStorage.setItem('theme', isDark ? 'dark' : 'light');
                const icon = themeBtn.querySelector('.material-symbols-outlined');
                if (icon) {
                    icon.textContent = isDark ? 'light_mode' : 'dark_mode';
                }
            });
        }
    });

    function showToast(message, type = 'info') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed bottom-4 right-4 flex flex-col gap-2 z-[9999]';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        const bgColors = {
            'success': 'bg-[#dcfce7] text-[#166534] border-[#bbf7d0]',
            'error': 'bg-[#fee2e2] text-[#991b1b] border-[#fecaca]',
            'info': 'bg-surface-container-low text-on-surface border-outline-variant'
        };
        const colorClass = bgColors[type] || bgColors['info'];
        
        toast.className = `px-4 py-3 rounded-lg border shadow-sm flex items-center gap-2 transform translate-y-full opacity-0 transition-all duration-300 ${colorClass}`;
        toast.innerHTML = `<span class="font-body-sm">${message}</span>`;
        
        container.appendChild(toast);
        
        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-full', 'opacity-0');
        });
        
        setTimeout(() => {
            toast.classList.add('translate-y-full', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    return {
        formatCurrency,
        formatTime,
        shortId,
        getStatusStyles,
        createStatusBadge,
        createPaymentRow,
        createTimeline,

        createIdempotencyNotice,
        createDetailContent,
        showToast,
        LIFECYCLE_STEPS,
    };
})();
