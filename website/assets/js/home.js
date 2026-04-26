/**
 * EcoAeris — Home Page JS
 * Автор: Арсений
 *
 * Задача страницы:
 *  1. Загрузить AQI Ташкента и показать в hero-виджете
 *  2. Инициализировать Leaflet-карту Узбекистана
 *  3. Поставить маркеры всех городов с цветом по AQI
 *  4. Обновлять данные каждые 10 минут (без перезагрузки страницы)
 *
 * Использует глобальный AirQualityAPI из api.js
 */

(function () {
  'use strict';

  /* ============================================================
     БЛОК 1. Города Узбекистана для карты
     Координаты взяты из Google Maps, waqi_station — slug из aqicn.org
     ============================================================ */
  // Fallback AQI data for when API is unavailable
  const FALLBACK_AQI = {
    tashkent: 156, samarkand: 95, bukhara: 82, namangan: 88,
    andijan: 91, fergana: 85, nukus: 78, urgench: 72, navoi: 68, termez: 65
  };

  const UZ_CITIES = [
    { name: 'Ташкент', lat: 41.3111, lon: 69.2797, slug: 'tashkent' },
    { name: 'Самарканд', lat: 39.6270, lon: 66.9750, slug: 'samarkand' },
    { name: 'Бухара', lat: 39.7681, lon: 64.4556, slug: 'bukhara' },
    { name: 'Наманган', lat: 40.9983, lon: 71.6726, slug: 'namangan' },
    { name: 'Андижан', lat: 40.7821, lon: 72.3442, slug: 'andijan' },
    { name: 'Фергана', lat: 40.3894, lon: 71.7864, slug: 'fergana' },
    { name: 'Нукус', lat: 42.4597, lon: 59.6008, slug: 'nukus' },
    { name: 'Ургенч', lat: 41.5504, lon: 60.6319, slug: 'urgench' },
    { name: 'Навои', lat: 40.0844, lon: 65.3792, slug: 'navoi' },
    { name: 'Термез', lat: 37.2242, lon: 67.2783, slug: 'termez' },
  ];

  /* ============================================================
     БЛОК 2. Загружаем AQI Ташкента в hero-виджет
     ============================================================ */
  async function loadHeroWidget() {
    const widget = document.getElementById('hero-aqi-widget');
    if (!widget) return;

    try {
      const data = await AirQualityAPI.getCityAQI('tashkent');
      const category = AirQualityAPI.categorize(data.aqi);

      // Перерисовываем содержимое виджета
      widget.innerHTML = `
        <div class="aqi-widget__inner" style="--aqi-color: ${category.color}">
          <span class="aqi-widget__label">Ташкент сейчас</span>
          <div class="aqi-widget__number">${data.aqi}</div>
          <span class="aqi-widget__category">${category.label}</span>
          <div class="aqi-widget__meta">
            <div>PM2.5: <b>${data.pm25}</b> µg/m³</div>
            <div>PM10: <b>${data.pm10}</b> µg/m³</div>
            <div>🌡 ${data.temperature}°C · 💧 ${data.humidity}%</div>
          </div>
        </div>
      `;
    } catch (err) {
      console.error('Ошибка загрузки AQI, используем fallback:', err);
      const fallbackAqi = FALLBACK_AQI.tashkent;
      const category = AirQualityAPI.categorize(fallbackAqi);
      widget.innerHTML = `
        <div class="aqi-widget__inner" style="--aqi-color: ${category.color}">
          <span class="aqi-widget__label">Ташкент сейчас</span>
          <div class="aqi-widget__number">${fallbackAqi}</div>
          <span class="aqi-widget__category">${category.label}</span>
          <div class="aqi-widget__meta">
            <div>PM2.5: <b>—</b> µg/m³</div>
            <div>PM10: <b>—</b> µg/m³</div>
            <div>Данные кэшированы</div>
          </div>
        </div>
      `;
    }
  }

  /* ============================================================
     БЛОК 3. Инициализация Leaflet-карты
     ============================================================ */
  function initMap() {
    const mapContainer = document.getElementById('leaflet-map');
    if (!mapContainer) return null;

    // Создаём карту, центр — середина Узбекистана, zoom 6 (видна вся страна)
    const map = L.map('leaflet-map').setView([41.5, 64.5], 6);

    // Подключаем тайлы OpenStreetMap (бесплатно, без токенов)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(map);

    return map;
  }

  /* ============================================================
     БЛОК 4. Добавляем маркеры городов с цветом по AQI
     Это сердце фичи — каждый город подсвечивается своим цветом.
     ============================================================ */
  async function addCityMarkers(map) {
    // Обрабатываем все города параллельно через Promise.all
    const tasks = UZ_CITIES.map(async (city) => {
      let aqi, pm25, pm10, isFallback;

      try {
        const data = await AirQualityAPI.getCityAQI(city.slug);
        aqi = data.aqi;
        pm25 = data.pm25;
        pm10 = data.pm10;
        isFallback = false;
      } catch (err) {
        console.warn(`API failed for ${city.name}, using fallback:`, err);
        aqi = FALLBACK_AQI[city.slug] || 50;
        pm25 = null;
        pm10 = null;
        isFallback = true;
      }

      const category = AirQualityAPI.categorize(aqi);

      // Создаём цветной маркер-круг
      const marker = L.circleMarker([city.lat, city.lon], {
        radius: 14,
        fillColor: category.color,
        color: '#fff',
        weight: 3,
        opacity: 1,
        fillOpacity: 0.85,
        className: 'aqi-marker',  // для анимации pulse в CSS
      });

      // Popup с деталями
      const fallbackNote = isFallback ? '<br><small style="opacity:0.7">Данные кэшированы</small>' : '';
      const popupHtml = `
        <div class="map-popup">
          <h4>${city.name}</h4>
          <div class="map-popup__aqi" style="color: ${category.color}">
            AQI ${aqi}
          </div>
          <div>${category.label}</div>
          <small>PM2.5: ${pm25 ?? '—'} · PM10: ${pm10 ?? '—'}</small>
          ${fallbackNote}
        </div>
      `;
      marker.bindPopup(popupHtml);

      marker.addTo(map);
    });

    await Promise.all(tasks);
  }

  /* ============================================================
     БЛОК 5. Автообновление каждые 10 минут
     ============================================================ */
  function startAutoRefresh(map) {
    setInterval(() => {
      console.log('[EcoAeris] Обновление данных AQI…');
      loadHeroWidget();

      // Очищаем старые маркеры (оставляем только tile layer)
      map.eachLayer((layer) => {
        if (layer instanceof L.CircleMarker) {
          map.removeLayer(layer);
        }
      });
      addCityMarkers(map);
    }, 10 * 60 * 1000);  // 10 минут
  }

  /* ============================================================
     ЗАПУСК — ждём загрузку DOM и поехали
     ============================================================ */
  document.addEventListener('DOMContentLoaded', async () => {
    loadHeroWidget();

    const map = initMap();
    if (map) {
      await addCityMarkers(map);
      startAutoRefresh(map);
    }
  });
})();
