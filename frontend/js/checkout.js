document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const paymentId = urlParams.get('payment_id');

    const ui = {
        loading: document.getElementById('loading-state'),
        error: document.getElementById('error-state'),
        errorMessage: document.getElementById('error-message'),
        checkout: document.getElementById('checkout-state'),
        success: document.getElementById('success-state'),
        declined: document.getElementById('declined-state'),
        merchantName: document.getElementById('merchant-name'),
        amountDisplay: document.getElementById('amount-display'),
        paymentIdDisplay: document.getElementById('payment-id-display'),
        btnAccept: document.getElementById('btn-accept'),
        btnDecline: document.getElementById('btn-decline')
    };

    if (!paymentId) {
        showError("No payment ID provided in the URL.");
        return;
    }

    ui.paymentIdDisplay.textContent = paymentId.split('-')[0] + '...';

    // Fetch Payment Details
    fetch(`http://127.0.0.1:8001/api/v1/payments/checkout/${paymentId}/`)
        .then(res => {
            if (!res.ok) throw new Error('Payment not found or already processed.');
            return res.json();
        })
        .then(data => {
            if (data.status !== 'INITIATED') {
                throw new Error(`This payment cannot be processed (Status: ${data.status}).`);
            }
            ui.merchantName.textContent = data.merchant_name;
            
            // Format currency
            const formatter = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: data.currency || 'USD'
            });
            ui.amountDisplay.textContent = formatter.format(data.amount);
            
            showState(ui.checkout);
        })
        .catch(err => {
            showError(err.message);
        });

    // Accept & Pay Action
    ui.btnAccept.addEventListener('click', () => {
        processAction('capture', ui.btnAccept);
    });

    // Decline Action
    ui.btnDecline.addEventListener('click', () => {
        processAction('fail', ui.btnDecline);
    });

    function processAction(action, btnElement) {
        // Disable buttons
        ui.btnAccept.disabled = true;
        ui.btnDecline.disabled = true;
        const originalText = btnElement.innerHTML;
        btnElement.innerHTML = `<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-current mx-auto"></div>`;
        
        fetch(`http://127.0.0.1:8001/api/v1/payments/checkout/${paymentId}/process/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action })
        })
        .then(res => {
            if (!res.ok) throw new Error('Failed to process payment');
            return res.json();
        })
        .then(data => {
            if (action === 'capture') {
                showState(ui.success);
            } else {
                showState(ui.declined);
            }
            // Add animation classes
            setTimeout(() => {
                const activeState = action === 'capture' ? ui.success : ui.declined;
                activeState.classList.remove('scale-95', 'opacity-0');
                activeState.classList.add('scale-100', 'opacity-100');
            }, 50);
        })
        .catch(err => {
            btnElement.innerHTML = originalText;
            ui.btnAccept.disabled = false;
            ui.btnDecline.disabled = false;
            alert(err.message);
        });
    }

    function showState(activeElement) {
        [ui.loading, ui.error, ui.checkout, ui.success, ui.declined].forEach(el => {
            el.classList.add('hidden');
        });
        activeElement.classList.remove('hidden');
    }

    function showError(msg) {
        ui.errorMessage.textContent = msg;
        showState(ui.error);
    }
});
