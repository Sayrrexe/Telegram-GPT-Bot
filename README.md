# GPT\Image Generation Bot

Этот проект представляет собой бота, который использует бесплатные API GPT для генерации текстовых ответов и изображений на основе пользовательских запросов. Бот поддерживает команды для получения истории запросов, очистки истории и генерации изображений.

## Установка

### Предварительные требования

- Python 3.7 или выше
- pip (Python package installer)
- Доступ к интернету для работы с API

### Клонирование репозитория

Сначала клонируйте репозиторий:

```bash
git clone https://github.com/Sayrrexe/Telegram-GPT-Bot.git
cd Telegram-GPT-Bot
```

### Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта и добавьте в него ваш токен:

```
TOKEN=ваш_токен
```
### Ручная установка

1. Создайте виртуальное окружение и активируйте его:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Установите зависимости из файла `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

### Автоматическая установка
Только для Ubuntu

    ```bash
    chmod +x setup.sh
    ./run.sh
    ```

Скрипт автоматически установит все зависимости и запустит работу бота


## Использование

1. Запустите бота:

   ```bash
   python3 run.py
   ```

2. Взаимодействуйте с ботом через Telegram. Используйте команды:
   - `/start` - Начать взаимодействие с ботом.
   - `/img текст` - Сгенерировать изображение на основе текста.
   - `/history` - Просмотреть историю запросов.
   - `/clear` - Очистить историю запросов.

## Структура проекта

- `config.py` - Конфигурация и настройки проекта.
- `user.py` - Логика обработки сообщений от пользователей.
- `gpt.py` - Взаимодействие с моделями GPT для генерации текста и изображений.
- `app/images.py` - Модули для загрузки изображений.
- `requirements.txt` - Список зависимостей проекта.

## Лицензия

Этот проект лицензирован под MIT License. Пожалуйста, ознакомьтесь с файлом LICENSE для получения дополнительной информации.

## Контрибьюция

Если вы хотите внести свой вклад в проект, пожалуйста, создайте форк репозитория, внесите изменения и создайте pull request.

## Поддержка

Если у вас есть вопросы или проблемы, пожалуйста, создайте issue в репозитории.