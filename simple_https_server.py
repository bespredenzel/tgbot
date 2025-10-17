#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой HTTPS сервер для Telegram Web App с правильной настройкой
"""

import ssl
import threading
import time
import requests
import json
from flask import Flask, request, jsonify, render_template_string
import urllib.parse
import re
from datetime import datetime
import os
from database import (
    add_or_update_sku, add_user_sku, get_user_skus, 
    get_sku_by_article, get_price_history, get_stats,
    get_daily_price_by_article, add_daily_price, get_today_prices
)

# Импортируем функции из основного приложения
try:
    from app import (
        get_product_price, verify_telegram_webapp_data, 
        get_user_id_from_telegram_data, PAGE
    )
except ImportError as e:
    print(f"Ошибка импорта из app.py: {e}")

app = Flask(__name__)

# Настройки сервера
HOST = '0.0.0.0'
HTTP_PORT = 5000
HTTPS_PORT = 5443
SSL_CERT = 'server.crt'
SSL_KEY = 'server.key'

def check_ssl_files():
    """Проверяет наличие SSL файлов"""
    if not os.path.exists(SSL_CERT) or not os.path.exists(SSL_KEY):
        print("SSL сертификаты не найдены!")
        return False
    return True

def create_ssl_context():
    """Создает SSL контекст"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(SSL_CERT, SSL_KEY)
    return context

# Главная страница
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    article = None
    
    # Получаем user_id из параметров URL или из Telegram Web App данных
    user_id = request.args.get('user_id', 'anonymous')
    
    # Проверяем, есть ли данные Telegram Web App
    telegram_init_data = request.headers.get('X-Telegram-Init-Data', '')
    if telegram_init_data:
        try:
            telegram_user_id = get_user_id_from_telegram_data(telegram_init_data)
            if telegram_user_id:
                user_id = telegram_user_id
        except:
            pass
    
    current_date = datetime.now().strftime("%d.%m.%Y")

    if request.method == "POST":
        article = request.form.get("article", "").strip()
        if article:
            try:
                # Получаем цену товара
                product_url = f"https://www.ozon.ru/product/{article}/"
                price_data = get_product_price(product_url)
                
                # Извлекаем данные
                if isinstance(price_data, dict):
                    price_text = price_data.get("price", "Не найдена")
                    product_name = price_data.get("name", f"Товар {article}")
                    source = price_data.get("source", "Selenium")
                    
                    # Извлекаем только число из цены
                    price_match = re.search(r'([\d\s,]+)', price_text)
                    price = price_match.group(1).strip() if price_match else "Не найдена"
                else:
                    price_match = re.search(r'([\d\s,]+)\s*₽', price_data)
                    price = price_match.group(1).strip() if price_match else "Не найдена"
                    product_name = f"Товар {article}"
                    source = "Selenium"
                
                # Сохраняем в базу данных
                sku_id = add_or_update_sku(
                    article=article,
                    product_name=product_name,
                    current_price=price,
                    price_source=source,
                    product_url=product_url
                )
                
                # Добавляем связь пользователя с товаром
                if user_id != 'anonymous':
                    add_user_sku(user_id, sku_id)
                
                result = f'''
                <a href="https://www.ozon.ru/product/{article}/" target="_blank" style="color: #3b82f6; text-decoration: none; font-weight: 600;">Товар на Ozon.ru</a><br><br>
                <strong>Цена на {current_date}:</strong> {price} ₽ ({source})<br><br>
                <small style="color: #64748b;">Товар добавлен в ваш список отслеживания</small>
                '''
            except Exception as e:
                result = f"Ошибка при получении цены: {str(e)}"

    # Получаем товары пользователя
    products = []
    if user_id != 'anonymous':
        try:
            products = get_user_skus(user_id)
        except:
            pass

    # Определяем текущую страницу
    current_page = 'search'
    if request.path == '/my-products':
        current_page = 'products'

    return render_template_string(PAGE, 
                                user_id=user_id, 
                                result=result, 
                                article=article,
                                products=products,
                                current_page=current_page)

