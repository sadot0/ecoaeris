/**
 * EcoAeris — About Page JS
 * Файл: about.js
 * Страница: about.html (О нас)
 * Автор: Эмран
 *
 * JS-функция: i18n переключатель языков (RU / UZ / EN) через data-i18n
 * атрибуты + переключатель тёмной/светлой темы через [data-theme] на <html>.
 * Оба параметра сохраняются в LocalStorage.
 */

/*
 * Заметки разработчика (Эмран):
 *
 * Моя задача — переключатель языков (RU/UZ/EN) и тёмная тема.
 *
 * Как работает i18n:
 * - Каждый переводимый элемент имеет атрибут data-i18n="ключ"
 * - При клике на кнопку языка, функция applyLanguage() проходит по всем
 *   элементам с data-i18n и подставляет перевод из i18n.json
 * - Выбор сохраняется в localStorage — при следующем заходе язык тот же
 *
 * Тёмная тема:
 * - Работает через атрибут data-theme="dark" на <html>
 * - CSS-переменные в base.css автоматически меняются
 * - Тоже сохраняется в localStorage
 *
 * Что было сложно:
 * - Узбекский перевод: машинный перевод неточный, проверял через друзей
 * - textContent затирает вложенные теги — пока обошёл, не кладу теги в data-i18n
 *
 * Что я узнал: работа с JSON, DOM-атрибуты, localStorage, CSS custom properties
 */

(function () {
  'use strict';

  let translations = null;  // загрузится из i18n.json
  const LANG_KEY = 'ecoaeris_lang';
  const THEME_KEY = 'ecoaeris_theme';

  /* ============================================================
     БЛОК 1. Загрузка переводов
     ============================================================ */
  /** loadTranslations — загружает JSON-файл с переводами для трёх языков */
  async function loadTranslations() {
    try {
      const resp = await fetch('assets/data/i18n.json');
      translations = await resp.json();
    } catch (err) {
      translations = { ru: {}, uz: {}, en: {} };
    }
  }

  /* ============================================================
     БЛОК 2. Применить язык ко всем элементам с data-i18n
     ============================================================ */
  /** applyLanguage — применяет выбранный язык ко всем элементам с data-i18n */
  function applyLanguage(lang) {
    if (!translations || !translations[lang]) return;

    document.documentElement.setAttribute('lang', lang);
    localStorage.setItem(LANG_KEY, lang);

    // Обновляем текст всех элементов с data-i18n="ключ"
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.dataset.i18n;
      const value = translations[lang][key];
      if (value) {
        el.textContent = value;
      }
    });

    // Подсвечиваем активную кнопку
    document.querySelectorAll('.lang-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
  }

  /* ============================================================
     БЛОК 3. Переключатель темы
     Работает через атрибут [data-theme] на <html>.
     CSS-переменные в base.css переопределяются для dark-темы.
     ============================================================ */
  /** applyTheme — устанавливает тему (light/dark) через атрибут data-theme на html */
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);

    const icon = document.querySelector('.theme-toggle__icon');
    if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
  }

  /** toggleTheme — переключает тему между light и dark */
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    applyTheme(current === 'light' ? 'dark' : 'light');
  }

  /* ============================================================
     БЛОК 4. Инициализация
     ============================================================ */
  document.addEventListener('DOMContentLoaded', async () => {
    await loadTranslations();

    // Восстанавливаем сохранённый язык и тему или используем дефолт
    const savedLang = localStorage.getItem(LANG_KEY) || 'ru';
    const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
    applyLanguage(savedLang);
    applyTheme(savedTheme);

    // Кнопки языка
    document.querySelectorAll('.lang-btn').forEach((btn) => {
      btn.addEventListener('click', () => applyLanguage(btn.dataset.lang));
    });

    // Переключатель темы
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
  });
})();
