# ME Terminal

Веб-панель для мониторинга инвентаря складов на Minecraft-сервере. Сканирует контейнеры (сундуки, шалкеры, бочки) и показывает все предметы в реальном времени с 3D иконками.

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Tailwind](https://img.shields.io/badge/Tailwind-4-38bdf8?logo=tailwindcss)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Возможности

- Отображение всех предметов со складов в виде сетки с 3D иконками
- Поиск на русском и английском языке
- Фильтр по категориям (Блоки / Инструменты / Броня / Еда / Ресурсы)
- Несколько складов с переключением
- Авто-обновление каждые 15 секунд
- Тёмный glassmorphism дизайн с неоновыми акцентами
- Тултипы с детальной информацией (количество, шалкеры)
- Сортировка по количеству и имени

---

## Стек

| Компонент | Технология |
|-----------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, shadcn/ui |
| Backend API | Python (stdlib http.server) |
| Данные | NBT-парсер region файлов Minecraft |
| Иконки | 3D renders (webp) + Faithful 64x + vanilla jar |

---

## Быстрый старт

### Требования

- Python 3.10+
- Node.js 20+
- npm

### Установка

```bash
git clone https://github.com/BaXyTostik/ME-Terminal.git
cd ME-Terminal

# Установить зависимости фронтенда
cd frontend
npm install
cd ..
```

### Запуск

```bash
# Вариант 1: через bat-файл (Windows)
start_server.bat

# Вариант 2: вручную (два терминала)
python server.py              # API на :8000
cd frontend && npm run dev    # Frontend на :3000
```

Открыть http://localhost:3000

---

## Настройка

Файл `config.json`:

```json
{
  "data_file": "region/containers.json",
  "refresh_interval": 15,
  "warehouses": {
    "our_warehouse": "Наш склад",
    "wool_warehouse": "Склад шерсти"
  }
}
```

---

## Структура проекта

```
ME-Terminal/
├── server.py                 # Python API сервер
├── config.json               # Конфигурация складов
├── nbt_parser.py             # Парсер NBT данных
├── start_server.bat          # Запуск обоих серверов
├── static/
│   └── textures/             # Иконки предметов (renders, faithful, jar)
└── frontend/                 # Next.js приложение
    ├── src/
    │   ├── app/              # Главная страница + стили
    │   ├── components/       # React компоненты
    │   └── lib/              # API, типы, категории, локализация
    ├── next.config.ts        # Proxy к Python API
    └── package.json
```

---

## Иконки

Текстуры не включены в репозиторий (слишком большие). Для загрузки:

```bash
# 3D renders (~1500 предметов, webp)
# Источник: github.com/JuraRusan/Minecraft-calculator
# Поместить в: static/textures/renders/

# Faithful 64x (PNG)
# Поместить в: static/textures/faithful/item/ и faithful/block/

# Vanilla jar fallback (16x PNG)
# Поместить в: static/textures/jar/item/ и jar/block/
```

---

## API

| Endpoint | Описание |
|----------|----------|
| `GET /api/warehouses` | Список складов |
| `GET /api/items?wh=__all__` | Предметы склада |
| `GET /api/config` | Конфигурация |
| `GET /textures/{path}` | Иконки предметов |

---

## Лицензия

MIT
