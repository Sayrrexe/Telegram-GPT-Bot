#!/bin/bash

# Определение переменных
VENV_DIR=".venv"
IMAGES_DIR="images"
REQUIREMENTS_FILE="requirements.txt"

# Функция для проверки наличия команды
check_command() {
    command -v "$1" >/dev/null 2>&1 || { echo >&2 "Необходимо установить $1. Пожалуйста, установите его и повторите попытку."; exit 1; }
}

# Проверка наличия Python и pip
check_command python3
check_command pip3

# Проверка наличия requirements.txt
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "Файл $REQUIREMENTS_FILE не найден. Пожалуйста, проверьте путь."
    exit 1
fi

# Установка системных зависимостей 
echo "Установка системных зависимостей..."
sudo apt-get install -y python3-venv python3-pip

# Создание и активация виртуального окружения
echo "Создание виртуального окружения..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Виртуальное окружение создано."
else
    echo "Виртуальное окружение уже существует."
fi

# Активация виртуального окружения
source "$VENV_DIR/bin/activate"

# Установка зависимостей
echo "Установка зависимостей из $REQUIREMENTS_FILE..."
pip install --upgrade pip  # Обновление pip до последней версии
pip install -r "$REQUIREMENTS_FILE"

# Создание директории для изображений, если она не существует
if [ ! -d "$IMAGES_DIR" ]; then
    mkdir -p "$IMAGES_DIR"
    echo "Директория $IMAGES_DIR создана."
else
    echo "Директория $IMAGES_DIR уже существует."
fi

# Запуск бота
echo "Запуск Бота..."
python3 run.py