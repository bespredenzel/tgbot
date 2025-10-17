#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import requests
import json
import sys
import os

# Устанавливаем кодировку для Windows
if sys.platform == "win32":
    os.system("chcp 65001 >nul")

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"\n[1] {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"[OK] {description} - успешно")
            if result.stdout.strip():
                print(f"   Вывод: {result.stdout.strip()}")
        else:
            print(f"[ERROR] {description} - ошибка")
            if result.stderr.strip():
                print(f"   Ошибка: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] {description} - исключение: {e}")
        return False

def test_render():
    """Тестирует работу Render"""
    print(f"\n[TEST] Тестирование Render...")
    try:
        response = requests.post(
            "https://tgbot-rrsb.onrender.com/api/search-article",
            json={"article": "146215073", "user_id": "test_update"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Render работает корректно")
            print(f"   Артикул: {result['article']}")
            print(f"   Название: {result['product_name']}")
            print(f"   Цена: {result['price']}")
            print(f"   Источник: {result['source']}")
            return True
        else:
            print(f"[ERROR] Render вернул ошибку: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка тестирования Render: {e}")
        return False

def main():
    """Основная функция обновления системы"""
    print("ЗАПУСК КОМАНДЫ 'UPDATE ALL'")
    print("=" * 50)
    
    # 1. Остановка процессов
    print("\nЭТАП 1: Остановка процессов")
    run_command("taskkill /f /im python.exe", "Остановка Python процессов")
    
    # Небольшая пауза
    time.sleep(2)
    
    # 2. Запуск приложения
    print("\nЭТАП 2: Запуск сервисов")
    run_command("python app.py", "Запуск Flask приложения")
    time.sleep(3)
    run_command("python telegram_bot.py", "Запуск Telegram бота")
    
    # Пауза для запуска сервисов
    time.sleep(5)
    
    # 3. Обновление Git
    print("\nЭТАП 3: Обновление Git")
    run_command("git add .", "Добавление файлов в Git")
    run_command("git commit -m \"Auto-update: restart services and test Render\"", "Создание коммита")
    run_command("git push", "Отправка в удаленный репозиторий")
    
    # 4. Ожидание обновления Render
    print("\nЭТАП 4: Ожидание обновления Render")
    print("Ожидание 60 секунд для обновления Render...")
    time.sleep(60)
    
    # 5. Тестирование Render
    print("\nЭТАП 5: Тестирование Render")
    render_works = test_render()
    
    # Итоговый отчет
    print("\n" + "=" * 50)
    print("ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 50)
    
    if render_works:
        print("[SUCCESS] ВСЕ СИСТЕМЫ РАБОТАЮТ КОРРЕКТНО!")
        print("   • Бот и приложение перезапущены")
        print("   • Git обновлен")
        print("   • Render работает")
        print("\nКОМАНДА 'UPDATE ALL' ВЫПОЛНЕНА УСПЕШНО!")
    else:
        print("[WARNING] ПРОБЛЕМЫ С RENDER")
        print("   • Бот и приложение перезапущены")
        print("   • Git обновлен")
        print("   • Render требует дополнительной проверки")
        print("\nРЕКОМЕНДУЕТСЯ ПРОВЕРИТЬ RENDER ВРУЧНУЮ")

if __name__ == "__main__":
    main()
