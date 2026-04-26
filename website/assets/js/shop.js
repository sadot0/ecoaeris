/**
 * EcoAeris — Shop Page
 * Файл: shop.js
 * Страница: shop.html (Магазин)
 * Автор: Самира
 *
 * JS-функция: каталог товаров с динамическими фильтрами (бренд, цена,
 * площадь покрытия, наличие) и сортировкой + корзина покупок,
 * которая сохраняется в LocalStorage (не пропадает при обновлении страницы).
 */

(function () {
  'use strict';

  /* ============================================================
     БЛОК 1. Каталог товаров (в реальном проекте — из purifiers.json)
     ============================================================ */
  const PRODUCTS = [
    { id: 1, brand: 'Xiaomi', model: 'Mi Air Purifier 3C', price: 1700000, coverage: 45, filter: 'HEPA H13', available: true, image: 'assets/images/purifiers/xiaomi-3c.svg', rating: 4.5 },
    { id: 2, brand: 'Xiaomi', model: 'Mi 4 Lite', price: 2100000, coverage: 43, filter: 'HEPA H13', available: true, image: 'assets/images/purifiers/xiaomi-4lite.svg', rating: 4.4 },
    { id: 3, brand: 'Xiaomi', model: 'Mi Smart 4 Pro', price: 2990000, coverage: 60, filter: 'HEPA H13 + Carbon', available: true, image: 'assets/images/purifiers/xiaomi-4pro.svg', rating: 4.7 },
    { id: 4, brand: 'Samsung', model: 'AX60R5080WD', price: 3500000, coverage: 60, filter: 'HEPA + Carbon', available: true, image: 'assets/images/purifiers/xiaomi-4pro.svg', rating: 4.5 },
    { id: 5, brand: 'Smartmi', model: 'Air Purifier P1', price: 4200000, coverage: 55, filter: 'HEPA H13 + Carbon', available: true, image: 'assets/images/purifiers/xiaomi-4lite.svg', rating: 4.6 },
    { id: 6, brand: 'Philips', model: 'AC1715/10', price: 5290000, coverage: 78, filter: 'NanoProtect HEPA', available: true, image: 'assets/images/purifiers/philips-ac1715.svg', rating: 4.6 },
    { id: 7, brand: 'Philips', model: 'AC2887/10', price: 6890000, coverage: 79, filter: 'NanoProtect HEPA', available: true, image: 'assets/images/purifiers/philips-ac2887.svg', rating: 4.8 },
    { id: 8, brand: 'Dyson', model: 'Purifier Cool TP10', price: 7690000, coverage: 80, filter: 'HEPA H13 + Carbon', available: true, image: 'assets/images/purifiers/dyson-tp10.svg', rating: 4.9 },
    { id: 9, brand: 'Blueair', model: 'Classic 480i', price: 8500000, coverage: 40, filter: 'HEPASilent + Carbon', available: false, image: 'assets/images/purifiers/philips-ac1715.svg', rating: 4.8 },
    { id: 10, brand: 'Dyson', model: 'PH04 Humidify+Cool', price: 12900000, coverage: 100, filter: 'HEPA H13 + Carbon', available: true, image: 'assets/images/purifiers/dyson-tp10.svg', rating: 4.9 },
    { id: 11, brand: 'IQAir', model: 'HealthPro 250', price: 21000000, coverage: 200, filter: 'HyperHEPA H14', available: true, image: 'assets/images/purifiers/iqair.svg', rating: 5.0 },
    { id: 12, brand: 'Airdog', model: 'X8 Commercial', price: 28000000, coverage: 300, filter: 'TPA ионный', available: true, image: 'assets/images/purifiers/iqair.svg', rating: 4.7 },
  ];

  /* ============================================================
     БЛОК 2. Корзина — работа с LocalStorage
     ============================================================ */
  const CART_KEY = 'ecoaeris_cart';

  /** getCart — читает корзину из LocalStorage; при ошибке возвращает пустой массив */
  function getCart() {
    try {
      return JSON.parse(localStorage.getItem(CART_KEY)) || [];
    } catch (e) {
      return [];
    }
  }

  /** saveCart — сохраняет массив корзины в LocalStorage */
  function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
  }

  /** addToCart — добавляет товар в корзину или увеличивает qty на 1 */
  function addToCart(productId) {
    const cart = getCart();
    const existing = cart.find((item) => item.id === productId);
    if (existing) {
      existing.qty += 1;
    } else {
      cart.push({ id: productId, qty: 1 });
    }
    saveCart(cart);
    renderCart();
  }

  /** removeFromCart — полностью удаляет товар из корзины по id */
  function removeFromCart(productId) {
    const cart = getCart().filter((item) => item.id !== productId);
    saveCart(cart);
    renderCart();
  }

  /** changeQty — изменяет количество товара в корзине на delta (+1 или -1) */
  function changeQty(productId, delta) {
    const cart = getCart();
    const item = cart.find((i) => i.id === productId);
    if (item) {
      item.qty = Math.max(1, item.qty + delta);
      saveCart(cart);
      renderCart();
    }
  }

  /* ============================================================
     БЛОК 3. Рендер карточек товаров
     ============================================================ */
  /** renderProducts — рендерит карточки товаров в сетку #products-grid */
  function renderProducts(products) {
    const grid = document.getElementById('products-grid');
    const counter = document.getElementById('result-count');
    counter.textContent = products.length;

    if (products.length === 0) {
      grid.innerHTML = '<p class="empty">По фильтрам ничего не найдено. Сбросьте фильтры.</p>';
      return;
    }

    grid.innerHTML = products.map((p) => `
      <article class="product-card" data-id="${p.id}">
        <div class="product-card__img">
          <img src="${p.image}" alt="${p.brand} ${p.model}" loading="lazy"
               onerror="this.src='assets/images/purifiers/placeholder.svg'">
          ${!p.available ? '<span class="product-card__oos">Нет в наличии</span>' : ''}
        </div>
        <div class="product-card__body">
          <div class="product-card__brand">${p.brand}</div>
          <h3 class="product-card__title">${p.model}</h3>
          <div class="product-card__meta">
            <span>📐 ${p.coverage} м²</span>
            <span>⭐ ${p.rating}</span>
          </div>
          <div class="product-card__filter">🧪 ${p.filter}</div>
          <div class="product-card__bottom">
            <div class="product-card__price">${formatPrice(p.price)} сум</div>
            <button class="btn btn--primary btn-add-cart"
                    ${!p.available ? 'disabled' : ''}
                    data-id="${p.id}">
              ${p.available ? 'В корзину' : 'Недоступно'}
            </button>
          </div>
        </div>
      </article>
    `).join('');

    // Навешиваем обработчики
    grid.querySelectorAll('.btn-add-cart').forEach((btn) => {
      btn.addEventListener('click', () => addToCart(parseInt(btn.dataset.id)));
    });
  }

  /** renderCart — рендерит содержимое корзины (бейдж, список, итого) */
  function renderCart() {
    const cart = getCart();
    const body = document.getElementById('cart-body');
    const badge = document.getElementById('cart-badge');
    const total = document.getElementById('cart-total');

    const totalQty = cart.reduce((s, i) => s + i.qty, 0);
    badge.textContent = totalQty;
    badge.classList.toggle('hidden', totalQty === 0);

    if (cart.length === 0) {
      body.innerHTML = '<p class="cart__empty">Корзина пуста</p>';
      total.textContent = '0';
      return;
    }

    let sum = 0;
    body.innerHTML = cart.map((item) => {
      const product = PRODUCTS.find((p) => p.id === item.id);
      if (!product) return '';
      const subtotal = product.price * item.qty;
      sum += subtotal;
      return `
        <div class="cart-item">
          <div class="cart-item__title">${product.brand} ${product.model}</div>
          <div class="cart-item__controls">
            <button class="qty-btn" data-action="minus" data-id="${item.id}">−</button>
            <span class="qty">${item.qty}</span>
            <button class="qty-btn" data-action="plus" data-id="${item.id}">+</button>
            <button class="remove-btn" data-id="${item.id}" aria-label="Удалить">🗑</button>
          </div>
          <div class="cart-item__price">${formatPrice(subtotal)} сум</div>
        </div>
      `;
    }).join('');

    total.textContent = formatPrice(sum);

    // Обработчики для +/-/удалить
    body.querySelectorAll('.qty-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.dataset.id);
        const delta = btn.dataset.action === 'plus' ? 1 : -1;
        changeQty(id, delta);
      });
    });
    body.querySelectorAll('.remove-btn').forEach((btn) => {
      btn.addEventListener('click', () => removeFromCart(parseInt(btn.dataset.id)));
    });
  }

  /* ============================================================
     БЛОК 4. Фильтры и сортировка
     ============================================================ */
  /** getActiveFilters — собирает текущие значения всех чекбоксов и радио-фильтров */
  function getActiveFilters() {
    const filters = { brands: [], price: null, coverage: [], availableOnly: false };

    document.querySelectorAll('input[data-filter="brand"]:checked').forEach((el) => {
      filters.brands.push(el.value);
    });

    const priceEl = document.querySelector('input[data-filter="price"]:checked');
    if (priceEl && priceEl.value) {
      const [min, max] = priceEl.value.split('-').map(Number);
      filters.price = { min, max };
    }

    document.querySelectorAll('input[data-filter="coverage"]:checked').forEach((el) => {
      filters.coverage.push(el.value);
    });

    filters.availableOnly = document.querySelector('input[data-filter="available"]')?.checked || false;

    return filters;
  }

  /** applyFilters — фильтрует и сортирует товары, затем перерендеривает сетку */
  function applyFilters() {
    const f = getActiveFilters();
    let result = [...PRODUCTS];

    if (f.brands.length) {
      result = result.filter((p) => f.brands.includes(p.brand));
    }
    if (f.price) {
      result = result.filter((p) => p.price >= f.price.min && p.price <= f.price.max);
    }
    if (f.coverage.length) {
      result = result.filter((p) => {
        if (f.coverage.includes('small') && p.coverage < 40) return true;
        if (f.coverage.includes('medium') && p.coverage >= 40 && p.coverage < 80) return true;
        if (f.coverage.includes('large') && p.coverage >= 80) return true;
        return false;
      });
    }
    if (f.availableOnly) {
      result = result.filter((p) => p.available);
    }

    // Сортировка
    const sort = document.getElementById('sort-select').value;
    if (sort === 'price-asc') result.sort((a, b) => a.price - b.price);
    if (sort === 'price-desc') result.sort((a, b) => b.price - a.price);
    if (sort === 'coverage-desc') result.sort((a, b) => b.coverage - a.coverage);

    renderProducts(result);
  }

  /** formatPrice — форматирует число в удобочитаемую цену с пробелами */
  function formatPrice(n) {
    return n.toLocaleString('ru-RU').replace(/,/g, ' ');
  }

  /* ============================================================
     БЛОК 5. Старт
     ============================================================ */
  document.addEventListener('DOMContentLoaded', () => {
    // Первый рендер
    renderProducts(PRODUCTS);
    renderCart();

    // Счётчик в hero
    document.getElementById('shop-counter').textContent =
      `${PRODUCTS.length} моделей от ${formatPrice(Math.min(...PRODUCTS.map(p => p.price)))} сум`;

    // Фильтры
    document.querySelectorAll('.filter').forEach((el) => {
      el.addEventListener('change', applyFilters);
    });
    document.getElementById('sort-select').addEventListener('change', applyFilters);
    document.getElementById('reset-filters').addEventListener('click', () => {
      document.querySelectorAll('.filter').forEach((el) => {
        if (el.type === 'checkbox') el.checked = false;
      });
      document.querySelector('input[data-filter="price"][value=""]').checked = true;
      applyFilters();
    });

    // Корзина — открытие/закрытие
    const cartEl = document.getElementById('cart');
    document.getElementById('cart-toggle').addEventListener('click', () => cartEl.classList.toggle('open'));
    document.getElementById('cart-close').addEventListener('click', () => cartEl.classList.remove('open'));
  });
})();
