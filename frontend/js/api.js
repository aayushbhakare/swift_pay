
const SwiftPayAPI = {
    BASE_URL: '/api/v1',
    getToken() { return localStorage.getItem('swiftpay_jwt_access') || ''; },
    setToken(access, refresh) {
        localStorage.setItem('swiftpay_jwt_access', access);
        if (refresh) localStorage.setItem('swiftpay_jwt_refresh', refresh);
    },
    clearToken() {
        localStorage.removeItem('swiftpay_jwt_access');
        localStorage.removeItem('swiftpay_jwt_refresh');
    },
    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getToken()}`,
            ...options.headers,
        };
        const res = await fetch(`${this.BASE_URL}${endpoint}`, { ...options, headers });
        if (res.status === 401) {
            this.clearToken();
            window.location.href = 'landingpage.html';
            throw new Error('UNAUTHORIZED');
        }
        if (!res.ok) {
            const body = await res.json().catch(() => ({}));
            throw new Error(body.error || `Request failed (${res.status})`);
        }
        if (options.responseType === 'blob') return res.blob();
        if (options.responseType === 'text') return res.text();
        return res.json();
    }
};
