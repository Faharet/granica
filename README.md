# Granica - Система управления арендой электровелосипедов

Веб-приложение для управления парком электровелосипедов, бронированием и арендой. Построено на Django с использованием django-daisy для современного интерфейса.

## Основные возможности

- **Управление велосипедами**
  - Каталог моделей электровелосипедов с характеристиками
  - Учёт конкретных велосипедов с серийными номерами
  - Мониторинг статуса (доступен, забронирован, в аренде, в ремонте)
  - Отслеживание технического обслуживания
  - GPS-трекинг велосипедов
  - Управление фотографиями моделей

- **Система бронирования**
  - Бронирование велосипедов пользователями
  - Обработка запросов менеджерами
  - Отслеживание статусов бронирования
  - Комментарии пользователей и менеджеров

- **Управление арендой**
  - Оформление договоров аренды
  - Контроль депозитов и штрафов
  - Отслеживание просроченных аренд
  - История аренд пользователей

- **Профили пользователей**
  - Расширенные профили с личными данными
  - Загрузка документов удостоверяющих личность
  - Контактная информация
  - Информация о близких родственниках

- **Многоязычность**
  - Поддержка русского, казахского и английского языков
  - Локализация интерфейса

## Технологический стек

- **Backend**: Django 5.2+
- **UI**: django-daisy (современный UI framework)
- **База данных**: PostgreSQL
- **Хранилище файлов**: MinIO
- **Дополнительно**: 
  - django-phonenumber-field для работы с номерами телефонов
  - python-dotenv для управления конфигурацией

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/Faharet/granica.git
cd granica
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Django настройки
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# База данных PostgreSQL
DB_NAME=granica
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# MinIO настройки
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_USE_HTTPS=False
MINIO_BUCKET_NAME=granica-media
```

### 5. Инициализация базы данных

```bash
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Компиляция переводов

```bash
python compile_translations.py
```

### 8. Сборка CSS (опционально)

```bash
npm install
npm run build
```

### 9. Запуск сервера разработки

```bash
python manage.py runserver
```

Откройте браузер и перейдите по адресу http://127.0.0.1:8000/

## Структура проекта

```
granica/
├── platform_manager/      # Управление пользователями и профилями
│   ├── models.py         # User, Profile, AdminUser и др.
│   ├── views.py          # Представления
│   └── admin.py          # Настройки админ-панели
├── bikes_manager/        # Управление велосипедами (архив)
├── rent_manager/         # Управление арендой и бронированием
│   ├── models.py         # Contract, Booking, Rental
│   └── admin.py          # Настройки админ-панели
├── django_daisy/         # UI компоненты
├── granica_admin/        # Настройки проекта
│   ├── settings.py       # Конфигурация Django
│   └── urls.py           # Маршруты
└── templates/            # HTML шаблоны
```

## Модели данных

### Основные модели:

- **User**: Пользователи системы
- **Profile**: Профили с персональными данными
- **BicycleModel**: Модели электровелосипедов
- **Bicycle**: Конкретные велосипеды
- **Booking**: Бронирования велосипедов
- **Rental**: Активные аренды
- **Contract**: Договоры аренды

## Разработка

### Требования

- Python 3.10+
- PostgreSQL 13+
- MinIO (для хранения файлов)
- Node.js (для сборки frontend)

### Установка зависимостей для разработки

```bash
pip install -r requirements.txt
```

### Миграции базы данных

```bash
# Создание новых миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate
```

### Работа с переводами

```bash
# Сбор строк для перевода
python manage.py makemessages -l ru
python manage.py makemessages -l kk

# Компиляция переводов
python compile_translations.py
```

## Конфигурация

Все настройки управляются через переменные окружения в файле `.env`. Основные параметры:

- `DJANGO_SECRET_KEY` - секретный ключ Django
- `DJANGO_DEBUG` - режим отладки
- `DJANGO_ALLOWED_HOSTS` - разрешённые хосты
- `DB_*` - параметры подключения к БД
- `MINIO_*` - параметры хранилища файлов

## Лицензия

MIT License

## Автор

Faharet - [GitHub](https://github.com/Faharet)