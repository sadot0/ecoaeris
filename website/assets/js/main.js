/**
 * EcoAeris — Main JS
 * Логика которая работает на всех страницах:
 * - Мобильное меню (открытие/закрытие)
 * - Подсветка активной ссылки в навигации
 * - Обновление года в футере
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
