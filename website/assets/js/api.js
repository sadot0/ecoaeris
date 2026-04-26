/**
 * EcoAeris API Client
 * Файл: api.js
 * Тип: общий командный файл (используется на всех страницах)
 * Авторы: команда EcoAeris (Арсений, Муслима, Самира, Эмран, Мухаммад, Асад)
 *
 * Описание: обёртка над WAQI API для получения данных качества воздуха.
 * Предоставляет методы getCityAQI, getStationsInBounds и categorize,
 * которые используются другими модулями (home.js, pricing.js и др.).
 *
 * Использование:
 *   const data = await AirQualityAPI.getCityAQI('tashkent');
 *   console.log(data.aqi);  // 156
 */

/*
 * Заметки команды:
 *
 * Этот файл — общий API-клиент для всего проекта.
 * Написан Арсением (тимлид), используется на главной странице.
 *
 * WAQI API (aqicn.org) — бесплатный, до 1000 запросов/сек.
 * Токен 'demo' — ограниченный, для продакшна нужен свой.
 * Получить: https://aqicn.org/data-platform/token/
 *
 * Функции:
 * - getCityAQI(city) — AQI по городу с retry
 * - getStationsInBounds(bbox) — все станции в регионе
 * - categorize(aqi) — уровень по шкале US EPA
 */

// Временный публичный демо-токен WAQI. На продакшне замените на свой!
// Получить токен: https://aqicn.org/data-platform/token/
const WAQI_TOKEN = 'demo';  // TODO: заменить на рабочий токен

/**
 * Объект AirQualityAPI — содержит все методы для работы с WAQI API.
 * Глобально доступен через window.AirQualityAPI.
 */
const AirQualityAPI = {
  /**
   * Получить AQI по названию города.
   * @param {string} city — slug города (например "tashkent")
   * @returns {Promise<Object>} объект с aqi, pm25, pm10, time, city
   */
  async getCityAQI(city, retries = 2) {
    const url = `https://api.waqi.info/feed/${city}/?token=${WAQI_TOKEN}`;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url);
        const json = await response.json();

        if (json.status !== 'ok') {
          throw new Error(`WAQI error for ${city}: ${json.data}`);
        }

        // Нормализуем ответ — вытаскиваем то что нам надо
        return {
          aqi: json.data.aqi,
          city: json.data.city.name,
          pm25: json.data.iaqi.pm25?.v ?? null,
          pm10: json.data.iaqi.pm10?.v ?? null,
          temperature: json.data.iaqi.t?.v ?? null,
          humidity: json.data.iaqi.h?.v ?? null,
          time: json.data.time.iso,
        };
      } catch (err) {
        if (attempt < retries) {
          // Wait before retrying (exponential backoff: 1s, 2s)
          await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
          // silently retry
        } else {
          throw err;
        }
      }
    }
  },

  /**
   * Получить все станции в bounding box (для карты).
   * @param {Array} bbox — [latMin, lonMin, latMax, lonMax]
   */
  async getStationsInBounds(bbox) {
    const [latMin, lonMin, latMax, lonMax] = bbox;
    const url = `https://api.waqi.info/map/bounds/?latlng=${latMin},${lonMin},${latMax},${lonMax}&token=${WAQI_TOKEN}`;
    const response = await fetch(url);
    const json = await response.json();

    if (json.status !== 'ok') {
      throw new Error('WAQI bounds error');
    }

    return json.data.map((s) => ({
      uid: s.uid,
      lat: s.lat,
      lon: s.lon,
      aqi: parseInt(s.aqi) || 0,
      station: s.station.name,
    }));
  },

  /**
   * Определить категорию AQI по значению (US EPA scale).
   * Возвращает объект { level, label, color } для UI.
   */
  categorize(aqi) {
    if (aqi <= 50) return { level: 'good', label: 'Хороший', color: '#00E400' };
    if (aqi <= 100) return { level: 'moderate', label: 'Умеренный', color: '#FFFF00' };
    if (aqi <= 150) return { level: 'usg', label: 'Вредный для уязвимых', color: '#FF7E00' };
    if (aqi <= 200) return { level: 'unhealthy', label: 'Вредный', color: '#FF0000' };
    if (aqi <= 300) return { level: 'very-unhealthy', label: 'Очень вредный', color: '#8F3F97' };
    return { level: 'hazardous', label: 'Опасный', color: '#7E0023' };
  },
};

// Делаем объект доступным глобально, чтобы другие скрипты (home.js, pricing.js)
// могли вызывать AirQualityAPI.getCityAQI() и AirQualityAPI.categorize()
window.AirQualityAPI = AirQualityAPI;
