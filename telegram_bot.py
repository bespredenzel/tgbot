import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (замените на ваш токен от @BotFather)
BOT_TOKEN = "8466699669:AAFkayv3f9JQmkNJsrvXV32oFMmkWlIMTCc"

def generate_math_question():
    """Генерирует случайный пример из таблицы умножения"""
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    correct_answer = a * b
    
    # Создаем неправильные варианты ответов
    wrong_answers = []
    while len(wrong_answers) < 3:
        wrong = correct_answer + random.randint(-10, 10)
        if wrong != correct_answer and wrong > 0 and wrong not in wrong_answers:
            wrong_answers.append(wrong)
    
    # Смешиваем правильный ответ с неправильными
    all_answers = [correct_answer] + wrong_answers
    random.shuffle(all_answers)
    
    return {
        'question': f"{a} × {b} = ?",
        'correct_answer': correct_answer,
        'answers': all_answers
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Генерируем математический пример
    math_data = generate_math_question()
    
    # Сохраняем правильный ответ в контексте
    context.user_data['correct_answer'] = math_data['correct_answer']
    
    # Создаем кнопки с вариантами ответов
    keyboard = []
    for answer in math_data['answers']:
        keyboard.append([InlineKeyboardButton(str(answer), callback_data=f'answer_{answer}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"Привет, {user.mention_html()}!\n"
        f"Я простой Telegram бот.\n\n"
        f"🔢 Для подтверждения, что вы не бот, решите пример:\n"
        f"<b>{math_data['question']}</b>\n\n"
        f"Выберите правильный ответ:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатия на кнопку"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('answer_'):
        # Извлекаем выбранный ответ
        selected_answer = int(query.data.split('_')[1])
        correct_answer = context.user_data.get('correct_answer')
        
        if correct_answer is None:
            await query.edit_message_text("❌ Ошибка: попробуйте снова /start")
            return
        
        if selected_answer == correct_answer:
            # Правильный ответ — показываем кнопку, открывающую приложение Telegram через deep link
            user = update.effective_user
            user_id = str(user.id)  # Получаем ID пользователя
            app_url = f'https://your-app-name.railway.app/?user_id={user_id}'
            
            keyboard = [
                [InlineKeyboardButton("🚀 Открыть приложение", web_app=WebAppInfo(url=app_url))]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "✅ Правильно! Вы прошли проверку.\n\n"
                f"🆔 Ваш ID: {user_id}\n"
                "Нажмите кнопку ниже, чтобы открыть приложение:",
                reply_markup=reply_markup
            )
        else:
            # Неправильный ответ - генерируем новый пример
            math_data = generate_math_question()
            context.user_data['correct_answer'] = math_data['correct_answer']
            
            keyboard = []
            for answer in math_data['answers']:
                keyboard.append([InlineKeyboardButton(str(answer), callback_data=f'answer_{answer}')])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ Неправильно! Попробуйте еще раз:\n\n"
                f"🔢 <b>{math_data['question']}</b>\n\n"
                f"Выберите правильный ответ:",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    


def main() -> None:
    """Основная функция для запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
