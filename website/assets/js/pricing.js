/**
 * EcoAeris — Pricing Page
 * Автор: Мухаммад
 *
 * Уникальная JS-функция:
 *   1. Chart.js график AQI за 7 дней для 3 городов UZ
 *   2. PM2.5 → AQI конвертер по US EPA с анимацией счётчика
 */

(function () {
  'use strict';

  /* ============================================================
     БЛОК 1. Генерация демо-данных AQI за 7 дней
     ВАЖНО: в ассесменте лучше использовать реальные данные
     WAQI API /feed/{city}/history (но бесплатный тариф не даёт history).
     Поэтому имитируем реалистичные значения на основе IQAir-отчёта.
     ============================================================ */
  function generateDemoAQI() {
    const days = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(d.getDate() - i);
      days.push(d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }));
    }

    // Реалистичные AQI: Ташкент хуже, Бухара и Самарканд чуть лучше
    return {
      labels: days,
      tashkent: [148, 165, 172, 158, 189, 167, 156],
      samarkand: [95, 102, 110, 98, 118, 105, 92],
      bukhara: [78, 82, 88, 95, 102, 89, 84],
    };
  }

  /* ============================================================
     БЛОК 2. Инициализация Chart.js
     ============================================================ */
  function initChart() {
    const ctx = document.getElementById('aqi-chart');
    if (!ctx) return;

    const data = generateDemoAQI();

    // Градиент для фона графика Ташкента
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(239, 68, 68, 0.4)');
    gradient.addColorStop(1, 'rgba(239, 68, 68, 0)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Ташкент',
            data: data.tashkent,
            borderColor: '#EF4444',
            backgroundColor: gradient,
            fill: true,
            tension: 0.4,
            borderWidth: 3,
          },
          {
            label: 'Самарканд',
            data: data.samarkand,
            borderColor: '#F59E0B',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            tension: 0.4,
            borderWidth: 2,
          },
          {
            label: 'Бухара',
            data: data.bukhara,
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { font: { family: 'Inter', size: 13 } } },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: AQI ${ctx.raw}`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'AQI (US EPA)' },
            grid: { color: 'rgba(15, 23, 42, 0.05)' },
          },
          x: { grid: { display: false } },
        },
      },
    });
  }

  /* ============================================================
     БЛОК 3. PM2.5 → AQI конвертер
     Формула US EPA: линейная интерполяция по breakpoints.
     Источник: https://en.wikipedia.org/wiki/Air_quality_index#United_States
     ============================================================ */
  const EPA_BREAKPOINTS = [
    // [pm25_low, pm25_high, aqi_low, aqi_high, category, color]
    [0.0,  9.0,   0,   50,  'Хороший',           '#00E400'],
    [9.1,  35.4,  51,  100, 'Умеренный',         '#FFFF00'],
    [35.5, 55.4,  101, 150, 'Вредный для уязвимых', '#FF7E00'],
    [55.5, 125.4, 151, 200, 'Вредный',           '#FF0000'],
    [125.5, 225.4, 201, 300, 'Очень вредный',    '#8F3F97'],
    [225.5, 500,  301, 500, 'Опасный',           '#7E0023'],
  ];

  function pm25ToAQI(pm25) {
    const bp = EPA_BREAKPOINTS.find((b) => pm25 >= b[0] && pm25 <= b[1]);
    if (!bp) return { aqi: 500, category: 'За шкалой', color: '#7E0023' };

    const [pmLow, pmHigh, aqiLow, aqiHigh, category, color] = bp;
    // Линейная интерполяция
    const aqi = Math.round(
      ((aqiHigh - aqiLow) / (pmHigh - pmLow)) * (pm25 - pmLow) + aqiLow
    );
    return { aqi, category, color };
  }

  /* ============================================================
     БЛОК 4. Анимация счётчика AQI (от 0 до значения)
     Уникальная деталь — плавное "проматывание" числа
     ============================================================ */
  function animateCounter(target, duration = 800) {
    const el = document.querySelector('.converter__value');
    if (!el) return;

    const start = parseInt(el.textContent) || 0;
    const diff = target - start;
    const startTime = performance.now();

    function step(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      // Ease-out-cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(start + diff * eased);
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function renderConverter(pm25) {
    const result = pm25ToAQI(pm25);
    const container = document.getElementById('converter-result');

    // Если результат ещё не существует — создаём
    if (!container.querySelector('.converter__value')) {
      container.innerHTML = `
        <div class="converter__card" style="--result-color: ${result.color}">
          <span class="converter__label">AQI</span>
          <div class="converter__value">0</div>
          <span class="converter__category">${result.category}</span>
        </div>
      `;
    } else {
      // Обновляем стиль и категорию
      const card = container.querySelector('.converter__card');
      card.style.setProperty('--result-color', result.color);
      container.querySelector('.converter__category').textContent = result.category;
    }

    animateCounter(result.aqi);
  }

  /* ============================================================
     БЛОК 5. Инициализация
     ============================================================ */
  document.addEventListener('DOMContentLoaded', () => {
    initChart();

    // Первый рендер конвертера
    const input = document.getElementById('pm25-input');
    if (input) {
      renderConverter(parseFloat(input.value));
      input.addEventListener('input', (e) => {
        const v = parseFloat(e.target.value);
        if (!isNaN(v) && v >= 0 && v <= 500) {
          renderConverter(v);
        }
      });
    }
  });
})();
