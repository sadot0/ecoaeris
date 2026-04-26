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

(function () {
  'use strict';

  /* --- Мобильное меню --- */
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }

  /* --- Активная ссылка в меню --- */
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav__link').forEach((link) => {
    const href = link.getAttribute('href');
    if (href === currentPage) {
      link.classList.add('active');
    }
  });

  /* --- Год в футере --- */
  const yearSpan = document.getElementById('footer-year');
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
})();
