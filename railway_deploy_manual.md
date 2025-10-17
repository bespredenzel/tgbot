# Ручной деплой на Railway

## Способ 1: Railway CLI

1. **Установите Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Войдите в Railway:**
   ```bash
   railway login
   ```

3. **Инициализируйте проект:**
   ```bash
   railway init
   ```

4. **Загрузите код:**
   ```bash
   railway up
   ```

## Способ 2: Прямая загрузка ZIP

1. **Создайте ZIP архив** с файлами проекта
2. **В Railway Dashboard** выберите "Deploy from ZIP"
3. **Загрузите архив**

## Способ 3: Подключение через URL

1. **В Railway Dashboard** выберите "Deploy from GitHub repo"
2. **Введите полный URL:** `https://github.com/bespredenzel/tgbot`
3. **Нажмите "Deploy"**

## Способ 4: Создание нового репозитория

1. **Создайте новый репозиторий** с другим именем
2. **Загрузите код туда**
3. **Попробуйте деплой снова**

## Необходимые переменные окружения:

```
BOT_TOKEN=8466699669:AAFkayv3f9JQmkNJsrvXV32oFMmkWlIMTCc
FLASK_ENV=production
```
