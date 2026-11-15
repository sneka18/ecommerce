/**
 * AI-Enhanced E-Commerce Platform
 * Main Homepage & Global UI Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    loadRecommendedProducts();
    loadTrendingProducts();
    loadAIShoppingInsights();
});

/**
 * Render standard product card HTML
 */
function renderProductCard(product, options = {}) {
    const isAi = options.isAiRecommended || false;
    const aiReason = options.reason || '';

    return `
        <div class="product-card animate-fade-in">
            ${isAi ? `<div class="product-card-badge">✨ AI Recommended</div>` : ''}
            <div class="product-image-wrap">
                <a href="/product-details.html?id=${product.id}">
                    <img src="${product.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80'}" alt="${product.name}" loading="lazy">
                </a>
            </div>
            <div class="product-body">
                <div class="product-meta">
                    <span class="product-category">${product.category ? product.category.name : 'Catalog'}</span>
                    <span class="product-rating">★ ${product.rating || '4.8'} <span style="color: var(--text-muted); font-size: 0.75rem;">(${product.num_reviews || 0})</span></span>
                </div>
                <h3 class="product-title">
                    <a href="/product-details.html?id=${product.id}">${product.name}</a>
                </h3>
                <p class="product-desc-snippet">${product.description || 'Premium craftsmanship and outstanding quality.'}</p>
                ${aiReason ? `<div style="font-size: 0.76rem; color: #6366f1; background: #eef2ff; padding: 4px 8px; border-radius: 6px; margin-bottom: 12px; font-weight: 500;">💡 ${aiReason}</div>` : ''}
                <div class="product-footer">
                    <span class="product-price">${formatCurrency(product.price)}</span>
                    <button class="add-cart-btn" onclick="addToCart(${product.id}, 1)" title="Add to Cart">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="9" cy="21" r="1"></circle>
                            <circle cx="20" cy="21" r="1"></circle>
                            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Load Categories Chips
 */
async function loadCategories() {
    const container = document.getElementById('category-chips-container');
    if (!container) return;

    try {
        const categories = await API.get('/categories');
        let html = `<a href="/products.html" class="category-chip active">All Products</a>`;
        categories.forEach(cat => {
            html += `<a href="/products.html?category=${cat.id}" class="category-chip">${cat.name}</a>`;
        });
        container.innerHTML = html;
    } catch (e) {
        console.error('Error loading categories:', e);
    }
}

/**
 * Load Personalized ML Recommendations (KNN Model)
 */
async function loadRecommendedProducts() {
    const grid = document.getElementById('recommended-products-grid');
    const titleElem = document.getElementById('recommendations-section-title');
    if (!grid) return;

    try {
        const data = await API.get('/recommendations', { limit: 4 });
        if (titleElem && data.title) {
            titleElem.innerHTML = `✨ ${data.title}`;
        }

        if (!data.recommendations || data.recommendations.length === 0) {
            grid.innerHTML = `<p style="color: var(--text-secondary); grid-column: 1 / -1;">No recommendations available at this time.</p>`;
            return;
        }

        grid.innerHTML = data.recommendations.map(item => 
            renderProductCard(item.product, { isAiRecommended: true, reason: item.reason })
        ).join('');
    } catch (e) {
        console.error('Error loading recommendations:', e);
        grid.innerHTML = `<p style="color: var(--text-muted); grid-column: 1 / -1;">Browse products to activate machine learning recommendations.</p>`;
    }
}

/**
 * Load Featured / Trending Catalog Products
 */
async function loadTrendingProducts() {
    const grid = document.getElementById('trending-products-grid');
    if (!grid) return;

    try {
        const response = await API.get('/products', { limit: 8, sort_by: 'popular' });
        const items = response.items || [];
        if (items.length === 0) {
            grid.innerHTML = `<p style="color: var(--text-secondary); grid-column: 1 / -1;">Catalog is being updated.</p>`;
            return;
        }

        grid.innerHTML = items.map(p => renderProductCard(p)).join('');
    } catch (e) {
        console.error('Error loading trending products:', e);
    }
}

/**
 * Load Dynamic AI Shopping Insights (Google Gemini API)
 */
async function loadAIShoppingInsights() {
    const container = document.getElementById('ai-shopping-insights-container');
    if (!container) return;

    try {
        const res = await API.post('/ai/shopping-insights', {
            category: 'Electronics & Lifestyle',
            interests: ['Premium performance', 'Smart ergonomics', 'Energy efficiency']
        });

        const insights = res.data || {};
        container.innerHTML = `
            <div class="ai-insights-card animate-fade-in">
                <div class="ai-badge">✨ Powered by Google Gemini AI</div>
                <h3 class="ai-insights-headline">${insights.headline || 'Intelligent Shopping Assistant'}</h3>
                <p style="font-size: 1.05rem; opacity: 0.95; max-width: 800px; line-height: 1.6;">
                    ${insights.ai_recommendation_summary || 'Our generative AI analyzes customer sentiment and trending specifications to guide your purchasing decisions.'}
                </p>
                <div class="ai-tips-grid">
                    ${(insights.smart_tips || [
                        'Look for balanced customer feedback and warranty verification.',
                        'Compare specifications with your daily workload requirements.',
                        'Leverage seasonal promotions to maximize hardware value.'
                    ]).map(tip => `
                        <div class="ai-tip-item">
                            <strong style="display: block; margin-bottom: 4px; color: #a5b4fc;">💡 Smart Advice</strong>
                            ${tip}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } catch (e) {
        console.error('Error loading AI shopping insights:', e);
        container.style.display = 'none';
    }
}

