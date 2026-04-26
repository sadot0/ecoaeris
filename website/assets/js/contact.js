/**
 * EcoAeris — Contact Page
 * Автор: Асад
 *
 * Уникальная JS-функция:
 *   1. Валидация формы с regex для UZ-телефона (+998 XX XXX-XX-XX)
 *   2. FAQ accordion — только один открытый блок одновременно
 */

(function () {
  'use strict';

  /* ============================================================
     БЛОК 1. Валидаторы
     Каждый возвращает '' (ок) или строку с ошибкой
     ============================================================ */
  const validators = {
    name(value) {
      if (!value || value.trim().length < 2) return 'Введите имя (минимум 2 символа)';
      return '';
    },

    phone(value) {
      // Узбекский мобильный: +998 + 9 цифр.
      // Принимаем с пробелами, скобками, дефисами — нормализуем.
      const normalized = value.replace(/[\s()\-]/g, '');
      // Regex: +998 + 9 цифр ровно
      const regex = /^\+998\d{9}$/;
      if (!normalized) return 'Введите номер телефона';
      if (!regex.test(normalized)) {
        return 'Формат: +998 XX XXX-XX-XX';
      }
      return '';
    },

    email(value) {
      if (!value) return ''; // необязательное поле
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!regex.test(value)) return 'Некорректный email';
      return '';
    },

    agree(checked) {
      if (!checked) return 'Подтвердите согласие';
      return '';
    },
  };

  /* ============================================================
     БЛОК 2. Показать ошибку под полем + shake-анимация
     ============================================================ */
  function showError(fieldName, message) {
    const errorEl = document.querySelector(`.form-error[data-for="${fieldName}"]`);
    const input = document.querySelector(`[name="${fieldName}"], #${fieldName}`);

    if (errorEl) errorEl.textContent = message;
    if (input) {
      input.classList.toggle('error', !!message);
      // Триггерим shake-анимацию через re-apply класса
      if (message) {
        input.classList.remove('shake');
        void input.offsetWidth; // trigger reflow
        input.classList.add('shake');
      }
    }
  }

  function clearErrors() {
    document.querySelectorAll('.form-error').forEach((el) => (el.textContent = ''));
    document.querySelectorAll('.contact-form input, .contact-form textarea, .contact-form select')
      .forEach((el) => el.classList.remove('error'));
  }

  /* ============================================================
     БЛОК 3. Обработка submit формы
     ============================================================ */
  function handleSubmit(e) {
    e.preventDefault();
    clearErrors();

    const form = e.target;
    const data = {
      name: form.name.value,
      phone: form.phone.value,
      email: form.email.value,
      subject: form.subject.value,
      message: form.message.value,
      agree: form.agree.checked,
    };

    // Валидация
    const errors = {
      name: validators.name(data.name),
      phone: validators.phone(data.phone),
      email: validators.email(data.email),
      agree: validators.agree(data.agree),
    };

    // Показать ошибки
    let hasError = false;
    Object.keys(errors).forEach((field) => {
      if (errors[field]) {
        showError(field, errors[field]);
        hasError = true;
      }
    });

    if (hasError) return;

    // В реальном проекте тут fetch('/api/contact', { method: 'POST', body: ... })
    // Для MVP — просто показываем успех + даём ссылку на бот
    const feedback = document.getElementById('form-feedback');
    feedback.className = 'form-feedback form-feedback--success';
    feedback.innerHTML = `
      ✅ <b>Заявка отправлена!</b><br>
      Мы позвоним на ${data.phone} в течение 30 минут.<br>
      Для ускорения — напишите нам в
      <a href="https://t.me/EcoAeris_team_bot?start=contact_${Date.now()}" target="_blank">Telegram</a>.
    `;

    form.reset();
  }

  /* ============================================================
     БЛОК 4. FAQ Accordion
     Логика: клик открывает/закрывает, при открытии закрываем остальные
     ============================================================ */
  function initAccordion() {
    const items = document.querySelectorAll('.faq-item');

    items.forEach((item) => {
      const head = item.querySelector('.faq-item__head');
      const body = item.querySelector('.faq-item__body');

      head.addEventListener('click', () => {
        const isOpen = item.classList.contains('open');

        // Закрываем все
        items.forEach((i) => {
          i.classList.remove('open');
          i.querySelector('.faq-item__head').setAttribute('aria-expanded', 'false');
          i.querySelector('.faq-item__body').style.maxHeight = '0';
          i.querySelector('.faq-item__icon').textContent = '+';
        });

        // Если был закрыт — открываем
        if (!isOpen) {
          item.classList.add('open');
          head.setAttribute('aria-expanded', 'true');
          body.style.maxHeight = body.scrollHeight + 'px';
          item.querySelector('.faq-item__icon').textContent = '−';
        }
      });
    });
  }

  /* ============================================================
     БЛОК 5. Маска ввода телефона (опционально — улучшает UX)
     ============================================================ */
  function initPhoneMask() {
    const phone = document.getElementById('phone');
    if (!phone) return;

    phone.addEventListener('input', (e) => {
      let value = e.target.value.replace(/\D/g, '');
      if (!value.startsWith('998')) value = '998' + value;
      value = value.slice(0, 12); // +998 + 9 цифр

      let formatted = '+998';
      if (value.length > 3) formatted += ' ' + value.slice(3, 5);
      if (value.length > 5) formatted += ' ' + value.slice(5, 8);
      if (value.length > 8) formatted += '-' + value.slice(8, 10);
      if (value.length > 10) formatted += '-' + value.slice(10, 12);

      e.target.value = formatted;
    });
  }

  /* ============================================================
     БЛОК 6. Запуск
     ============================================================ */
  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contact-form');
    if (form) form.addEventListener('submit', handleSubmit);

    initAccordion();
    initPhoneMask();
  });
})();
