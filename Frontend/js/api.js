/**
 * AI-Enhanced E-Commerce Platform
 * Core API & Utility Module
 */

// Dynamic API Base URL:
// In production (e.g. on Render) or when served directly by FastAPI (port 8000), use ${window.location.origin}/api.
// When developing locally with an independent frontend dev server (e.g. port 5500/3000), route to local backend on 8000.
const isLocalDevServer = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    && window.location.port !== ''
    && window.location.port !== '8000';

const API_BASE = isLocalDevServer 
    ? 'http://127.0.0.1:8000/api' 
    : `${window.location.origin}/api`;

const API = {
    /**
     * Get stored JWT token
     */
    getToken() {
        return localStorage.getItem('ai_ecommerce_token');
    },

    /**
     * Set stored JWT token and user info
     */
    setAuth(token, user) {
        localStorage.setItem('ai_ecommerce_token', token);
        localStorage.setItem('ai_ecommerce_user', JSON.stringify(user));
    },

    /**
     * Get current user object
     */
    getUser() {
        const u = localStorage.getItem('ai_ecommerce_user');
        try {
            return u ? JSON.parse(u) : null;
        } catch {
            return null;
        }
    },

    /**
     * Clear auth credentials
     */
    clearAuth() {
        localStorage.removeItem('ai_ecommerce_token');
        localStorage.removeItem('ai_ecommerce_user');
    },

    /**
     * Generic HTTP request handler
     */
    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Handle Unauthorized / Expired session
            if (response.status === 401) {
                // Only redirect if not already on login/register
                if (!window.location.pathname.includes('login.html') && !window.location.pathname.includes('register.html')) {
                    this.clearAuth();
                }
            }

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const errorMessage = data.detail || data.message || `Request failed (${response.status})`;
                throw new Error(errorMessage);
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    get(endpoint, params = {}) {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${endpoint}?${query}` : endpoint;
        return this.request(url, { method: 'GET' });
    },

    post(endpoint, body = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });
    },

    put(endpoint, body = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
};

/**
 * Toast Notification System
 */
function showToast(message, type = 'info', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type} animate-slide-down`;

    const iconMap = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <span style="font-weight: 800; font-size: 1.1rem;">${iconMap[type] || 'ℹ'}</span>
        <span style="flex: 1; font-size: 0.92rem;">${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Utility: Format Currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount || 0);
}

/**
 * Global Loading Overlay
 */
function toggleLoading(show, message = 'Loading...') {
    let overlay = document.getElementById('global-loading-overlay');
    if (show) {
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'global-loading-overlay';
            overlay.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px);
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                gap: 16px; z-index: 99999; color: #fff;
            `;
            overlay.innerHTML = `
                <div class="spinner" style="width: 48px; height: 48px; border-width: 4px;"></div>
                <div id="loading-text" style="font-weight: 600; font-size: 1.05rem;">${message}</div>
            `;
            document.body.appendChild(overlay);
        } else {
            document.getElementById('loading-text').innerText = message;
            overlay.style.display = 'flex';
        }
    } else {
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
}

