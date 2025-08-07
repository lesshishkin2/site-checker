# Site Checker - AI Agent для проверки фишинговых сайтов

## Описание проекта

AI агент для автоматической проверки веб-сайтов на предмет фишинга и мошенничества. Агент анализирует содержимое сайта, делает скриншоты и использует интернет-поиск для выявления подозрительной активности.

## Архитектура проекта

```
site_checker/
├── src/
│   ├── agents/           # Основные агенты
│   ├── core/            # Базовая логика
│   ├── models/          # Модели данных
│   ├── services/        # Сервисы (скриншоты, поиск, анализ)
│   └── utils/           # Утилиты
├── tests/               # Тесты
├── docs/                # Документация  
└── config/              # Конфигурационные файлы
```

## Технический стек

- **Python 3.11+**
- **OpenAI Agents SDK** - основной фреймворк для создания агентов
- **Playwright/Selenium** - для получения скриншотов и контента сайтов
- **OpenAI GPT-4** - для анализа содержимого
- **Requests/aiohttp** - для веб-запросов
- **Google Search API** или аналог - для интернет-поиска

## Основные компоненты

### 1. Web Content Fetcher
- Получение HTML содержимого сайта
- Создание скриншотов
- Извлечение метаданных

### 2. Content Analyzer Agent
- Анализ текстового содержимого
- Поиск подозрительных паттернов
- Определение типа сайта

### 3. Visual Analyzer Agent  
- Анализ скриншотов сайта
- Поиск визуальных признаков фишинга
- Сравнение с известными брендами

### 4. Web Search Agent
- Поиск информации о домене
- Проверка репутации сайта
- Поиск жалоб и отзывов

### 5. Risk Assessment Agent
- Объединение результатов анализа
- Расчет итогового скора (0-10)
- Формирование структурированного отчета

## Выходной формат

```json
{
  "url": "https://example.com",
  "risk_score": 7.5,
  "analysis_timestamp": "2024-01-01T12:00:00Z",
  "findings": {
    "content_analysis": {
      "suspicious_keywords": ["urgent", "limited time"],
      "fake_login_forms": true,
      "ssl_issues": false
    },
    "visual_analysis": {
      "brand_impersonation": "PayPal",
      "suspicious_elements": ["fake logos", "poor quality graphics"]
    },
    "reputation_check": {
      "domain_age": "2 days",
      "previous_reports": 5,
      "blacklist_status": "listed"
    }
  },
  "recommendation": "HIGH RISK - Likely phishing site",
  "confidence": 0.92
}
```

## Команды для разработки

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск тестов
python -m pytest tests/

# Линтинг
python -m flake8 src/
python -m black src/

# Проверка типов
python -m mypy src/
```

## Переменные окружения

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

## Репозиторий GitHub

https://github.com/lesshishkin2/site-checker