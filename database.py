import sqlite3
import os
from datetime import datetime

# Путь к базе данных
DB_PATH = 'price_monitor.db'

def init_database():
    """Инициализация базы данных и создание таблиц"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица SKU - все товары, которые были запрошены
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SKU (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article TEXT UNIQUE NOT NULL,
            product_name TEXT,
            current_price TEXT,
            price_source TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            product_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица UserSKU - связь пользователей с товарами
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserSKU (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            sku_id INTEGER NOT NULL,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (sku_id) REFERENCES SKU (id),
            UNIQUE(user_id, sku_id)
        )
    ''')
    
    # Таблица PriceHistory - история цен
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PriceHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku_id INTEGER NOT NULL,
            price TEXT NOT NULL,
            price_source TEXT,
            recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sku_id) REFERENCES SKU (id)
        )
    ''')
    
    # Таблица DailyPrices - ежедневные цены
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DailyPrices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku_id INTEGER NOT NULL,
            price TEXT NOT NULL,
            price_source TEXT,
            price_date DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sku_id) REFERENCES SKU (id),
            UNIQUE(sku_id, price_date)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных инициализирована успешно")

def add_or_update_sku(article, product_name=None, current_price=None, price_source=None, product_url=None):
    """Добавляет или обновляет товар в таблице SKU"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли товар
        cursor.execute('SELECT id FROM SKU WHERE article = ?', (article,))
        existing_sku = cursor.fetchone()
        
        if existing_sku:
            # Обновляем существующий товар
            sku_id = existing_sku[0]
            cursor.execute('''
                UPDATE SKU 
                SET current_price = ?, price_source = ?, last_updated = CURRENT_TIMESTAMP,
                    product_name = COALESCE(?, product_name), product_url = COALESCE(?, product_url)
                WHERE id = ?
            ''', (current_price, price_source, product_name, product_url, sku_id))
            
            # Добавляем запись в историю цен
            if current_price:
                cursor.execute('''
                    INSERT INTO PriceHistory (sku_id, price, price_source)
                    VALUES (?, ?, ?)
                ''', (sku_id, current_price, price_source))
        else:
            # Создаем новый товар
            cursor.execute('''
                INSERT INTO SKU (article, product_name, current_price, price_source, product_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (article, product_name, current_price, price_source, product_url))
            
            sku_id = cursor.lastrowid
            
            # Добавляем запись в историю цен
            if current_price:
                cursor.execute('''
                    INSERT INTO PriceHistory (sku_id, price, price_source)
                    VALUES (?, ?, ?)
                ''', (sku_id, current_price, price_source))
        
        conn.commit()
        return sku_id
        
    except Exception as e:
        print(f"Ошибка при добавлении/обновлении SKU: {e}")
        return None
    finally:
        conn.close()

def add_user_sku(user_id, sku_id):
    """Добавляет связь пользователя с товаром"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли уже связь
        cursor.execute('''
            SELECT id, is_active FROM UserSKU 
            WHERE user_id = ? AND sku_id = ?
        ''', (user_id, sku_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # Если связь существует, но неактивна - активируем её
            if existing[1] == 0:
                cursor.execute('''
                    UPDATE UserSKU 
                    SET is_active = 1, added_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (existing[0],))
                conn.commit()
                return True
            else:
                # Связь уже активна
                return True
        else:
            # Создаем новую связь
            cursor.execute('''
                INSERT INTO UserSKU (user_id, sku_id, is_active)
                VALUES (?, ?, 1)
            ''', (user_id, sku_id))
            conn.commit()
            return True
        
    except Exception as e:
        print(f"Ошибка при добавлении UserSKU: {e}")
        return False
    finally:
        conn.close()

def get_user_skus(user_id):
    """Получает все товары пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT s.article, s.product_name, s.current_price, s.price_source, 
                   s.last_updated, s.product_url, us.added_at
            FROM UserSKU us
            JOIN SKU s ON us.sku_id = s.id
            WHERE us.user_id = ? AND us.is_active = 1
            ORDER BY us.added_at DESC
        ''', (user_id,))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Ошибка при получении товаров пользователя: {e}")
        return []
    finally:
        conn.close()

def get_sku_by_article(article):
    """Получает товар по артикулу"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM SKU WHERE article = ?', (article,))
        return cursor.fetchone()
        
    except Exception as e:
        print(f"Ошибка при получении SKU: {e}")
        return None
    finally:
        conn.close()

def get_price_history(sku_id, limit=10):
    """Получает историю цен товара"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        if limit is None:
            # Получаем все записи без ограничения
            cursor.execute('''
                SELECT price, price_source, recorded_at
                FROM PriceHistory
                WHERE sku_id = ?
                ORDER BY recorded_at DESC
            ''', (sku_id,))
        else:
            # Получаем ограниченное количество записей
            cursor.execute('''
                SELECT price, price_source, recorded_at
                FROM PriceHistory
                WHERE sku_id = ?
                ORDER BY recorded_at DESC
                LIMIT ?
            ''', (sku_id, limit))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Ошибка при получении истории цен: {e}")
        return []
    finally:
        conn.close()

def get_all_skus():
    """Получает все товары из базы"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM SKU ORDER BY created_at DESC')
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Ошибка при получении всех SKU: {e}")
        return []
    finally:
        conn.close()

