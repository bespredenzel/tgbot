# Render.com Deployment Configuration

## Файл render.yaml
```yaml
services:
  - type: web
    name: price-monitor-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py & python telegram_bot.py
    envVars:
      - key: BOT_TOKEN
        value: 8466699669:AAFkayv3f9JQmkNJsrvXV32oFMmkWlIMTCc
      - key: FLASK_ENV
        value: production
```

## Инструкция по деплою на Render:

1. **Откройте** https://render.com
2. **Войдите** через GitHub
3. **Нажмите** "New +" → "Web Service"
4. **Подключите** репозиторий `bespredenzel/tgbot`
5. **Настройте:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py & python telegram_bot.py`
   - **Environment Variables:**
     - `BOT_TOKEN=8466699669:AAFkayv3f9JQmkNJsrvXV32oFMmkWlIMTCc`
     - `FLASK_ENV=production`
6. **Нажмите** "Create Web Service"

## Преимущества Render:
- ✅ Бесплатный план
- ✅ Автоматический HTTPS
- ✅ Простая интеграция с GitHub
- ✅ Автоматический деплой при изменениях
