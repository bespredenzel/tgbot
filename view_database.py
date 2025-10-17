#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для просмотра содержимого базы данных Price Monitor
"""
import sqlite3
from datetime import datetime

def view_database():
    """Просматривает содержимое базы данных"""
    conn = sqlite3.connect('price_monitor.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("СОДЕРЖИМОЕ БАЗЫ ДАННЫХ PRICE MONITOR")
    print("=" * 60)
    
    # Статистика
    print("\nОБЩАЯ СТАТИСТИКА:")
    print("-" * 30)
    
    cursor.execute('SELECT COUNT(*) FROM SKU')
    total_skus = cursor.fetchone()[0]
    print(f"Всего товаров (SKU): {total_skus}")
    
    cursor.execute('SELECT COUNT(*) FROM UserSKU WHERE is_active = 1')
    active_user_skus = cursor.fetchone()[0]
    print(f"Активных связей пользователей: {active_user_skus}")
    
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM UserSKU WHERE is_active = 1')
    unique_users = cursor.fetchone()[0]
    print(f"Уникальных пользователей: {unique_users}")
    
    cursor.execute('SELECT COUNT(*) FROM PriceHistory')
    price_records = cursor.fetchone()[0]
    print(f"Записей в истории цен: {price_records}")
    
    cursor.execute('SELECT COUNT(*) FROM DailyPrices')
    daily_records = cursor.fetchone()[0]
    print(f"Ежедневных записей цен: {daily_records}")
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT COUNT(*) FROM DailyPrices WHERE price_date = ?', (today,))
    today_records = cursor.fetchone()[0]
    print(f"Записей на сегодня ({today}): {today_records}")
    
    # Все SKU
    print(f"\nВСЕ ТОВАРЫ В СПРАВОЧНИКЕ ({total_skus} шт.):")
    print("-" * 50)
    
    cursor.execute('''
        SELECT id, article, product_name, current_price, price_source, 
               last_updated, product_url, created_at
        FROM SKU 
        ORDER BY created_at DESC
    ''')
    
    skus = cursor.fetchall()
    
    if skus:
        for sku in skus:
            print(f"\nID: {sku[0]}")
            print(f"   Артикул: {sku[1]}")
            print(f"   Название: {sku[2]}")
            print(f"   Текущая цена: {sku[3]} руб")
            print(f"   Источник: {sku[4]}")
            print(f"   Обновлено: {sku[5]}")
            print(f"   Создано: {sku[6]}")
            print(f"   URL: {sku[7]}")
    else:
        print("   Товары не найдены")
    
    # Ежедневные цены на сегодня
    print(f"\nЦЕНЫ НА СЕГОДНЯ ({today}):")
    print("-" * 40)
    
    cursor.execute('''
        SELECT s.article, s.product_name, dp.price, dp.price_source, dp.created_at
        FROM DailyPrices dp
        JOIN SKU s ON dp.sku_id = s.id
        WHERE dp.price_date = ?
        ORDER BY dp.created_at DESC
    ''', (today,))
    
    today_prices = cursor.fetchall()
    
    if today_prices:
        for price in today_prices:
            print(f"   {price[0]} - {price[1]} | {price[2]} руб ({price[3]}) | {price[4]}")
    else:
        print("   Цены на сегодня не найдены")
    
    # Пользователи и их товары
    print(f"\nПОЛЬЗОВАТЕЛИ И ИХ ТОВАРЫ:")
    print("-" * 40)
    
    cursor.execute('''
        SELECT us.user_id, COUNT(us.sku_id) as sku_count,
               GROUP_CONCAT(s.article, ', ') as articles
        FROM UserSKU us
        JOIN SKU s ON us.sku_id = s.id
        WHERE us.is_active = 1
        GROUP BY us.user_id
        ORDER BY sku_count DESC
    ''')
    
    user_skus = cursor.fetchall()
    
    if user_skus:
        for user in user_skus:
            print(f"   Пользователь {user[0]}: {user[1]} товаров")
            print(f"   Артикулы: {user[2]}")
    else:
        print("   Пользователи не найдены")
    
    # Последние записи в истории цен
    print(f"\nПОСЛЕДНИЕ 10 ЗАПИСЕЙ В ИСТОРИИ ЦЕН:")
    print("-" * 50)
    
    cursor.execute('''
        SELECT s.article, ph.price, ph.price_source, ph.recorded_at
        FROM PriceHistory ph
        JOIN SKU s ON ph.sku_id = s.id
        ORDER BY ph.recorded_at DESC
        LIMIT 10
    ''')
    
    recent_prices = cursor.fetchall()
    
    if recent_prices:
        for price in recent_prices:
            print(f"   {price[0]} | {price[1]} руб ({price[2]}) | {price[3]}")
    else:
        print("   История цен пуста")
    
    conn.close()
    print("\n" + "=" * 60)
    print("Просмотр базы данных завершен")

if __name__ == "__main__":
    view_database()
