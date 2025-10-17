#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для округления всех цен в базе данных в большую сторону
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
import math
import re

def round_all_prices():
    """Округляет все цены в базе данных в большую сторону"""
    print("Округление всех цен в большую сторону...")
    
    conn = sqlite3.connect('price_monitor.db')
    cursor = conn.cursor()
    
    try:
        # Получаем все записи с ценами
        cursor.execute('SELECT id, current_price FROM SKU WHERE current_price IS NOT NULL')
        skus = cursor.fetchall()
        
        cursor.execute('SELECT id, price FROM PriceHistory WHERE price IS NOT NULL')
        price_history = cursor.fetchall()
        
        cursor.execute('SELECT id, price FROM DailyPrices WHERE price IS NOT NULL')
        daily_prices = cursor.fetchall()
        
        print(f"Найдено записей для обновления:")
        print(f"  SKU: {len(skus)}")
        print(f"  PriceHistory: {len(price_history)}")
        print(f"  DailyPrices: {len(daily_prices)}")
        
        updated_count = 0
        
        # Обновляем цены в таблице SKU
        for sku_id, price in skus:
            rounded_price = round_price(price)
            if rounded_price != price:
                cursor.execute('UPDATE SKU SET current_price = ? WHERE id = ?', (rounded_price, sku_id))
                updated_count += 1
                print(f"SKU {sku_id}: {price} -> {rounded_price}")
        
        # Обновляем цены в таблице PriceHistory
        for ph_id, price in price_history:
            rounded_price = round_price(price)
            if rounded_price != price:
                cursor.execute('UPDATE PriceHistory SET price = ? WHERE id = ?', (rounded_price, ph_id))
                updated_count += 1
                print(f"PriceHistory {ph_id}: {price} -> {rounded_price}")
        
        # Обновляем цены в таблице DailyPrices
        for dp_id, price in daily_prices:
            rounded_price = round_price(price)
            if rounded_price != price:
                cursor.execute('UPDATE DailyPrices SET price = ? WHERE id = ?', (rounded_price, dp_id))
                updated_count += 1
                print(f"DailyPrices {dp_id}: {price} -> {rounded_price}")
        
        conn.commit()
        print(f"\nОкругление завершено. Обновлено записей: {updated_count}")
        
    except Exception as e:
        print(f"Ошибка при округлении цен: {e}")
        conn.rollback()
    finally:
        conn.close()

def round_price(price_str):
    """Округляет цену в большую сторону"""
    if not price_str:
        return price_str
    
    # Извлекаем только числа из цены
    price_match = re.search(r'([\d\s,]+)', str(price_str))
    if price_match:
        price_str_clean = price_match.group(1).replace(' ', '').replace(',', '')
        try:
            # Преобразуем в число и округляем в большую сторону
            price_value = math.ceil(float(price_str_clean))
            return str(price_value)
        except (ValueError, TypeError):
            return price_str
    else:
        return price_str

if __name__ == "__main__":
    round_all_prices()
