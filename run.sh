#!/bin/bash

# Определение переменных
VENV_DIR=".venv"
IMAGES_DIR="images"

# Проверка наличия requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "Файл requirements.txt не найден. Пожалуйста, проверьте путь."
    exit 1
fi

# Создание и активация виртуального окружения
echo "Создание виртуального окружения..."

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Виртуальное окружение создано."
fi

# Активация виртуального окружения и установка зависимостей
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt

# Создание директории для изображений, если она не существует
if [ ! -d "$IMAGES_DIR" ]; then
    mkdir -p "$IMAGES_DIR"
    echo "Директория $IMAGES_DIR создана."
else
    echo "Директория $IMAGES_DIR уже существует."
fi

# Запуск бота
echo "Запуск Бота!."
python3 run.py