def remove_user_sku(user_id, article):
    """Удаляет товар из списка пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Находим SKU по артикулу
        cursor.execute('SELECT id FROM SKU WHERE article = ?', (article,))
        sku = cursor.fetchone()
        
        if sku:
            sku_id = sku[0]
            cursor.execute('''
                UPDATE UserSKU 
                SET is_active = 0 
                WHERE user_id = ? AND sku_id = ?
            ''', (user_id, sku_id))
            
            conn.commit()
            return True
        
        return False
        
    except Exception as e:
        print(f"Ошибка при удалении UserSKU: {e}")
        return False
    finally:
        conn.close()

def get_daily_price(sku_id, price_date=None):
    """Получает цену товара на определенную дату"""
    if price_date is None:
        price_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT price, price_source, created_at
            FROM DailyPrices
            WHERE sku_id = ? AND price_date = ?
        ''', (sku_id, price_date))
        
        result = cursor.fetchone()
        return result
        
    except Exception as e:
        print(f"Ошибка при получении ежедневной цены: {e}")
        return None
    finally:
        conn.close()

def add_daily_price(sku_id, price, price_source, price_date=None):
    """Добавляет или обновляет ежедневную цену"""
    if price_date is None:
        price_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем, есть ли уже цена на эту дату
        cursor.execute('''
            SELECT id FROM DailyPrices
            WHERE sku_id = ? AND price_date = ?
        ''', (sku_id, price_date))
        
        existing_price = cursor.fetchone()
        
        if existing_price:
            # Обновляем существующую цену
            cursor.execute('''
                UPDATE DailyPrices
                SET price = ?, price_source = ?, created_at = CURRENT_TIMESTAMP
                WHERE sku_id = ? AND price_date = ?
            ''', (price, price_source, sku_id, price_date))
        else:
            # Добавляем новую цену
            cursor.execute('''
                INSERT INTO DailyPrices (sku_id, price, price_source, price_date)
                VALUES (?, ?, ?, ?)
            ''', (sku_id, price, price_source, price_date))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Ошибка при добавлении ежедневной цены: {e}")
        return False
    finally:
        conn.close()

def get_daily_price_by_article(article, price_date=None):
    """Получает ежедневную цену товара по артикулу"""
    if price_date is None:
        price_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT dp.price, dp.price_source, dp.created_at, s.article, s.product_name
            FROM DailyPrices dp
            JOIN SKU s ON dp.sku_id = s.id
            WHERE s.article = ? AND dp.price_date = ?
        ''', (article, price_date))
        
        result = cursor.fetchone()
        return result
        
    except Exception as e:
        print(f"Ошибка при получении ежедневной цены по артикулу: {e}")
        return None
    finally:
        conn.close()

def get_daily_prices_history(sku_id, days=7):
    """Получает историю ежедневных цен за последние N дней"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT price, price_source, price_date, created_at
            FROM DailyPrices
            WHERE sku_id = ?
            ORDER BY price_date DESC
            LIMIT ?
        ''', (sku_id, days))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Ошибка при получении истории ежедневных цен: {e}")
        return []
    finally:
        conn.close()

def get_today_prices():
    """Получает все цены на сегодняшний день"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT s.article, s.product_name, dp.price, dp.price_source, dp.created_at
            FROM DailyPrices dp
            JOIN SKU s ON dp.sku_id = s.id
            WHERE dp.price_date = ?
            ORDER BY dp.created_at DESC
        ''', (today,))
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Ошибка при получении цен на сегодня: {e}")
        return []
    finally:
        conn.close()

