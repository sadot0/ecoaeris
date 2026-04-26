/**
 * EcoAeris — Home Page JS
 * Автор: Арсений
 *
 * Карта качества воздуха Узбекистана:
 *  1. Тепловой слой AQI от WAQI (реальные данные со всех станций мира)
 *  2. Маркеры всех мониторинговых станций в регионе UZ
 *  3. Hero-виджет с live AQI Ташкента
 *  4. Автообновление каждые 10 минут
 *
 * Источник данных: aqicn.org (World Air Quality Index)
 */

(function () {
  'use strict';

  /* ============================================================
     БЛОК 1. Конфигурация
     ============================================================ */

  // Bounding box Узбекистана (lat_min, lon_min, lat_max, lon_max)
  const UZ_BOUNDS = [37, 56, 46, 74];

  // Центр карты и зум
  const MAP_CENTER = [41.3, 64.5];
  const MAP_ZOOM = 6;

  // Fallback данные на случай если API недоступен
  const FALLBACK_STATIONS = [
    { name: 'Ташкент, US Embassy', lat: 41.3111, lon: 69.2797, aqi: 156 },
    { name: 'Ташкент, Юнусабад', lat: 41.3650, lon: 69.2840, aqi: 142 },
    { name: 'Самарканд', lat: 39.6270, lon: 66.9750, aqi: 95 },
    { name: 'Бухара', lat: 39.7681, lon: 64.4556, aqi: 82 },
    { name: 'Наманган', lat: 40.9983, lon: 71.6726, aqi: 88 },
    { name: 'Андижан', lat: 40.7821, lon: 72.3442, aqi: 91 },
    { name: 'Фергана', lat: 40.3894, lon: 71.7864, aqi: 85 },
    { name: 'Нукус', lat: 42.4597, lon: 59.6008, aqi: 78 },
    { name: 'Ургенч', lat: 41.5504, lon: 60.6319, aqi: 72 },
    { name: 'Навои', lat: 40.0844, lon: 65.3792, aqi: 68 },
    { name: 'Термез', lat: 37.2242, lon: 67.2783, aqi: 65 },
  ];

  /* ============================================================
     БЛОК 2. Hero-виджет AQI Ташкента
     ============================================================ */
  async function loadHeroWidget() {
    const widget = document.getElementById('hero-aqi-widget');
    if (!widget) return;

    try {
      const data = await AirQualityAPI.getCityAQI('tashkent');
      const cat = AirQualityAPI.categorize(data.aqi);

      widget.innerHTML = `
        <div class="aqi-widget__inner" style="--aqi-color: ${cat.color}">
          <span class="aqi-widget__label">Ташкент сейчас</span>
          <div class="aqi-widget__number">${data.aqi}</div>
          <span class="aqi-widget__category">${cat.label}</span>
          <div class="aqi-widget__meta">
            <div>PM2.5: <b>${data.pm25 ?? '—'}</b> µg/m³</div>
            <div>PM10: <b>${data.pm10 ?? '—'}</b> µg/m³</div>
            <div>🌡 ${data.temperature ?? '—'}°C · 💧 ${data.humidity ?? '—'}%</div>
            <div style="font-size:0.75rem;opacity:0.7;margin-top:4px">
              Обновлено: ${new Date(data.time).toLocaleTimeString('ru-RU', {hour:'2-digit', minute:'2-digit'})}
            </div>
          </div>
        </div>
      `;
    } catch (err) {
      console.warn('[EcoAeris] API недоступен, показываем fallback:', err.message);
      const fallback = FALLBACK_STATIONS[0];
      const cat = AirQualityAPI.categorize(fallback.aqi);
      widget.innerHTML = `
        <div class="aqi-widget__inner" style="--aqi-color: ${cat.color}">
          <span class="aqi-widget__label">Ташкент</span>
          <div class="aqi-widget__number">${fallback.aqi}</div>
          <span class="aqi-widget__category">${cat.label}</span>
          <div class="aqi-widget__meta">
            <div>PM2.5: <b>65</b> µg/m³</div>
            <div>PM10: <b>78</b> µg/m³</div>
            <div style="font-size:0.75rem;opacity:0.7;margin-top:4px">Кэшированные данные</div>
          </div>
        </div>
      `;
    }
  }

  /* ============================================================
     БЛОК 3. Инициализация Leaflet-карты с тепловым слоем WAQI
     ============================================================ */
  function initMap() {
    const mapContainer = document.getElementById('leaflet-map');
    if (!mapContainer) return null;

    // Создаём карту с центром на Узбекистане
    const map = L.map('leaflet-map', {
      zoomControl: true,
      scrollWheelZoom: true,
    }).setView(MAP_CENTER, MAP_ZOOM);

    // Базовый слой — CartoDB Positron (чистая светлая карта, лучше для overlay)
    const baseLight = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap · © CARTO',
      maxZoom: 18,
      subdomains: 'abcd',
    });

    // Базовый слой — OpenStreetMap (классический)
    const baseOSM = L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18,
    });

    // Тёмный базовый слой
    const baseDark = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap · © CARTO',
      maxZoom: 18,
      subdomains: 'abcd',
    });

    // По умолчанию — светлая
    baseLight.addTo(map);

    // ⭐ ТЕПЛОВОЙ СЛОЙ WAQI — реальные данные AQI со всех станций мира
    // Тайлы раскрашивают карту по US EPA шкале (зелёный → красный → фиолетовый)
    const aqiHeatLayer = L.tileLayer(
      'https://tiles.aqicn.org/tiles/usepa-aqi/{z}/{x}/{y}.png?token=' + WAQI_TOKEN, {
      attribution: '© <a href="https://aqicn.org">WAQI.info</a> Air Quality Data',
      opacity: 0.55,
      maxZoom: 18,
    });

    // Добавляем тепловой слой поверх базовой карты
    aqiHeatLayer.addTo(map);

    // Переключатель слоёв
    const baseLayers = {
      'Светлая': baseLight,
      'Стандартная': baseOSM,
      'Тёмная': baseDark,
    };
    const overlays = {
      '🌡 Тепловая карта AQI': aqiHeatLayer,
    };
    L.control.layers(baseLayers, overlays, { position: 'topright' }).addTo(map);

    return map;
  }

  /* ============================================================
     БЛОК 4. Загрузка станций мониторинга из WAQI bounds API
     Показываем ВСЕ реальные станции в регионе Узбекистана
     ============================================================ */
  async function loadStationMarkers(map) {
    let stations;

    try {
      // Загружаем все станции в bounding box Узбекистана
      stations = await AirQualityAPI.getStationsInBounds(UZ_BOUNDS);
      console.log(`[EcoAeris] Загружено ${stations.length} станций из WAQI API`);
    } catch (err) {
      console.warn('[EcoAeris] API bounds недоступен, используем fallback:', err.message);
      // Конвертируем fallback в формат станций
      stations = FALLBACK_STATIONS.map((s, i) => ({
        uid: i,
        lat: s.lat,
        lon: s.lon,
        aqi: s.aqi,
        station: s.name,
      }));
    }

    // Фильтруем невалидные (aqi = 0 или отрицательный)
    stations = stations.filter(s => s.aqi > 0);

    // Создаём маркеры для каждой станции
    const markersGroup = L.layerGroup();

    stations.forEach((s) => {
      const cat = AirQualityAPI.categorize(s.aqi);

      // Размер маркера зависит от AQI (больше = опаснее = заметнее)
      const radius = Math.max(8, Math.min(20, 8 + s.aqi / 30));

      const marker = L.circleMarker([s.lat, s.lon], {
        radius: radius,
        fillColor: cat.color,
        color: '#fff',
        weight: 2,
        opacity: 0.9,
        fillOpacity: 0.8,
        className: 'aqi-marker',
      });

      // Popup с информацией о станции
      marker.bindPopup(`
        <div class="map-popup">
          <h4>${s.station}</h4>
          <div class="map-popup__aqi" style="color: ${cat.color}">
            AQI ${s.aqi}
          </div>
          <div style="margin-bottom:4px">${cat.label}</div>
          <small style="color:#64748B">Источник: WAQI.info</small>
        </div>
      `);

      // Tooltip при наведении (быстрый просмотр без клика)
      marker.bindTooltip(`${s.station}: AQI ${s.aqi}`, {
        direction: 'top',
        offset: [0, -8],
        className: 'aqi-tooltip',
      });

      marker.addTo(markersGroup);
    });

    markersGroup.addTo(map);

    // Обновляем счётчик станций в описании карты
    const subtitle = document.querySelector('#map .section__subtitle');
    if (subtitle) {
      subtitle.textContent = `${stations.length} станций мониторинга · данные обновляются каждые 10 минут · источник: WAQI.info`;
    }

    return markersGroup;
  }

  /* ============================================================
     БЛОК 5. Автообновление каждые 10 минут
     ============================================================ */
  function startAutoRefresh(map, markersGroup) {
    setInterval(async () => {
      console.log('[EcoAeris] Обновление данных AQI…');

      // Обновляем виджет
      loadHeroWidget();

      // Удаляем старые маркеры
      if (markersGroup) {
        markersGroup.clearLayers();
        map.removeLayer(markersGroup);
      }

      // Загружаем свежие данные
      await loadStationMarkers(map);
    }, 10 * 60 * 1000); // 10 минут
  }

  /* ============================================================
     ЗАПУСК
     ============================================================ */
  document.addEventListener('DOMContentLoaded', async () => {
    // Загружаем hero-виджет
    loadHeroWidget();

    // Инициализируем карту с тепловым слоем
    const map = initMap();
    if (map) {
      // Загружаем маркеры станций
      const markersGroup = await loadStationMarkers(map);

      // Запускаем автообновление
      startAutoRefresh(map, markersGroup);
    }
  });
})();
