#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления исторических цен за сентябрь 2025
"""
import sqlite3
import random
from datetime import datetime, timedelta

def add_september_history():
    """Добавляет исторические цены за сентябрь 2025"""
    print("=" * 60)
    print("ДОБАВЛЕНИЕ ИСТОРИЧЕСКИХ ЦЕН ЗА СЕНТЯБРЬ 2025")
    print("=" * 60)
    
    # Подключаемся к базе данных
    conn = sqlite3.connect('price_monitor.db')
    cursor = conn.cursor()
    
    try:
        # Получаем информацию о существующем SKU
        cursor.execute('SELECT id, article, current_price FROM SKU WHERE id = 1')
        sku_data = cursor.fetchone()
        
        if not sku_data:
            print("Ошибка: SKU с ID=1 не найден!")
            return
        
        sku_id, article, base_price = sku_data
        base_price_int = int(base_price.replace(' ', '').replace(',', ''))
        
        print(f"Найден SKU:")
        print(f"   ID: {sku_id}")
        print(f"   Артикул: {article}")
        print(f"   Базовая цена: {base_price} руб")
        print(f"   Базовая цена (число): {base_price_int} руб")
        
        # Генерируем даты с 1 по 30 сентября 2025
        start_date = datetime(2025, 9, 1)
        end_date = datetime(2025, 9, 30)
        
        current_date = start_date
        added_count = 0
        
        print(f"\nДобавление цен с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}:")
        print("-" * 50)
        
        while current_date <= end_date:
            # Случайное изменение цены: +2, +1, 0, -1, -2
            price_change = random.choice([-2, -1, 0, 1, 2])
            new_price = base_price_int + price_change
            
            # Убеждаемся, что цена не отрицательная
            if new_price < 1:
                new_price = 1
            
            # Форматируем цену как в базе
            price_str = str(new_price)
            
            # Проверяем, есть ли уже цена на эту дату
            cursor.execute('''
                SELECT id FROM PriceHistory 
                WHERE sku_id = ? AND DATE(recorded_at) = ?
            ''', (sku_id, current_date.strftime('%Y-%m-%d')))
            
            existing_price = cursor.fetchone()
            
            if not existing_price:
                # Добавляем новую запись в историю
                cursor.execute('''
                    INSERT INTO PriceHistory (sku_id, price, price_source, recorded_at)
                    VALUES (?, ?, ?, ?)
                ''', (sku_id, price_str, 'Historical Data', current_date.strftime('%Y-%m-%d %H:%M:%S')))
                
                added_count += 1
                print(f"   {current_date.strftime('%d.%m.%Y')}: {price_str} руб (изменение: {price_change:+d})")
            else:
                print(f"   {current_date.strftime('%d.%m.%Y')}: цена уже существует, пропускаем")
            
            # Переходим к следующему дню
            current_date += timedelta(days=1)
        
        # Сохраняем изменения
        conn.commit()
        
        print(f"\nРезультат:")
        print(f"   Добавлено записей: {added_count}")
        print(f"   Период: сентябрь 2025")
        
        # Показываем статистику
        cursor.execute('SELECT COUNT(*) FROM PriceHistory WHERE sku_id = ?', (sku_id,))
        total_records = cursor.fetchone()[0]
        
        print(f"   Всего записей в истории для SKU {sku_id}: {total_records}")
        
        # Показываем последние 5 записей
        print(f"\nПоследние 5 записей в истории:")
        print("-" * 40)
        
        cursor.execute('''
            SELECT price, price_source, recorded_at
            FROM PriceHistory 
            WHERE sku_id = ?
            ORDER BY recorded_at DESC
            LIMIT 5
        ''', (sku_id,))
        
        recent_records = cursor.fetchall()
        
        for i, record in enumerate(recent_records, 1):
            price, source, recorded_at = record
            print(f"   {i}. {price} руб ({source}) - {recorded_at}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\n" + "=" * 60)
    print("ДОБАВЛЕНИЕ ИСТОРИЧЕСКИХ ЦЕН ЗАВЕРШЕНО")

if __name__ == "__main__":
    add_september_history()
