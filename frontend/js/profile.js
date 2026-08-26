document.addEventListener('DOMContentLoaded', () => {
    const profileForm = document.getElementById('profile-form');
    
    const fieldMap = {
        'business_name': document.getElementById('business-name'),
        'trading_name': document.getElementById('trading-name'),
        'entity_type': document.getElementById('business-type'),
        'pan': document.getElementById('pan'),
        'gst': document.getElementById('gst'),
        'bank_name': document.getElementById('bank-name'),
        'account_holder_name': document.getElementById('holder-name'),
        'account_number': document.getElementById('account-number'),
        'ifsc_code': document.getElementById('ifsc'),
        'business_address': document.getElementById('address'),
        'webhook_url': document.getElementById('webhook')
    };

    // Buttons
    const saveBtn = document.getElementById('save-profile-btn');
    const generateKeyBtn = document.getElementById('generate-key-btn');
    const toggleAccountBtn = document.getElementById('toggle-account-btn');
    
    if (toggleAccountBtn && fieldMap.account_number) {
        toggleAccountBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const input = fieldMap.account_number;
            const icon = toggleAccountBtn.querySelector('span');
            if (input.type === 'password') {
                input.type = 'text';
                icon.textContent = 'visibility_off';
            } else {
                input.type = 'password';
                icon.textContent = 'visibility';
            }
        });
    }

    if (profileForm) {
        profileForm.addEventListener('submit', (e) => {
            e.preventDefault();
        });
    }
    
    // Populate form if data exists
    async function loadProfile() {
        try {
            await SwiftPayAPI.request('/merchants/balance/'); // To check auth
            const data = await SwiftPayAPI.request('/merchants/profile/');
            
            Object.entries(fieldMap).forEach(([key, element]) => {
                if (element && data[key] !== undefined && data[key] !== null) {
                    element.value = data[key];
                }
            });

            // Set Email and Phone
            const emailInput = document.getElementById('email-address');
            if (emailInput && data.email) emailInput.value = data.email;

            const phoneInput = document.getElementById('phone-number');
            const verifyPhoneBtn = document.getElementById('verify-phone-btn');
            const phoneBadge = document.getElementById('phone-status-badge');

            if (phoneInput && data.phone_number) phoneInput.value = data.phone_number;
            
            if (data.phone_verified) {
                if (phoneBadge) phoneBadge.classList.remove('hidden');
                if (verifyPhoneBtn) verifyPhoneBtn.classList.add('hidden');
                if (phoneInput) {
                    phoneInput.readOnly = true;
                    phoneInput.classList.add('cursor-not-allowed', 'bg-surface-variant');
                }
            }

            // Set API Key display
            const apiKeyDisplay = document.getElementById('api-key-display');
            if (apiKeyDisplay && data.key_id) {
                apiKeyDisplay.textContent = data.key_id;
            }

        } catch (err) {
            console.error(err);
        }
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            saveBtn.textContent = 'Saving...';
            saveBtn.disabled = true;
            try {
                const payload = {};
                Object.entries(fieldMap).forEach(([key, element]) => {
                    if (element) {
                        payload[key] = element.value || null;
                    }
                });
                
                await SwiftPayAPI.request('/merchants/profile/', {
                    method: 'PATCH',
                    body: JSON.stringify(payload)
                });
                saveBtn.textContent = 'Saved!';
                Components.showToast('Profile saved successfully', 'success');
                setTimeout(() => { saveBtn.textContent = 'Save changes'; saveBtn.disabled = false; }, 2000);
            } catch (err) {
                Components.showToast(err.message, 'error');
                saveBtn.textContent = 'Save changes';
                saveBtn.disabled = false;
            }
        });
    }

    const verifyPhoneBtn = document.getElementById('verify-phone-btn');
    const phoneOtpSection = document.getElementById('phone-otp-section');
    const phoneOtpInput = document.getElementById('phone-otp-input');
    const submitPhoneOtpBtn = document.getElementById('submit-phone-otp-btn');
    const closeOtpModalBtn = document.getElementById('close-otp-modal-btn');
    const phoneInput = document.getElementById('phone-number');

    if (verifyPhoneBtn) {
        verifyPhoneBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const phone = phoneInput.value.trim();
            if (!phone || phone.length < 10) {
                Components.showToast('Please enter a valid 10-digit phone number', 'error');
                return;
            }
            verifyPhoneBtn.textContent = 'Sending...';
            verifyPhoneBtn.disabled = true;
            try {
                await SwiftPayAPI.request('/auth/otp/send/', {
                    method: 'POST',
                    body: JSON.stringify({ phone })
                });
                phoneOtpSection.classList.remove('hidden');
                phoneOtpInput.focus();
                Components.showToast('OTP sent successfully', 'success');
            } catch (err) {
                Components.showToast(err.message, 'error');
            } finally {
                verifyPhoneBtn.textContent = 'Verify';
                verifyPhoneBtn.disabled = false;
            }
        });
    }
    
    if (closeOtpModalBtn) {
        closeOtpModalBtn.addEventListener('click', () => {
            phoneOtpSection.classList.add('hidden');
        });
    }

    if (submitPhoneOtpBtn) {
        submitPhoneOtpBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const phone = phoneInput.value.trim();
            const otp = phoneOtpInput.value.trim();
            if (!otp) {
                Components.showToast('Please enter the OTP', 'error');
                return;
            }
            submitPhoneOtpBtn.textContent = 'Confirming...';
            submitPhoneOtpBtn.disabled = true;
            try {
                await SwiftPayAPI.request('/auth/otp/verify/', {
                    method: 'POST',
                    body: JSON.stringify({ phone, otp })
                });
                Components.showToast('Phone verified successfully', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } catch (err) {
                Components.showToast(err.message, 'error');
                submitPhoneOtpBtn.textContent = 'Verify OTP';
                submitPhoneOtpBtn.disabled = false;
            }
        });
    }

    if (generateKeyBtn) {
        generateKeyBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            generateKeyBtn.textContent = 'Generating...';
            generateKeyBtn.disabled = true;
            try {
                const data = await SwiftPayAPI.request('/merchants/api-key/generate/', { method: 'POST' });
                const apiKeyDisplay = document.getElementById('api-key-display');
                if (apiKeyDisplay) {
                    apiKeyDisplay.textContent = data.key_id;
                }
                
                // Show Modal
                const modal = document.getElementById('api-key-modal');
                const modalKeyId = document.getElementById('modal-key-id');
                const modalKeySecret = document.getElementById('modal-key-secret');
                
                if (modal && modalKeyId && modalKeySecret) {
                    modalKeyId.value = data.key_id;
                    modalKeySecret.value = data.key_secret;
                    modal.classList.remove('hidden');
                }

                generateKeyBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]" data-icon="add">add</span> Generate API key';
                generateKeyBtn.disabled = false;
            } catch (err) {
                Components.showToast(err.message, 'error');
                generateKeyBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]" data-icon="add">add</span> Generate API key';
                generateKeyBtn.disabled = false;
            }
        });
    }

    // Modal Copy and Close Handlers
    const closeModalBtn = document.getElementById('close-modal-btn');
    const doneModalBtn = document.getElementById('done-modal-btn');
    const copyKeyIdBtn = document.getElementById('copy-key-id');
    const copyKeySecretBtn = document.getElementById('copy-key-secret');
    const apiKeyModal = document.getElementById('api-key-modal');

    const closeModal = () => {
        if (apiKeyModal) apiKeyModal.classList.add('hidden');
    };

    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    if (doneModalBtn) doneModalBtn.addEventListener('click', closeModal);

    const copyToClipboard = (inputId, btn) => {
        const input = document.getElementById(inputId);
        if (input) {
            navigator.clipboard.writeText(input.value).then(() => {
                const icon = btn.querySelector('span');
                icon.textContent = 'check';
                icon.classList.add('text-green-500');
                setTimeout(() => {
                    icon.textContent = 'content_copy';
                    icon.classList.remove('text-green-500');
                }, 2000);
            });
        }
    };

    if (copyKeyIdBtn) copyKeyIdBtn.addEventListener('click', () => copyToClipboard('modal-key-id', copyKeyIdBtn));
    if (copyKeySecretBtn) copyKeySecretBtn.addEventListener('click', () => copyToClipboard('modal-key-secret', copyKeySecretBtn));



    loadProfile();
});
