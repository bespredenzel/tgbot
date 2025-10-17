#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отображения базы данных в табличном формате
"""
import sqlite3
from datetime import datetime

def display_tables_formatted():
    """Отображает таблицы в удобном табличном формате"""
    conn = sqlite3.connect('price_monitor.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("БАЗА ДАННЫХ PRICE MONITOR - ТАБЛИЧНЫЙ ФОРМАТ")
    print("=" * 80)
    
    # Таблица SKU
    print("\nТАБЛИЦА SKU (Товары):")
    print("-" * 80)
    cursor.execute('SELECT * FROM SKU')
    skus = cursor.fetchall()
    
    if skus:
        print(f"{'ID':<3} {'Артикул':<12} {'Название':<20} {'Цена':<8} {'Источник':<12} {'Обновлено':<20}")
        print("-" * 80)
        for sku in skus:
            print(f"{sku[0]:<3} {sku[1]:<12} {sku[2]:<20} {sku[3]:<8} {sku[4]:<12} {sku[5]:<20}")
    else:
        print("Товары не найдены")
    
    # Таблица DailyPrices
    print(f"\nТАБЛИЦА DailyPrices (Ежедневные цены):")
    print("-" * 80)
    cursor.execute('SELECT * FROM DailyPrices')
    daily_prices = cursor.fetchall()
    
    if daily_prices:
        print(f"{'ID':<3} {'SKU_ID':<6} {'Цена':<8} {'Источник':<12} {'Дата':<12} {'Создано':<20}")
        print("-" * 80)
        for dp in daily_prices:
            print(f"{dp[0]:<3} {dp[1]:<6} {dp[2]:<8} {dp[3]:<12} {dp[4]:<12} {dp[5]:<20}")
    else:
        print("Ежедневные цены не найдены")
    
    # Таблица PriceHistory (первые 20 записей)
    print(f"\nТАБЛИЦА PriceHistory (История цен) - последние 20 записей:")
    print("-" * 80)
    cursor.execute('''
        SELECT * FROM PriceHistory 
        ORDER BY recorded_at DESC 
        LIMIT 20
    ''')
    price_history = cursor.fetchall()
    
    if price_history:
        print(f"{'ID':<3} {'SKU_ID':<6} {'Цена':<8} {'Источник':<15} {'Записано':<20}")
        print("-" * 80)
        for ph in price_history:
            print(f"{ph[0]:<3} {ph[1]:<6} {ph[2]:<8} {ph[3]:<15} {ph[4]:<20}")
    else:
        print("История цен пуста")
    
    # Статистика
    print(f"\nСТАТИСТИКА:")
    print("-" * 50)
    
    cursor.execute('SELECT COUNT(*) FROM SKU')
    total_skus = cursor.fetchone()[0]
    print(f"Всего товаров (SKU): {total_skus}")
    
    cursor.execute('SELECT COUNT(*) FROM DailyPrices')
    daily_records = cursor.fetchone()[0]
    print(f"Ежедневных записей: {daily_records}")
    
    cursor.execute('SELECT COUNT(*) FROM PriceHistory')
    history_records = cursor.fetchone()[0]
    print(f"Записей в истории: {history_records}")
    
    # Статистика по источникам
    cursor.execute('''
        SELECT price_source, COUNT(*) as count
        FROM PriceHistory 
        GROUP BY price_source
        ORDER BY count DESC
    ''')
    sources_stats = cursor.fetchall()
    
    print(f"\nИсточники данных:")
    for source, count in sources_stats:
        print(f"  {source}: {count} записей")
    
    # Статистика по месяцам
    cursor.execute('''
        SELECT strftime('%Y-%m', recorded_at) as month, COUNT(*) as count
        FROM PriceHistory 
        GROUP BY strftime('%Y-%m', recorded_at)
        ORDER BY month DESC
    ''')
    monthly_stats = cursor.fetchall()
    
    print(f"\nЗаписи по месяцам:")
    for month, count in monthly_stats:
        print(f"  {month}: {count} записей")
    
    conn.close()
    print("\n" + "=" * 80)
    print("Просмотр завершен")

def display_price_history_by_date():
    """Отображает историю цен по датам в хронологическом порядке"""
    conn = sqlite3.connect('price_monitor.db')
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("ИСТОРИЯ ЦЕН ПО ДАТАМ (хронологический порядок)")
    print("=" * 80)
    
    cursor.execute('''
        SELECT DATE(recorded_at) as date, price, price_source, COUNT(*) as records
        FROM PriceHistory 
        GROUP BY DATE(recorded_at), price, price_source
        ORDER BY date DESC
    ''')
    
    daily_records = cursor.fetchall()
    
    if daily_records:
        print(f"{'Дата':<12} {'Цена':<8} {'Источник':<15} {'Записей':<8}")
        print("-" * 50)
        
        current_date = None
        for record in daily_records:
            date, price, source, records = record
            if date != current_date:
                print(f"\n{date}:")
                current_date = date
            print(f"  {price:<8} {source:<15} {records:<8}")
    else:
        print("История цен пуста")
    
    conn.close()
    print("\n" + "=" * 80)

if __name__ == "__main__":
    display_tables_formatted()
    display_price_history_by_date()
