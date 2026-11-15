/**
 * AI-Enhanced E-Commerce Platform
 * Shopping Cart Client Module
 */

document.addEventListener('DOMContentLoaded', () => {
    refreshCartBadge();
});

async function refreshCartBadge() {
    const badge = document.getElementById('cart-count-badge');
    if (!badge) return;

    if (!API.getToken()) {
        badge.innerText = '0';
        badge.style.display = 'none';
        return;
    }

    try {
        const cart = await API.get('/cart');
        const count = cart.total_items || 0;
        badge.innerText = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    } catch {
        badge.style.display = 'none';
    }
}

async function addToCart(productId, quantity = 1) {
    if (!API.getToken()) {
        showToast('Please sign in to add items to your shopping cart.', 'warning');
        setTimeout(() => {
            window.location.href = `/login.html?redirect=${encodeURIComponent(window.location.pathname)}`;
        }, 800);
        return;
    }

    try {
        await API.post('/cart', {
            product_id: parseInt(productId),
            quantity: parseInt(quantity)
        });

        showToast('Product added to your cart!', 'success');
        refreshCartBadge();

        // Animate cart button
        const cartBtn = document.getElementById('navbar-cart-btn');
        if (cartBtn) {
            cartBtn.classList.add('animate-scale-up');
            setTimeout(() => cartBtn.classList.remove('animate-scale-up'), 400);
        }
    } catch (error) {
        showToast(error.message || 'Could not add product to cart.', 'error');
    }
}

