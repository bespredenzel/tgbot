# Fly.io Deployment Guide

## Настройка деплоя на Fly.io (бесплатно)

### 1. Установка Fly CLI
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

### 2. Логин в Fly.io
```bash
fly auth login
```

### 3. Создание приложения
```bash
fly launch --no-deploy
```

### 4. Настройка переменных окружения
```bash
fly secrets set BOT_TOKEN=8466699669:AAFkayv3f9JQmkNJsrvXV32oFMmkWlIMTCc
fly secrets set FLASK_ENV=production
```

### 5. Деплой
```bash
fly deploy
```

## Преимущества Fly.io:
- ✅ Бесплатный тариф с 3 приложениями
- ✅ Автоматический HTTPS
- ✅ Глобальная сеть
- ✅ Простой деплой через CLI
