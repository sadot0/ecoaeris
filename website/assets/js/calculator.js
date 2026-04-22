/**
 * EcoAeris — Calculator Wizard
 * Автор: Муслима
 *
 * Уникальная логика: мульти-шаговый wizard (4 шага) с сохранением
 * ответов пользователя и рекомендацией очистителя на основе
 * матрицы правил.
 */

(function () {
  'use strict';

  /* ============================================================
     БЛОК 1. Каталог очистителей
     Реальные модели с реальными ценами UZ (декабрь 2025)
     ============================================================ */
  const PURIFIERS = [
    {
      id: 'xiaomi-3c', brand: 'Xiaomi', model: 'Mi Air Purifier 3C',
      price: 1700000, coverage: 45, tags: ['budget', 'apartment', 'kids'],
      image: 'assets/images/purifiers/xiaomi-3c.svg',
      pros: ['Бесшумный', 'Удалённое управление', 'Бюджетный'],
    },
    {
      id: 'xiaomi-4pro', brand: 'Xiaomi', model: 'Mi Smart Air Purifier 4 Pro',
      price: 2990000, coverage: 60, tags: ['apartment', 'kids', 'allergy', 'mid'],
      image: 'assets/images/purifiers/xiaomi-4pro.svg',
      pros: ['HEPA H13 фильтр', 'OLED-дисплей', 'Приложение'],
    },
    {
      id: 'philips-ac1715', brand: 'Philips', model: 'AC1715/10',
      price: 5290000, coverage: 78, tags: ['apartment', 'house', 'allergy'],
      image: 'assets/images/purifiers/philips-ac1715.svg',
      pros: ['HEPA NanoProtect', 'Режим сна', 'Датчик PM2.5'],
    },
    {
      id: 'dyson-tp10', brand: 'Dyson', model: 'Purifier Cool TP10',
      price: 7690000, coverage: 80, tags: ['apartment', 'house', 'premium', 'high', 'allergy'],
      image: 'assets/images/purifiers/dyson-tp10.svg',
      pros: ['360° фильтрация', 'Встроенный вентилятор', 'Премиум-дизайн'],
    },
    {
      id: 'industrial-pro', brand: 'IQAir', model: 'HealthPro 250',
      price: 21000000, coverage: 200, tags: ['office', 'industrial', 'high'],
      image: 'assets/images/purifiers/iqair.svg',
      pros: ['Для площадей до 200м²', 'Медицинский HEPA', 'Промышленное применение'],
    },
  ];

  /* ============================================================
     БЛОК 2. Состояние wizard'а
     ============================================================ */
  const state = {
    step: 1,
    totalSteps: 4,
    answers: {
      placement: null,  // apartment | house | office | industrial
      area: 60,         // м²
      needs: null,      // allergy | kids | smoke | none
      budget: null,     // low | mid | high | rent
    },
  };

  /* ============================================================
     БЛОК 3. Логика перехода между шагами
     ============================================================ */
  function showStep(num) {
    document.querySelectorAll('.wizard__step').forEach((el) => {
      el.classList.toggle('active', parseInt(el.dataset.step) === num);
    });

    // Обновляем progress bar (на шаге 5 = результат, ставим 100%)
    const bar = document.getElementById('progress-bar');
    const label = document.getElementById('progress-label');
    if (num <= 4) {
      bar.style.width = `${(num / 4) * 100}%`;
      label.textContent = `Шаг ${num} из 4`;
    } else {
      bar.style.width = '100%';
      label.textContent = 'Готово ✓';
    }
  }

  function next() {
    if (state.step < 5) {
      state.step++;
      showStep(state.step);
      if (state.step === 5) calculateAndRender();
    }
  }

  function back() {
    if (state.step > 1) {
      state.step--;
      showStep(state.step);
    }
  }

  /* ============================================================
     БЛОК 4. Алгоритм рекомендации
     Фильтруем каталог по ответам, сортируем по релевантности
     ============================================================ */
  function calculate() {
    const { placement, area, needs, budget } = state.answers;

    // 1. Фильтр по типу помещения
    let candidates = PURIFIERS.filter((p) =>
      p.tags.includes(placement) || (placement === 'industrial' && p.coverage >= 150)
    );

    // 2. Фильтр по площади — coverage должен быть >= area
    candidates = candidates.filter((p) => p.coverage >= area * 0.8);

    // 3. Фильтр по бюджету
    const budgetMap = { low: 3000000, mid: 6000000, high: Infinity };
    if (budget !== 'rent' && budgetMap[budget]) {
      candidates = candidates.filter((p) => p.price <= budgetMap[budget]);
    }

    // 4. Скоринг: +1 за каждое совпадение tag с needs
    candidates.forEach((p) => {
      p._score = 0;
      if (needs && needs !== 'none' && p.tags.includes(needs)) p._score += 10;
      // Бонус за соответствие покрытия (не сильно больше и не меньше)
      const diff = Math.abs(p.coverage - area);
      p._score += Math.max(0, 20 - diff / 5);
    });

    // 5. Сортируем по скору
    candidates.sort((a, b) => b._score - a._score);

    // Fallback если нет вариантов — даём самый бюджетный
    if (candidates.length === 0) {
      candidates = [PURIFIERS[0]];
    }

    return {
      primary: candidates[0],
      alternatives: candidates.slice(1, 3),
    };
  }

  /* ============================================================
     БЛОК 5. Рендер результата
     ============================================================ */
  function calculateAndRender() {
    const { primary, alternatives } = calculate();

    document.getElementById('result-title').textContent = `${primary.brand} ${primary.model}`;
    document.getElementById('result-subtitle').textContent =
      `Лучший выбор для ${state.answers.placement === 'apartment' ? 'квартиры' : 'помещения'} ${state.answers.area} м²`;

    const container = document.getElementById('result-main');
    container.innerHTML = `
      <article class="card recommendation">
        <div class="recommendation__grid">
          <img src="${primary.image}" alt="${primary.model}" class="recommendation__img"
               onerror="this.src='assets/images/purifiers/placeholder.svg'">
          <div class="recommendation__body">
            <div class="recommendation__price">${formatPrice(primary.price)} сум</div>
            <ul class="recommendation__pros">
              ${primary.pros.map((p) => `<li>✓ ${p}</li>`).join('')}
            </ul>
            <div class="recommendation__coverage">
              <b>Площадь покрытия:</b> ${primary.coverage} м²
            </div>
          </div>
        </div>
      </article>

      ${alternatives.length > 0 ? `
        <h3 class="alt-title">Другие варианты:</h3>
        <div class="alternatives">
          ${alternatives.map((a) => `
            <article class="card alt">
              <h4>${a.brand} ${a.model}</h4>
              <div class="alt__price">${formatPrice(a.price)} сум</div>
              <small>Покрытие: ${a.coverage} м²</small>
            </article>
          `).join('')}
        </div>
      ` : ''}
    `;
  }

  function formatPrice(n) {
    return n.toLocaleString('ru-RU').replace(/,/g, ' ');
  }

  /* ============================================================
     БЛОК 6. Навешиваем обработчики
     ============================================================ */
  document.addEventListener('DOMContentLoaded', () => {
    // Клики по option-card — запоминаем выбор и автоматически next
    document.querySelectorAll('.option-card').forEach((card) => {
      card.addEventListener('click', () => {
        const step = card.closest('.wizard__step');
        const stepNum = parseInt(step.dataset.step);
        const value = card.dataset.value;

        // Убираем active у других и ставим на эту
        step.querySelectorAll('.option-card').forEach((c) => c.classList.remove('active'));
        card.classList.add('active');

        // Сохраняем в state
        const keyMap = { 1: 'placement', 3: 'needs', 4: 'budget' };
        state.answers[keyMap[stepNum]] = value;

        // Автопереход через 300мс (чтобы пользователь увидел выбор)
        setTimeout(next, 300);
      });
    });

    // Кнопки «Назад / Далее»
    document.querySelectorAll('[data-action]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        if (action === 'next') next();
        if (action === 'back') back();
        if (action === 'restart') {
          state.step = 1;
          state.answers = { placement: null, area: 60, needs: null, budget: null };
          showStep(1);
        }
      });
    });

    // Слайдер площади
    const areaSlider = document.getElementById('area-slider');
    const areaValue = document.getElementById('area-value');
    if (areaSlider) {
      areaSlider.addEventListener('input', (e) => {
        state.answers.area = parseInt(e.target.value);
        areaValue.textContent = state.answers.area;
      });
    }
  });
})();
