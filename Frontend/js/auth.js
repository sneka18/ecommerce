/**
 * AI-Enhanced E-Commerce Platform
 * Authentication & RBAC Guard Module
 */

document.addEventListener('DOMContentLoaded', () => {
    updateNavbarAuth();
    setupGlobalSearch();
});

function updateNavbarAuth() {
    const authActions = document.getElementById('navbar-auth-actions');
    if (!authActions) return;

    const user = API.getUser();
    const token = API.getToken();

    if (user && token) {
        let dashboardLink = '';
        if (user.role === 'seller') {
            dashboardLink = `<a href="/seller/dashboard.html" class="nav-link" style="color: var(--primary); font-weight: 700;">🏪 Seller Portal</a>`;
        } else if (user.role === 'admin') {
            dashboardLink = `<a href="/admin/dashboard.html" class="nav-link" style="color: #ec4899; font-weight: 700;">⚙️ Admin Panel</a>`;
        }

        authActions.innerHTML = `
            ${dashboardLink}
            <div style="display: flex; align-items: center; gap: 8px;">
                <a href="/profile.html" class="btn btn-outline btn-sm" title="Manage Profile">
                    👤 ${user.full_name.split(' ')[0]}
                    <span style="font-size: 0.72rem; padding: 2px 6px; background: var(--primary-light); color: var(--primary); border-radius: 99px; margin-left: 4px; text-transform: uppercase;">${user.role}</span>
                </a>
                <button onclick="handleLogout()" class="btn btn-outline btn-sm" style="border-color: #fca5a5; color: #dc2626;" title="Sign out">
                    Logout
                </button>
            </div>
        `;
    } else {
        authActions.innerHTML = `
            <a href="/login.html" class="btn btn-outline btn-sm">Sign In</a>
            <a href="/register.html" class="btn btn-primary btn-sm">Register</a>
        `;
    }
}

function handleLogout() {
    API.clearAuth();
    showToast('You have been logged out successfully.', 'info');
    setTimeout(() => {
        window.location.href = '/login.html';
    }, 500);
}

function requireAuth(allowedRoles = []) {
    const user = API.getUser();
    const token = API.getToken();

    if (!user || !token) {
        showToast('Please sign in to access this page.', 'warning');
        setTimeout(() => {
            window.location.href = `/login.html?redirect=${encodeURIComponent(window.location.pathname)}`;
        }, 600);
        return false;
    }

    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role) && user.role !== 'admin') {
        showToast(`Access denied: requires ${allowedRoles.join(' or ')} permission.`, 'error');
        setTimeout(() => {
            window.location.href = '/';
        }, 800);
        return false;
    }

    return true;
}

function fillDemoCredentials(role) {
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (!emailInput || !passwordInput) return;

    if (role === 'admin') {
        emailInput.value = 'admin@ecommerce.com';
        passwordInput.value = 'AdminPassword123!';
    } else if (role === 'seller') {
        emailInput.value = 'seller@techhub.com';
        passwordInput.value = 'SellerPassword123!';
    } else if (role === 'customer') {
        emailInput.value = 'john@example.com';
        passwordInput.value = 'Customer123!';
    }
    showToast(`Loaded ${role.toUpperCase()} demo credentials. Click 'Sign In' to proceed!`, 'info');
}

function setupGlobalSearch() {
    const searchForm = document.getElementById('global-search-form');
    const searchInput = document.getElementById('global-search-input');
    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const q = searchInput.value.trim();
            if (q) {
                window.location.href = `/products.html?q=${encodeURIComponent(q)}`;
            }
        });
    }
}

