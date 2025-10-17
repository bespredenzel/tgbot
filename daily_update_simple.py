#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный скрипт ежедневного обновления всех товаров
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import daily_update_all_products, get_daily_update_stats
from datetime import datetime

def run_daily_update():
    """Запускает ежедневное обновление"""
    print(f"\n{'='*60}")
    print(f"ЕЖЕДНЕВНОЕ ОБНОВЛЕНИЕ ТОВАРОВ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Получаем статистику до обновления
    stats_before = get_daily_update_stats()
    print(f"Статистика до обновления:")
    print(f"  Товаров для обновления: {stats_before['total_products']}")
    print(f"  Последнее обновление: {stats_before['last_update']}")
    
    # Запускаем обновление
    daily_update_all_products()
    
    # Получаем статистику после обновления
    stats_after = get_daily_update_stats()
    print(f"\nСтатистика после обновления:")
    print(f"  Последнее обновление: {stats_after['last_update']}")
    print(f"  Обновлений за 7 дней: {stats_after['recent_updates']}")
    
    print(f"{'='*60}\n")

def show_stats():
    """Показывает статистику обновлений"""
    stats = get_daily_update_stats()
    print("Статистика ежедневных обновлений:")
    print(f"  Товаров для обновления: {stats['total_products']}")
    print(f"  Обновлений за 7 дней: {stats['recent_updates']}")
    print(f"  Последнее обновление: {stats['last_update']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "stats":
            show_stats()
        else:
            print("Использование:")
            print("  python daily_update_simple.py        - Запустить обновление")
            print("  python daily_update_simple.py stats  - Показать статистику")
    else:
        run_daily_update()
