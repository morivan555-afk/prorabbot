import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# Настройка Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """Ты опытный ассистент по ремонту квартиры. Твоё имя — «Прораб». 
Пользователь только начинает планировать ремонт и ему важны три вещи:
1. Планирование и бюджет — помоги составить план этапов ремонта, сметы, расставить приоритеты
2. Поиск мастеров и подрядчиков — на что обращать внимание, как проверить, какие вопросы задавать, как не нарваться на мошенников
3. Советы и лайфхаки — практические советы, на чём сэкономить, типичные ошибки, что делать самому а что лучше доверить профи

Отвечай чётко, структурированно и по делу. Используй списки и цифры там где это уместно. 
Если нужна конкретика (площадь, тип ремонта, бюджет) — уточняй. 
Всегда будь на стороне пользователя: предупреждай о рисках и помогай сэкономить.
Отвечай в Telegram — без лишнего форматирования, коротко и ясно."""

# История диалогов для каждого пользователя
user_chats = {}

def get_chat(user_id):
    if user_id not in user_chats:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        user_chats[user_id] = model.start_chat(history=[])
    return user_chats[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    await update.message.reply_text(
        "👷 Привет! Я Прораб — твой ассистент по ремонту.\n\n"
        "Помогу:\n"
        "📋 Спланировать ремонт с нуля\n"
        "💰 Составить смету и не вылететь из бюджета\n"
        "👷 Найти надёжных мастеров\n"
        "💡 Разобраться с лайфхаками и ошибками\n\n"
        "Просто напиши свой вопрос!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        chat = get_chat(user_id)
        response = chat.send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("Что-то пошло не так. Попробуй ещё раз или напиши /start")

def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
