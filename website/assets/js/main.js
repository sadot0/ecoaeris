/**
 * EcoAeris — Main JS
 * Файл: main.js
 * Тип: общий командный файл (подключён на всех 6 страницах)
 * Авторы: команда EcoAeris (Арсений, Муслима, Самира, Эмран, Мухаммад, Асад)
 *
 * Описание: общая логика, которая работает на всех страницах сайта:
 * - Мобильное меню (открытие/закрытие по клику на .nav-toggle)
 * - Подсветка активной ссылки в навигации (сравнение href с текущим URL)
 * - Автоматическое обновление года в футере (#footer-year)
 */

/*
 * Заметки команды:
 *
 * Общий JS для всех 6 страниц. Подключён везде.
 * - Мобильное меню: открытие/закрытие + закрытие при клике на ссылку
 * - Год в футере обновляется автоматически
 *
 * Договорились: каждый подключает main.js + свой page.js.
 * Порядок: api.js (если нужен) → main.js → page.js
 */

(function () {
  'use strict';

  /* --- Мобильное меню ---
     Находим кнопку-гамбургер (.nav-toggle) и навигацию (.nav).
     По клику переключаем класс 'open' для показа/скрытия меню. */
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');

  if (toggle && nav) {
    // Обработчик клика: toggle класс 'open' у навигации
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }

  /* --- Закрытие мобильного меню при клике на ссылку --- */
  document.querySelectorAll('.nav__link').forEach((link) => {
    link.addEventListener('click', () => { if (nav) nav.classList.remove('open'); });
  });

  /* --- Год в футере ---
     Автоматически подставляем текущий год в элемент #footer-year,
     чтобы не обновлять вручную каждый январь. */
  const yearSpan = document.getElementById('footer-year');
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
})();
