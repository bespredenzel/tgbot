#!/bin/bash
# Запуск приложения на Railway

echo "Запуск Price Monitor Bot..."

# Запускаем Flask приложение в фоне
python app.py &
FLASK_PID=$!

# Запускаем Telegram бота
python telegram_bot.py &
BOT_PID=$!

# Ждем завершения процессов
wait $FLASK_PID $BOT_PID
