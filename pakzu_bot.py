import telebot
import re
from telebot import types

# === НАСТРОЙКИ ===
TOKEN = '7627809698:AAGV9AUSB4_JmF6GPKq8La4BEOyFYK0JH8U'
YUAN_RATE = 13          # курс юаня
USD_RATE = 90           # курс доллара
DELIVERY_RATE = 3.3     # $/кг доставка
ADMIN_USERNAME = '@boss_dd'  # для уведомлений

bot = telebot.TeleBot(TOKEN)
user_data = {}

# === ГЛАВНОЕ МЕНЮ ===
def main_menu(chat_id, text="Выбери действие из меню:"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔁 Новый расчёт", "ℹ️ Помощь", "📞 Контакты")
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id, "Привет! Я помогу рассчитать доставку из Китая 🇨🇳 ➡️ 🇷🇺")

@bot.message_handler(func=lambda m: True)
def menu_handler(message):
    if message.text == "🔁 Новый расчёт":
        user_data[message.chat.id] = {}

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Пропустить")
        bot.send_message(message.chat.id, "Пришли ссылку на товар или его описание:", reply_markup=markup)
        bot.register_next_step_handler(message, get_link)

    elif message.text == "ℹ️ Помощь":
        bot.send_message(message.chat.id, "Чтобы рассчитать доставку:\n\n1. Выберите 'Новый расчёт'\n2. Заполните все шаги\n3. Получите итоговую цену 💰")

    elif message.text == "📞 Контакты":
        bot.send_message(message.chat.id, "Связаться с нами: @boss_dd")

    else:
        bot.send_message(message.chat.id, "Я тебя не понял. Выбери вариант из меню:")
        main_menu(message.chat.id)

# === ЭТАПЫ ===

def get_link(message):
    text = message.text.strip()

    if text.lower() == "пропустить":
        user_data[message.chat.id]['link'] = "Без ссылки (ввод вручную)"
    else:
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        if not url_pattern.search(text):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("Пропустить")
            bot.send_message(message.chat.id, "❗️Пожалуйста, пришли корректную ссылку или нажми 'Пропустить'.", reply_markup=markup)
            bot.register_next_step_handler(message, get_link)
            return
        user_data[message.chat.id]['link'] = text

    bot.send_message(message.chat.id, "Введи цену за 1 шт в юанях:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    try:
        user_data[message.chat.id]['price'] = float(message.text)
        bot.send_message(message.chat.id, "Сколько стоит доставка по Китаю (в юанях)?")
        bot.register_next_step_handler(message, get_domestic_delivery)
    except:
        bot.send_message(message.chat.id, "Пожалуйста, введи число.")
        bot.register_next_step_handler(message, get_price)

def get_domestic_delivery(message):
    try:
        user_data[message.chat.id]['cn_delivery'] = float(message.text)
        bot.send_message(message.chat.id, "Укажи вес 1 штуки в кг:")
        bot.register_next_step_handler(message, get_weight)
    except:
        bot.send_message(message.chat.id, "Пожалуйста, введи число.")
        bot.register_next_step_handler(message, get_domestic_delivery)

def get_weight(message):
    try:
        user_data[message.chat.id]['weight'] = float(message.text)
        bot.send_message(message.chat.id, "Сколько штук нужно заказать?")
        bot.register_next_step_handler(message, get_quantity)
    except:
        bot.send_message(message.chat.id, "Пожалуйста, введи число.")
        bot.register_next_step_handler(message, get_weight)

def get_quantity(message):
    try:
        user_data[message.chat.id]['quantity'] = int(message.text)
        data = user_data[message.chat.id]

        total_price = (data['price'] + data['cn_delivery']) * YUAN_RATE * data['quantity']
        total_weight = data['weight'] * data['quantity']
        delivery_cost = total_weight * DELIVERY_RATE * USD_RATE
        final_total = round(total_price + delivery_cost, 2)
response = (
            f"💰 Стоимость товара: {round(total_price, 2)} ₽\n"
            f"📦 Доставка до РФ: {round(delivery_cost, 2)} ₽\n"
            f"🔢 Итого: {final_total} ₽"
        )

        bot.send_message(message.chat.id, response)

        admin_msg = (
            f"📥 Новый расчёт от @{message.chat.username or 'неизвестно'}:\n\n"
            f"🛒 Товар: {data['link']}\n"
            f"Цена: {data['price']} юаней\n"
            f"Доставка по Китаю: {data['cn_delivery']} юаней\n"
            f"Вес 1 шт: {data['weight']} кг\n"
            f"Кол-во: {data['quantity']}\n\n"
            f"💰 Итого: {final_total} ₽"
        )
        bot.send_message(ADMIN_USERNAME, admin_msg)

        # Возврат в главное меню
        main_menu(message.chat.id, "✅ Готово! Выбери следующее действие:")
        
    except:
        bot.send_message(message.chat.id, "Пожалуйста, введи корректное количество.")
        bot.register_next_step_handler(message, get_quantity)

# === ЗАПУСК ===
bot.polling()