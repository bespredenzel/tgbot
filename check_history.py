#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка истории цен после добавления исторических данных
"""
import requests

def check_history():
    """Проверяет историю цен"""
    print("=" * 60)
    print("ПРОВЕРКА ИСТОРИИ ЦЕН")
    print("=" * 60)
    
    try:
        # Получаем историю цен
        response = requests.get('http://127.0.0.1:5000/api/sku/146215073/history')
        
        if response.status_code == 200:
            data = response.json()
            print(f"Артикул: {data['article']}")
            print(f"Всего записей в истории: {len(data['history'])}")
            print("\nПоследние 15 записей:")
            print("-" * 50)
            
            for i, record in enumerate(data['history'][:15], 1):
                print(f"{i:2d}. {record['price']} руб ({record['source']}) - {record['recorded_at']}")
            
            # Статистика по источникам
            sources = {}
            for record in data['history']:
                source = record['source']
                sources[source] = sources.get(source, 0) + 1
            
            print(f"\nСтатистика по источникам:")
            print("-" * 30)
            for source, count in sources.items():
                print(f"   {source}: {count} записей")
                
        else:
            print(f"Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_history()