def get_stats():
    """Получает статистику по базе данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Общее количество товаров
        cursor.execute('SELECT COUNT(*) FROM SKU')
        total_skus = cursor.fetchone()[0]
        
        # Количество активных связей пользователей с товарами
        cursor.execute('SELECT COUNT(*) FROM UserSKU WHERE is_active = 1')
        active_user_skus = cursor.fetchone()[0]
        
        # Количество уникальных пользователей
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM UserSKU WHERE is_active = 1')
        unique_users = cursor.fetchone()[0]
        
        # Количество записей в истории цен
        cursor.execute('SELECT COUNT(*) FROM PriceHistory')
        price_records = cursor.fetchone()[0]
        
        # Количество ежедневных записей цен
        cursor.execute('SELECT COUNT(*) FROM DailyPrices')
        daily_price_records = cursor.fetchone()[0]
        
        # Количество записей на сегодня
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM DailyPrices WHERE price_date = ?', (today,))
        today_records = cursor.fetchone()[0]
        
        return {
            'total_skus': total_skus,
            'active_user_skus': active_user_skus,
            'unique_users': unique_users,
            'price_records': price_records,
            'daily_price_records': daily_price_records,
            'today_records': today_records
        }
        
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")
        return {}
    finally:
        conn.close()

def daily_update_all_products():
    """Ежедневное обновление всех товаров"""
    from app import get_product_price
    import math
    import re
    
    print("Начинаем ежедневное обновление всех товаров...")
    
    # Получаем все активные товары
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT DISTINCT s.id, s.article, s.product_name, s.current_price, s.price_source, s.product_url
            FROM SKU s
            JOIN UserSKU us ON s.id = us.sku_id
            WHERE us.is_active = 1
        ''')
        
        products = cursor.fetchall()
        
        if not products:
            print("Нет активных товаров для обновления")
            return
        
        print(f"Найдено {len(products)} товаров для обновления")
        
        updated_count = 0
        error_count = 0
        
        for sku_id, article, current_name, current_price, price_source, product_url in products:
            try:
                print(f"Обновляем товар {article}...")
                
                # Формируем URL если его нет
                if not product_url:
                    product_url = f"https://www.ozon.ru/product/{article}/"
                
                # Получаем актуальную информацию о товаре
                result = get_product_price(product_url)
                
                if isinstance(result, dict):
                    new_name = result.get('name', current_name)
                    new_price = result.get('price', current_price)
                    new_source = result.get('source', price_source)
                    
                    # Извлекаем только число из цены и округляем в большую сторону
                    price_match = re.search(r'([\d\s,]+)', new_price)
                    if price_match:
                        price_str = price_match.group(1).replace(' ', '').replace(',', '')
                        try:
                            price_value = str(math.ceil(float(price_str)))
                        except (ValueError, TypeError):
                            price_value = current_price
                    else:
                        price_value = current_price
                    
                    # Обновляем товар в основной таблице
                    cursor.execute('''
                        UPDATE SKU 
                        SET product_name = ?, current_price = ?, price_source = ?, last_updated = ?, product_url = ?
                        WHERE id = ?
                    ''', (new_name, price_value, new_source, datetime.now(), product_url, sku_id))
                    
                    # Добавляем запись в историю цен
                    cursor.execute('''
                        INSERT INTO PriceHistory (sku_id, price, price_source, recorded_at)
                        VALUES (?, ?, ?, ?)
                    ''', (sku_id, price_value, new_source, datetime.now()))
                    
                    # Добавляем запись в ежедневные цены
                    today = datetime.now().strftime('%Y-%m-%d')
                    cursor.execute('''
                        INSERT OR REPLACE INTO DailyPrices (sku_id, price, price_source, price_date, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (sku_id, price_value, new_source, today, datetime.now()))
                    
                    updated_count += 1
                    try:
                        print(f"OK: {new_name[:50]}... - {price_value} ₽")
                    except UnicodeEncodeError:
                        print(f"OK: {new_name[:50].encode('ascii', 'replace').decode('ascii')}... - {price_value} руб")
                    
                else:
                    error_count += 1
                    print(f"ERROR: Не удалось получить данные для товара {article}")
                
                # Небольшая пауза между запросами
                import time
                time.sleep(1)
                
            except Exception as e:
                error_count += 1
                print(f"ERROR: Ошибка при обновлении товара {article}: {e}")
        
        conn.commit()
        print(f"\nЕжедневное обновление завершено:")
        print(f"  Обновлено товаров: {updated_count}")
        print(f"  Ошибок: {error_count}")
        
    except Exception as e:
        print(f"Ошибка при ежедневном обновлении: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_products_for_daily_update():
    """Получает список товаров для ежедневного обновления"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT DISTINCT s.id, s.article, s.product_name, s.current_price, s.price_source, s.product_url
            FROM SKU s
            JOIN UserSKU us ON s.id = us.sku_id
            WHERE us.is_active = 1
            ORDER BY s.article
        ''')
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Ошибка при получении товаров для обновления: {e}")
        return []
    finally:
        conn.close()

def get_daily_update_stats():
    """Получает статистику ежедневного обновления"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Количество товаров для обновления
        cursor.execute('''
            SELECT COUNT(DISTINCT s.id)
            FROM SKU s
            JOIN UserSKU us ON s.id = us.sku_id
            WHERE us.is_active = 1
        ''')
        total_products = cursor.fetchone()[0]
        
        # Количество обновлений за последние 7 дней
        cursor.execute('''
            SELECT COUNT(DISTINCT sku_id)
            FROM DailyPrices
            WHERE price_date >= date('now', '-7 days')
        ''')
        recent_updates = cursor.fetchone()[0]
        
        # Последнее обновление
        cursor.execute('''
            SELECT MAX(price_date)
            FROM DailyPrices
        ''')
        last_update = cursor.fetchone()[0]
        
        return {
            'total_products': total_products,
            'recent_updates': recent_updates,
            'last_update': last_update
        }
        
    except Exception as e:
        print(f"Ошибка при получении статистики обновления: {e}")
        return {
            'total_products': 0,
            'recent_updates': 0,
            'last_update': None
        }
    finally:
        conn.close()

# Инициализируем базу данных при импорте
if __name__ == "__main__":
    init_database()
    print("База данных готова к работе!")
else:
    init_database()
