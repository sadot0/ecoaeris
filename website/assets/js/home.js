/**
 * EcoAeris — Home Page JS
 * Автор: Арсений
 *
 * Карта качества воздуха: тепловой слой WAQI + маркеры станций
 */

(function () {
  'use strict';

  /* ============================================================
     Конфигурация
     ============================================================ */
  const UZ_BOUNDS = [37, 56, 46, 74];
  const MAP_CENTER = [41.3, 64.5];
  const MAP_ZOOM = 6;

  const FALLBACK = [
    { station: 'Tashkent, US Embassy', lat: 41.311, lon: 69.279, aqi: 156 },
    { station: 'Tashkent, Yunusabad', lat: 41.365, lon: 69.284, aqi: 142 },
    { station: 'Samarkand', lat: 39.627, lon: 66.975, aqi: 95 },
    { station: 'Bukhara', lat: 39.768, lon: 64.455, aqi: 82 },
    { station: 'Namangan', lat: 40.998, lon: 71.672, aqi: 88 },
    { station: 'Andijan', lat: 40.782, lon: 72.344, aqi: 91 },
    { station: 'Fergana', lat: 40.389, lon: 71.786, aqi: 85 },
    { station: 'Nukus', lat: 42.459, lon: 59.600, aqi: 78 },
    { station: 'Urgench', lat: 41.550, lon: 60.631, aqi: 72 },
    { station: 'Navoi', lat: 40.084, lon: 65.379, aqi: 68 },
  ];

  /* ============================================================
     Hero-виджет
     ============================================================ */
  async function loadHeroWidget() {
    const w = document.getElementById('hero-aqi-widget');
    if (!w) return;

    let aqi, pm25, pm10, temp, hum, time;
    try {
      const d = await AirQualityAPI.getCityAQI('tashkent');
      aqi = d.aqi; pm25 = d.pm25; pm10 = d.pm10;
      temp = d.temperature; hum = d.humidity; time = d.time;
    } catch (e) {
      aqi = 156; pm25 = 65; pm10 = 78; temp = null; hum = null; time = null;
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

  /* ============================================================
     Карта
     ============================================================ */
  function initMap() {
    const el = document.getElementById('leaflet-map');
    if (!el) return null;

    const map = L.map('leaflet-map', {
      center: MAP_CENTER,
      zoom: MAP_ZOOM,
      zoomControl: true,
    });

    // Базовая карта — светлая, чистая
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap · CARTO',
      maxZoom: 18,
      subdomains: 'abcd',
    }).addTo(map);

    // Тепловой слой AQI — реальные данные загрязнения со всего мира
    L.tileLayer('https://tiles.aqicn.org/tiles/usepa-aqi/{z}/{x}/{y}.png?token=' + WAQI_TOKEN, {
      attribution: '© <a href="https://aqicn.org">WAQI</a>',
      opacity: 0.75,
      maxZoom: 18,
    }).addTo(map);

    return map;
  }

  /* ============================================================
     Маркеры станций (без шариков — только тепловая карта)
     Загружаем данные для подписи
     ============================================================ */
  async function loadStationCount(map) {
    try {
      const stations = await AirQualityAPI.getStationsInBounds(UZ_BOUNDS);
      const sub = document.querySelector('#map .section__subtitle');
      if (sub) sub.textContent = `${stations.length} станций · обновление каждые 10 мин · источник: WAQI.info`;
    } catch (e) {
      // тихо — тепловая карта и так показывает данные
    }
  }

  /* ============================================================
     Автообновление
     ============================================================ */
  /* ============================================================
     Запуск
     ============================================================ */
  document.addEventListener('DOMContentLoaded', async () => {
    loadHeroWidget();
    const map = initMap();
    if (map) loadStationCount(map);

    // Обновление виджета каждые 10 мин
    setInterval(() => loadHeroWidget(), 10 * 60 * 1000);
  });
})();
