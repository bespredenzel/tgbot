#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой просмотр таблиц базы данных
"""
import sqlite3

def show_tables():
    conn = sqlite3.connect('price_monitor.db')
    cursor = conn.cursor()
    
    print("=== ТАБЛИЦА SKU (Товары) ===")
    cursor.execute('SELECT * FROM SKU')
    skus = cursor.fetchall()
    for sku in skus:
        print(f"ID: {sku[0]}")
        print(f"  Артикул: {sku[1]}")
        print(f"  Название: {sku[2]}")
        print(f"  Цена: {sku[3]} руб")
        print(f"  Источник: {sku[4]}")
        print(f"  Обновлено: {sku[5]}")
        print()
    
    print("=== ТАБЛИЦА DailyPrices (Ежедневные цены) ===")
    cursor.execute('SELECT * FROM DailyPrices')
    daily_prices = cursor.fetchall()
    for dp in daily_prices:
        print(f"ID: {dp[0]}")
        print(f"  SKU_ID: {dp[1]}")
        print(f"  Цена: {dp[2]} руб")
        print(f"  Источник: {dp[3]}")
        print(f"  Дата: {dp[4]}")
        print(f"  Создано: {dp[5]}")
        print()
    
    print("=== ТАБЛИЦА PriceHistory (История цен) ===")
    cursor.execute('SELECT * FROM PriceHistory')
    history = cursor.fetchall()
    for h in history:
        print(f"ID: {h[0]}")
        print(f"  SKU_ID: {h[1]}")
        print(f"  Цена: {h[2]} руб")
        print(f"  Источник: {h[3]}")
        print(f"  Записано: {h[4]}")
        print()
    
    conn.close()

if __name__ == "__main__":
    show_tables()

