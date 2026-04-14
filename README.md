# Telegram-бот магазина

## Ссылки

- **Бот:** [@Podarkibotalinavix_bot](t.me/Podarkibotalinavix_bot)
- **Презентация:** [https://docs.google.com/presentation/d/1h-TJel_5tW3xpbtJFJSbKkYF6pEr-Hj6Kk7Qlh_0eXI/edit?usp=drive_link](#)

---

 ##Описание проекта
Telegram-бот с кулинарными рецептами, написанный на Python с использованием библиотеки aiogram 2.25.

Бот позволяет пользователям получать случайные рецепты, сохранять понравившиеся в избранное, добавлять свои рецепты с фотографиями и искать блюда по ингредиентам. Администратор может управлять рецептами.

База данных содержит [КОЛИЧЕСТВО] рецептов с фотографиями, импортированных с сайта Povarenok.ru.

Все данные хранятся в локальной базе данных SQLite (db.db).
---

## Структура проекта

```
[  Итоговый проект]/
├── main.py           # Основной файл бота (хэндлеры, логика)
├── base.py           # Класс SQL для работы с базой данных
├── config.py         # Токен бота
├── db.db             # База данных SQLite (рецепты, пользователи, избранное)
├── requirements.txt  # Зависимости проекта
└── images/           # Фотографии рецептов (сохраняются автоматически)

### Таблицы базы данных

| Таблица  | Назначение                                      |
|----------|-------------------------------------------------|
| `users`  | Данные пользователей (имя, статус, роль)    |
| `recept`  | Рецепты (название, описание, ингредиенты, статус)       |
| `favourite_recipe` | Избранные рецепты пользователей        |

---

## Инструкция по запуску на Windows

### 1. Клонирование / копирование проекта

Если проект уже есть на рабочем столе, этот шаг можно пропустить.

Если используете GitHub:

```bash
git clone https://github.com/ivan-artemev24/python-bot
cd python-bot
```

### 2. Создание и активация виртуального окружения

```powershell
# Создать виртуальное окружение (папка venv появится в корне проекта)
python -m venv venv

# Активировать окружение
.\venv\Scripts\Activate.ps1
```

При успешной активации в начале строки PowerShell появится префикс `(venv)`.

> **Если PowerShell выдаёт ошибку выполнения скриптов**, выполните один раз:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка токена

Создайте файл `config.py` в корне проекта:

```python
TOKEN = "ваш_токен_от_BotFather"
```

Токен можно получить у [@BotFather](https://t.me/BotFather) в Telegram.

### 5. Запуск бота

```bash
python main.py
```

Бот запустится в режиме long polling. Для остановки нажмите `Ctrl+C`.

---

## Требования

- Python 3.10+
- Токен бота от [@BotFather](https://t.me/BotFather)
- Зависимости из `requirements.txt`:
-aiogram==2.25.1
-aiohttp
-aiohttp-socks
-requests
-beautifulsoup4
-datasets

```
aiogram==3.26.0
```
