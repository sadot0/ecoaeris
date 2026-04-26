/**
 * EcoAeris — Home Page JS
 * Файл: home.js
 * Страница: index.html (Главная)
 * Автор: Арсений
 *
 * JS-функция: Live AQI виджет — загружает данные о качестве воздуха
 * в Ташкенте через WAQI API и отображает их в hero-секции.
 * Обновление каждые 10 минут. Карта — iframe WAQI (тепловая карта встроена в HTML).
 */

/*
 * Заметки разработчика (Арсений):
 *
 * Я отвечал за главную страницу и общую архитектуру проекта.
 * Главная задача — показать пользователю AQI Ташкента в реальном времени.
 * Использую WAQI API (aqicn.org) для получения данных.
 *
 * Что было сложно:
 * - WAQI API с demo-токеном часто возвращает ошибки, поэтому добавил fallback
 * - Карту сначала делал на Leaflet, но потом перешёл на iframe WAQI —
 *   тепловая карта выглядит намного лучше и показывает реальные данные
 * - setInterval каждые 10 минут обновляет виджет без перезагрузки страницы
 *
 * Что я узнал: async/await + fetch API, работа с внешними API, обработка ошибок
 */

(function () {
  'use strict';

  /**
   * loadHeroWidget — загружает данные AQI для Ташкента через API
   * и рендерит виджет в hero-секции. При ошибке API использует fallback-значения.
   */
  async function loadHeroWidget() {
    const w = document.getElementById('hero-aqi-widget');
    if (!w) return;

    let aqi, pm25, pm10, temp, hum;
    try {
      const d = await AirQualityAPI.getCityAQI('tashkent');
      aqi = d.aqi; pm25 = d.pm25; pm10 = d.pm10;
      temp = d.temperature; hum = d.humidity;
    } catch (e) {
      aqi = 156; pm25 = 65; pm10 = 78; temp = null; hum = null;
    }

    const c = AirQualityAPI.categorize(aqi);
    w.innerHTML = `
      <div class="aqi-widget__inner" style="--aqi-color:${c.color}">
        <span class="aqi-widget__label">Ташкент сейчас</span>
        <div class="aqi-widget__number">${aqi}</div>
        <span class="aqi-widget__category">${c.label}</span>
        <div class="aqi-widget__meta">
          <div>PM2.5: <b>${pm25 ?? '—'}</b> · PM10: <b>${pm10 ?? '—'}</b> µg/m³</div>
          ${temp != null ? `<div>🌡 ${temp}°C · 💧 ${hum}%</div>` : ''}
        </div>
      </div>`;
  }

  // При загрузке страницы вызываем виджет и ставим автообновление каждые 10 минут
  document.addEventListener('DOMContentLoaded', () => {
    loadHeroWidget();
    setInterval(loadHeroWidget, 10 * 60 * 1000); // обновление каждые 10 мин
  });
})();
