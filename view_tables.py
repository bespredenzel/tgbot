#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой просмотрщик базы данных SQLite
"""
import sqlite3

def view_tables():
    """Показывает все таблицы и их содержимое"""
    conn = sqlite3.connect('price_monitor.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("ПРОСМОТР БАЗЫ ДАННЫХ PRICE_MONITOR.DB")
    print("=" * 60)
    
    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Найдено таблиц: {len(tables)}")
    for table in tables:
        print(f"- {table[0]}")
    
    print("\n" + "=" * 60)
    
    # Показываем содержимое каждой таблицы
    for table in tables:
        table_name = table[0]
        print(f"\nТАБЛИЦА: {table_name}")
        print("-" * 40)
        
        # Получаем структуру таблицы
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print("Столбцы:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Получаем данные
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        
        print(f"\nЗаписей: {len(rows)}")
        if rows:
            print("Данные:")
            for i, row in enumerate(rows, 1):
                print(f"  {i}: {row}")
        else:
            print("Таблица пуста")
    
    conn.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    view_tables()

