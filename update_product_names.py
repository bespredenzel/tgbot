#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления названий товаров в базе данных
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_all_skus, add_or_update_sku
from app import get_product_price

def update_product_names():
    """Обновляет названия всех товаров в базе данных"""
    print("Обновление названий товаров...")
    
    # Получаем все товары из базы
    skus = get_all_skus()
    
    if not skus:
        print("В базе данных нет товаров")
        return
    
    print(f"Найдено {len(skus)} товаров для обновления")
    
    updated_count = 0
    
    for sku in skus:
        sku_id, article, current_name, current_price, price_source, last_updated, product_url, created_at = sku
        
        # Проверяем, нужно ли обновлять название
        if current_name and not current_name.startswith('Товар '):
            print(f"Товар {article}: название уже корректное - '{current_name[:50]}...'")
            continue
        
        print(f"\nОбновляем товар {article}...")
        
        try:
            # Получаем актуальную информацию о товаре
            product_url = f"https://www.ozon.ru/product/{article}/"
            result = get_product_price(product_url)
            
            if isinstance(result, dict):
                new_name = result.get('name', f'Товар {article}')
                new_price = result.get('price', current_price)
                new_source = result.get('source', price_source)
                
                # Извлекаем только число из цены
                import re
                price_match = re.search(r'([\d\s,]+)', new_price)
                price_value = price_match.group(1).strip() if price_match else current_price
                
                # Обновляем товар в базе
                updated_sku_id = add_or_update_sku(
                    article=article,
                    product_name=new_name,
                    current_price=price_value,
                    price_source=new_source,
                    product_url=product_url
                )
                
                if updated_sku_id:
                    print(f"OK Обновлено: {new_name[:50]}...")
                    updated_count += 1
                else:
                    print(f"ERROR Ошибка обновления товара {article}")
            else:
                print(f"ERROR Не удалось получить данные для товара {article}")
                
        except Exception as e:
            print(f"ERROR Ошибка при обновлении товара {article}: {e}")
    
    print(f"\nОбновление завершено. Обновлено товаров: {updated_count}")

if __name__ == "__main__":
    update_product_names()
