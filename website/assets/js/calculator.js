/**
 * EcoAeris — Calculator Wizard
 * Файл: calculator.js
 * Страница: calculator.html (Калькулятор подбора)
 * Автор: Муслима
 *
 * JS-функция: мульти-шаговый wizard с взвешенным скорингом.
 * Пользователь проходит 4 шага (тип помещения, площадь, потребности, бюджет),
 * после чего алгоритм оценивает 12 моделей очистителей по 4 критериям
 * (coverage*35% + budget*25% + needs*25% + type*15%) и выдаёт рекомендацию.
 */

(function () {
  'use strict';

  /* ============================================================
     БЛОК 1. Каталог очистителей — 12 моделей
     Реальные модели с реальными ценами UZ
     ============================================================ */
  const PURIFIERS = [
    // БЮДЖЕТ (до 2 млн)
    { id: 'xiaomi-3c', brand: 'Xiaomi', model: 'Mi Air Purifier 3C', price: 1700000, coverage: 45, cadr: 320, filter: 'HEPA H13', quiet: true, tags: ['budget','apartment','kids'], image: 'assets/images/purifiers/xiaomi-3c.svg', pros: ['Бесшумный ночной режим','Приложение Mi Home','Самый бюджетный'] },
    { id: 'xiaomi-4lite', brand: 'Xiaomi', model: 'Mi Air Purifier 4 Lite', price: 2100000, coverage: 43, cadr: 360, filter: 'HEPA H13', quiet: false, tags: ['budget','apartment'], image: 'assets/images/purifiers/xiaomi-4lite.svg', pros: ['HEPA H13 фильтр','Компактный размер','Приложение Mi Home'] },

    // СРЕДНИЙ (2-5 млн)
    { id: 'xiaomi-4pro', brand: 'Xiaomi', model: 'Mi Smart Air Purifier 4 Pro', price: 2990000, coverage: 60, cadr: 500, filter: 'HEPA H13+Carbon', quiet: false, tags: ['apartment','kids','allergy','smoke','mid'], image: 'assets/images/purifiers/xiaomi-4pro.svg', pros: ['HEPA H13 + угольный фильтр','OLED-дисплей','CADR 500 м³/ч'] },
    { id: 'samsung-ax60', brand: 'Samsung', model: 'AX60R5080WD', price: 3500000, coverage: 60, cadr: 467, filter: 'HEPA+Carbon', quiet: false, tags: ['apartment','house','mid','smoke','pets'], image: 'assets/images/purifiers/xiaomi-4pro.svg', pros: ['3-ступенчатая фильтрация','Убирает запах дыма и животных','Wi-Fi управление'] },
    { id: 'smartmi-p1', brand: 'Smartmi', model: 'Air Purifier P1', price: 4200000, coverage: 55, cadr: 400, filter: 'HEPA H13+Carbon', quiet: true, tags: ['apartment','house','kids','mid','dust'], image: 'assets/images/purifiers/xiaomi-4lite.svg', pros: ['Тихий как шёпот','Датчик CO2','Компактный и стильный'] },

    // ВЫШЕ СРЕДНЕГО (5-10 млн)
    { id: 'philips-ac1715', brand: 'Philips', model: 'AC1715/10', price: 5290000, coverage: 78, cadr: 550, filter: 'NanoProtect HEPA', quiet: false, tags: ['apartment','house','allergy','dust'], image: 'assets/images/purifiers/philips-ac1715.svg', pros: ['NanoProtect HEPA фильтр','Режим сна','Датчик PM2.5 в реальном времени'] },
    { id: 'philips-ac2887', brand: 'Philips', model: 'AC2887/10', price: 6890000, coverage: 79, cadr: 600, filter: 'NanoProtect HEPA', quiet: false, tags: ['house','office','allergy','high'], image: 'assets/images/purifiers/philips-ac2887.svg', pros: ['CADR 600 м³/ч','AeraSense датчик','Для больших помещений'] },
    { id: 'dyson-tp10', brand: 'Dyson', model: 'Purifier Cool TP10', price: 7690000, coverage: 80, cadr: 350, filter: 'HEPA H13+Carbon', quiet: false, tags: ['apartment','house','premium','high','allergy'], image: 'assets/images/purifiers/dyson-tp10.svg', pros: ['Вентилятор + очиститель 2в1','360° HEPA фильтрация','Премиум-дизайн'] },
    { id: 'blueair-classic', brand: 'Blueair', model: 'Classic 480i', price: 8500000, coverage: 40, cadr: 476, filter: 'HEPASilent+Carbon', quiet: true, tags: ['apartment','house','allergy','kids','high','dust'], image: 'assets/images/purifiers/philips-ac1715.svg', pros: ['Шведский бренд №1','HEPASilent технология','Почти бесшумный'] },

    // ПРЕМИУМ (10+ млн)
    { id: 'dyson-ph04', brand: 'Dyson', model: 'Purifier Humidify+Cool PH04', price: 12900000, coverage: 100, cadr: 400, filter: 'HEPA H13+Carbon', quiet: false, tags: ['house','office','premium','high','allergy','dust'], image: 'assets/images/purifiers/dyson-tp10.svg', pros: ['Очистка + увлажнение + охлаждение','Формальдегид-сенсор','До 100 м²'] },

    // ПРОМЫШЛЕННЫЙ (15+ млн)
    { id: 'iqair-hp250', brand: 'IQAir', model: 'HealthPro 250', price: 21000000, coverage: 200, cadr: 780, filter: 'HyperHEPA H14', quiet: false, tags: ['office','industrial','high'], image: 'assets/images/purifiers/iqair.svg', pros: ['Медицинский HyperHEPA H14','До 200 м²','Швейцарское качество'] },
    { id: 'airdog-x8', brand: 'Airdog', model: 'X8 Commercial', price: 28000000, coverage: 300, cadr: 1000, filter: 'TPA ионный', quiet: false, tags: ['industrial','high'], image: 'assets/images/purifiers/iqair.svg', pros: ['CADR 1000 м³/ч','Моющийся фильтр (без замены)','До 300 м²'] },
  ];

  /* ============================================================
     БЛОК 2. Состояние wizard'а
     ============================================================ */
  const state = {
    step: 1,
    totalSteps: 4,
    answers: {
      placement: null,  // apartment | house | office | industrial
      area: 60,         // м2
      needs: null,      // allergy | kids | smoke | none
      budget: null,     // low | mid | high | rent
    },
  };

  /* ============================================================
     БЛОК 3. Логика перехода между шагами
     ============================================================ */
  /** showStep — показывает нужный шаг wizard'а и обновляет progress bar */
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
      label.textContent = 'Готово';
    }
  }

  /** next — переход к следующему шагу; на шаге 5 запускает расчёт */
  function next() {
    if (state.step < 5) {
      state.step++;
      showStep(state.step);
      if (state.step === 5) calculateAndRender();
    }
  }

  /** back — переход к предыдущему шагу */
  function back() {
    if (state.step > 1) {
      state.step--;
      showStep(state.step);
    }
  }

  /* ============================================================
     БЛОК 4. Алгоритм рекомендации — взвешенный скоринг
     Все кандидаты оцениваются, ни один не отсеивается.
     totalScore = coverage*35 + budget*25 + needs*25 + type*15
     ============================================================ */

  /**
   * coverageScore: насколько площадь покрытия соответствует площади помещения.
   * Идеальный диапазон — coverage/area от 1.0 до 1.5x (100 баллов).
   * Ниже 1.0 или выше 1.5 — плавное снижение.
   */
  function scoreCoverage(purifier, area) {
    if (area <= 0) return 50;
    const ratio = purifier.coverage / area;

    if (ratio >= 1.0 && ratio <= 1.5) {
      return 100;
    } else if (ratio < 1.0) {
      // Недостаточно покрытия: чем меньше ratio, тем хуже
      // При ratio=0.5 -> 50, при ratio=0 -> 0
      return Math.max(0, ratio * 100);
    } else {
      // Слишком большой запас: ratio > 1.5
      // При ratio=2.0 -> 75, ratio=3.0 -> 50, ratio=5.0 -> 0
      return Math.max(0, 100 - (ratio - 1.5) * 28.5);
    }
  }

  /**
   * budgetScore: соответствие бюджету пользователя.
   * 100 если цена укладывается, 60 если немного выше, 20 если сильно выше.
   * rent = аренда, бюджет не ограничен (все получают 100).
   */
  function scoreBudget(purifier, budget) {
    const budgetLimits = { low: 3000000, mid: 6000000, high: 15000000, premium: 30000000 };

    if (budget === 'rent') return 100;

    const limit = budgetLimits[budget];
    if (!limit) return 50;

    if (purifier.price <= limit) {
      return 100;
    } else if (purifier.price <= limit * 1.3) {
      // Немного выше бюджета (до 30% сверху)
      return 60;
    } else if (purifier.price <= limit * 2.0) {
      // Заметно выше (до 2x)
      return 20;
    } else {
      // Сильно выше бюджета
      return 5;
    }
  }

  /**
   * needsScore: соответствие особым потребностям.
   * allergy -> +50 за HEPA H13 и выше
   * kids -> +50 за тихие модели / модели с тегом kids
   * smoke -> +50 за угольный фильтр (Carbon)
   * none -> базовые 50 баллов всем
   */
  function scoreNeeds(purifier, needs) {
    let score = 50; // базовый балл

    if (!needs || needs === 'none') return score;

    if (needs === 'allergy') {
      const f = purifier.filter.toLowerCase();
      if (f.includes('hepa h13') || f.includes('hepa h14') || f.includes('nanoprotect')) {
        score += 50;
      }
    }

    if (needs === 'kids') {
      if (purifier.quiet || purifier.tags.includes('kids')) {
        score += 50;
      }
    }

    if (needs === 'smoke') {
      const f = purifier.filter.toLowerCase();
      if (f.includes('carbon') || purifier.tags.includes('smoke')) {
        score += 50;
      }
    }

    if (needs === 'pets') {
      const f = purifier.filter.toLowerCase();
      if (f.includes('carbon')) {
        score += 50;
      }
    }

    if (needs === 'dust') {
      if (purifier.cadr >= 450) {
        score += 50;
      }
    }

    return score;
  }

  /**
   * typeScore: соответствие типу помещения.
   * industrial -> крупные модели (coverage >= 100) получают высший балл
   * apartment -> компактные модели (coverage <= 80) получают высший балл
   * house -> средние и крупные
   * office -> средние и крупные
   */
  function scoreType(purifier, placement) {
    const cov = purifier.coverage;
    const hasTag = purifier.tags.includes(placement);

    // Прямое совпадение тега — сильный бонус
    let score = hasTag ? 70 : 20;

    if (placement === 'industrial') {
      if (cov >= 150) score = 100;
      else if (cov >= 80) score = 40;
      else score = 10;
    } else if (placement === 'apartment') {
      if (cov <= 80) score = Math.max(score, 90);
      else score = Math.min(score, 30);
    } else if (placement === 'house') {
      if (cov >= 50 && cov <= 120) score = Math.max(score, 85);
      else if (cov > 120) score = Math.max(score, 40);
    } else if (placement === 'office') {
      if (cov >= 60) score = Math.max(score, 85);
    }

    return Math.min(100, score);
  }

  /**
   * Главная функция расчёта — все модели получают totalScore,
   * ни одна не отсеивается. Сортировка по итоговому баллу.
   */
  function calculate() {
    const { placement, area, needs, budget } = state.answers;

    const scored = PURIFIERS.map((p) => {
      const cScore = scoreCoverage(p, area);
      const bScore = scoreBudget(p, budget);
      const nScore = scoreNeeds(p, needs);
      const tScore = scoreType(p, placement);

      const totalScore = cScore * 0.35 + bScore * 0.25 + nScore * 0.25 + tScore * 0.15;
      const matchPercent = Math.round(totalScore);

      return { ...p, _score: totalScore, _match: matchPercent };
    });

    // Сортируем по убыванию скора
    scored.sort((a, b) => b._score - a._score);

    return {
      primary: scored[0],
      alternatives: scored.slice(1, 4),
    };
  }

  /* ============================================================
     БЛОК 5. Рендер результата
     ============================================================ */
  /** calculateAndRender — запускает алгоритм скоринга и рендерит HTML с результатами */
  function calculateAndRender() {
    const { primary, alternatives } = calculate();

    const placementLabels = {
      apartment: 'квартиры',
      house: 'дома',
      office: 'офиса',
      industrial: 'промышленного помещения',
    };
    const placementLabel = placementLabels[state.answers.placement] || 'помещения';

    document.getElementById('result-title').textContent = `${primary.brand} ${primary.model}`;
    document.getElementById('result-subtitle').textContent =
      `Лучший выбор для ${placementLabel} ${state.answers.area} м2`;

    const container = document.getElementById('result-main');
    container.innerHTML = `
      <article class="card recommendation">
        <div class="recommendation__grid">
          <img src="${primary.image}" alt="${primary.model}" class="recommendation__img"
               onerror="this.src='assets/images/purifiers/placeholder.svg'">
          <div class="recommendation__body">
            <div class="recommendation__match">Совпадение: ${primary._match}%</div>
            <div class="recommendation__price">${formatPrice(primary.price)} сум</div>
            <ul class="recommendation__pros">
              ${primary.pros.map((p) => `<li>${p}</li>`).join('')}
            </ul>
            <div class="recommendation__coverage">
              <b>Площадь покрытия:</b> ${primary.coverage} м2 &nbsp;|&nbsp;
              <b>CADR:</b> ${primary.cadr} м3/ч &nbsp;|&nbsp;
              <b>Фильтр:</b> ${primary.filter}
            </div>
          </div>
        </div>
      </article>

      ${alternatives.length > 0 ? `
        <h3 class="alt-title">Другие варианты:</h3>
        <div class="alternatives">
          ${alternatives.map((a) => `
            <article class="card alt">
              <img src="${a.image}" alt="${a.model}" class="alt__img"
                   onerror="this.src='assets/images/purifiers/placeholder.svg'">
              <h4>${a.brand} ${a.model}</h4>
              <div class="alt__match">Совпадение: ${a._match}%</div>
              <div class="alt__price">${formatPrice(a.price)} сум</div>
              <small>Покрытие: ${a.coverage} м2 &nbsp;|&nbsp; CADR: ${a.cadr} м3/ч</small>
            </article>
          `).join('')}
        </div>
      ` : ''}
    `;
  }

  /** formatPrice — форматирует число в удобочитаемую цену (пробелы как разделители) */
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