@app.route("/my-products")
def my_products():
    user_id = request.args.get('user_id', 'anonymous')
    products = []
    
    try:
        products = get_user_skus(user_id) if user_id != 'anonymous' else []
    except:
        pass
    
    product_rows = []
    for product in products:
        product_rows.append(f'''
        <tr>
            <td>{product.article}</td>
            <td>{product.product_name}</td>
            <td>{product.current_price}</td>
            <td>{product.price_source}</td>
            <td>{product.last_updated}</td>
            <td>
                <a href="{product.product_url}" target="_blank" class="product-link">Открыть</a> |
                <a href="/dashboard/{product.article}?user_id={user_id}" class="product-link dashboard">График</a> |
                <a href="/delete-product/{product.article}?user_id={user_id}" class="product-link delete" onclick="return confirm('Удалить товар из списка?')">Удалить</a>
            </td>
        </tr>
        ''')
    
    my_products_html = f'''
    <!doctype html>
    <html lang="ru">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Мои товары</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
            .wrap {{ max-width: 680px; margin: 0 auto; padding: 32px 20px; }}
            .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,.35); }}
            h1 {{ margin: 0 0 12px; font-size: 24px; }}
            p {{ margin: 8px 0 16px; color: #cbd5e1; }}
            .btn {{ display: inline-block; background: #22c55e; color: #052e12; font-weight: 700; border-radius: 8px; padding: 12px 20px; text-decoration: none; border: none; cursor: pointer; font-size: 16px; margin-right: 12px; }}
            .btn:hover {{ background: #16a34a; }}
            .products-table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
            .products-table th, .products-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #374151; }}
            .products-table th {{ background: #1f2937; color: #e2e8f0; font-weight: 600; }}
            .products-table td {{ color: #cbd5e1; }}
            .products-table tr:hover {{ background: #1f2937; }}
            .product-link {{ color: #3b82f6; text-decoration: none; }}
            .product-link:hover {{ text-decoration: underline; }}
            .product-link.delete {{ color: #ef4444; }}
            .product-link.delete:hover {{ color: #dc2626; }}
            .product-link.dashboard {{ color: #10b981; }}
            .product-link.dashboard:hover {{ color: #059669; }}
            .empty-state {{ text-align: center; padding: 40px; color: #64748b; }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <h1>Мои товары</h1>
            <a href="/?user_id={user_id}" class="btn">← Добавить новый товар</a>
            <table class="products-table">
                <thead>
                    <tr>
                        <th>Артикул</th>
                        <th>Название</th>
                        <th>Цена, Руб.</th>
                        <th>Источник</th>
                        <th>Обновлено</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(product_rows)}
                </tbody>
            </table>
        </div>
        
        <script>
            // Инициализация Telegram Web App
            if (window.Telegram && window.Telegram.WebApp) {{
                const tg = window.Telegram.WebApp;
                tg.expand();
                tg.ready();
                
                const user = tg.initDataUnsafe?.user;
                if (user) {{
                    console.log('Telegram User:', user);
                }}
                
                tg.MainButton.setText('Готово');
                tg.MainButton.hide();
                
                tg.onEvent('mainButtonClicked', function() {{
                    tg.close();
                }});
            }}
        </script>
    </body>
    </html>
    '''
    return my_products_html

@app.route("/api/update-stats")
def api_update_stats():
    """API для получения статистики обновлений"""
    try:
        from database import get_daily_update_stats
        stats = get_daily_update_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, 500

@app.route("/api/daily-update")
def api_daily_update():
    """API для запуска ежедневного обновления"""
    try:
        from database import daily_update_all_products, get_daily_update_stats
        stats_before = get_daily_update_stats()
        daily_update_all_products()
        stats_after = get_daily_update_stats()
        return {
            "success": True,
            "message": "Ежедневное обновление завершено",
            "stats_before": stats_before,
            "stats_after": stats_after,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, 500

def start_http_server():
    """Запускает HTTP сервер"""
    print(f"Запуск HTTP сервера на порту {HTTP_PORT}...")
    app.run(host=HOST, port=HTTP_PORT, debug=False, use_reloader=False, threaded=True)

def start_https_server():
    """Запускает HTTPS сервер"""
    if not check_ssl_files():
        print("Создаем SSL сертификаты...")
        os.system("python create_certs.py")
        
        if not check_ssl_files():
            print("Не удалось создать SSL сертификаты")
            return
    
    print(f"Запуск HTTPS сервера на порту {HTTPS_PORT}...")
    context = create_ssl_context()
    
    app.run(
        host=HOST, 
        port=HTTPS_PORT, 
        debug=False, 
        use_reloader=False,
        ssl_context=context,
        threaded=True
    )

def get_public_ip():
    """Получает публичный IP адрес"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            return response.json().get('ip')
    except:
        pass
    return None

def main():
    print("HTTPS сервер для Telegram Web App")
    print("=" * 40)
    
    # Получаем публичный IP
    public_ip = get_public_ip()
    if public_ip:
        print(f"Публичный IP: {public_ip}")
        print(f"HTTPS URL: https://{public_ip}:{HTTPS_PORT}")
    else:
        print("Не удалось получить публичный IP")
        print(f"Локальный HTTPS URL: https://localhost:{HTTPS_PORT}")
    
    print("\nЗапуск серверов...")
    
    # Запускаем HTTP сервер в отдельном потоке
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # Небольшая задержка
    time.sleep(2)
    
    # Запускаем HTTPS сервер в основном потоке
    try:
        start_https_server()
    except KeyboardInterrupt:
        print("\nОстановка серверов...")

if __name__ == "__main__":
    main()
