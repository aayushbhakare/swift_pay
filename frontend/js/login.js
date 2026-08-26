document.addEventListener('DOMContentLoaded', () => {
    const getStartedBtn = document.getElementById('get-started-btn');
    const loginModal = document.getElementById('login-modal');
    const closeModal = document.getElementById('close-login-modal');
    const googleLoginBtn = document.getElementById('google-login-btn');

    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', (e) => {
            e.preventDefault();
            loginModal.classList.remove('hidden');
        });
    }

    if (closeModal) {
        closeModal.addEventListener('click', () => {
            loginModal.classList.add('hidden');
        });
    }

    // Initialize Google SSO
    async function initGoogleSSO() {
        const fallbackBtn = document.getElementById('google-login-btn-fallback');
        try {
            const config = await SwiftPayAPI.request('/auth/config/');
            if (config.google_client_id && window.google) {
                google.accounts.id.initialize({
                    client_id: config.google_client_id,
                    callback: async (response) => {
                        try {
                            const data = await SwiftPayAPI.request('/auth/google/', {
                                method: 'POST',
                                body: JSON.stringify({ id_token: response.credential })
                            });
                            SwiftPayAPI.setToken(data.access, data.refresh);
                            window.location.href = 'dashboard.html';
                        } catch (err) {
                            console.error(err);
                            Components.showToast(err.message || 'Google Login Failed', 'error');
                        }
                    }
                });
                
                const container = document.getElementById('google-button-container');
                if (container) {
                    google.accounts.id.renderButton(
                        container,
                        { theme: "outline", size: "large", width: "100%" }
                    );
                }
            } else {
                if(fallbackBtn) fallbackBtn.classList.remove('hidden');
            }
        } catch (err) {
            console.error('Failed to init Google SSO:', err);
            if(fallbackBtn) fallbackBtn.classList.remove('hidden');
        }
    }
    
    // Call it immediately
    initGoogleSSO();
    
    const authForm = document.getElementById('auth-form');
    const toggleLink = document.getElementById('auth-toggle-link');
    const toggleText = document.getElementById('auth-toggle-text');
    const modalTitle = document.getElementById('modal-title');
    const submitBtn = document.getElementById('auth-submit-btn');
    const businessNameGroup = document.getElementById('business-name-group');
    const orDividerText = document.getElementById('or-divider-text');

    let isLogin = true;

    if (toggleLink) {
        toggleLink.addEventListener('click', (e) => {
            e.preventDefault();
            isLogin = !isLogin;
            if (isLogin) {
                modalTitle.textContent = 'Login to SwiftPay';
                orDividerText.textContent = 'Or login with email';
                businessNameGroup.classList.add('hidden');
                businessNameGroup.classList.remove('flex');
                submitBtn.textContent = 'Login';
                toggleText.textContent = "Don't have an account?";
                toggleLink.textContent = 'Sign up';
            } else {
                modalTitle.textContent = 'Create an account';
                orDividerText.textContent = 'Or sign up with email';
                businessNameGroup.classList.remove('hidden');
                businessNameGroup.classList.add('flex');
                submitBtn.textContent = 'Sign Up';
                toggleText.textContent = 'Already have an account?';
                toggleLink.textContent = 'Log in';
            }
        });
    }

    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email-input').value.trim();
            const password = document.getElementById('password-input').value;
            const businessName = document.getElementById('business-name-input')?.value.trim();

            if (!email || !password) {
                Components.showToast('Please enter email and password', 'error');
                return;
            }

            if (!isLogin && !businessName) {
                Components.showToast('Please enter your business name', 'error');
                return;
            }

            const originalText = submitBtn.textContent;
            submitBtn.textContent = isLogin ? 'Logging in...' : 'Signing up...';
            submitBtn.disabled = true;

            try {
                if (isLogin) {
                    const data = await SwiftPayAPI.request('/auth/login/', {
                        method: 'POST',
                        body: JSON.stringify({ email, password })
                    });
                    SwiftPayAPI.setToken(data.access, data.refresh);
                } else {
                    const data = await SwiftPayAPI.request('/auth/register/', {
                        method: 'POST',
                        body: JSON.stringify({ email, password, business_name: businessName })
                    });
                    SwiftPayAPI.setToken(data.access, data.refresh);
                }
                window.location.href = 'dashboard.html';
            } catch (err) {
                console.error(err);
                Components.showToast(err.message || 'Authentication failed', 'error');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});
