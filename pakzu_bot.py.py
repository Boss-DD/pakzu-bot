Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import telebot

# === НАСТРОЙКИ ===
TOKEN = '7627809698:AAGV9AUSB4_JmF6GPKq8La4BEOyFYK0JH8U'
YUAN_RATE = 13          # курс юаня
USD_RATE = 90           # курс доллара
DELIVERY_RATE = 3.3     # $/кг доставка

ADMIN_USERNAME = '@boss_dd'  # для уведомлений

bot = telebot.TeleBot(TOKEN)

user_data = {}

# === ХОД РАБОТЫ ===

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "Привет! Пришли ссылку на товар или его описание:")
    bot.register_next_step_handler(message, get_link)

def get_link(message):
    user_data[message.chat.id]['link'] = message.text
    bot.send_message(message.chat.id, "Введи цену за 1 шт в юанях:")
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    try:
...         user_data[message.chat.id]['price'] = float(message.text)
...         bot.send_message(message.chat.id, "Сколько стоит доставка по Китаю (в юанях)?")
...         bot.register_next_step_handler(message, get_domestic_delivery)
...     except:
...         bot.send_message(message.chat.id, "Пожалуйста, введи число.")
...         bot.register_next_step_handler(message, get_price)
... 
... def get_domestic_delivery(message):
...     try:
...         user_data[message.chat.id]['cn_delivery'] = float(message.text)
...         bot.send_message(message.chat.id, "Укажи вес 1 штуки в кг:")
...         bot.register_next_step_handler(message, get_weight)
...     except:
...         bot.send_message(message.chat.id, "Пожалуйста, введи число.")
...         bot.register_next_step_handler(message, get_domestic_delivery)
... 
... def get_weight(message):
...     try:
...         user_data[message.chat.id]['weight'] = float(message.text)
...         bot.send_message(message.chat.id, "Сколько штук нужно заказать?")
...         bot.register_next_step_handler(message, get_quantity)
...     except:
...         bot.send_message(message.chat.id, "Пожалуйста, введи число.")
...         bot.register_next_step_handler(message, get_weight)
... 
... def get_quantity(message):
...     try:
...         user_data[message.chat.id]['quantity'] = int(message.text)
... 
...         data = user_data[message.chat.id]
...         total_price = (data['price'] + data['cn_delivery']) * YUAN_RATE * data['quantity']
...         total_weight = data['weight'] * data['quantity']
...         delivery_cost = total_weight * DELIVERY_RATE * USD_RATE
...         final_total = round(total_price + delivery_cost, 2)
... 
...         response = (
...             f"💰 Стоимость товара: {round(total_price, 2)} ₽\n"
...             f"📦 Доставка до РФ: {round(delivery_cost, 2)} ₽\n"
...             f"🔢 Итого: {final_total} ₽"
...         )
... 
...         bot.send_message(message.chat.id, response)
... 
...         # Уведомление администратору
...         admin_msg = (
...             f"📥 Новый расчёт от @{message.chat.username or 'неизвестно'}:\n\n"
...             f"🛒 Товар: {data['link']}\n"
...             f"Цена: {data['price']} юаней\n"
...             f"Доставка по Китаю: {data['cn_delivery']} юаней\n"
...             f"Вес 1 шт: {data['weight']} кг\n"
...             f"Кол-во: {data['quantity']}\n\n"
...             f"💰 Итого: {final_total} ₽"
...         )
...         bot.send_message(ADMIN_USERNAME, admin_msg)
... 
...     except:
...         bot.send_message(message.chat.id, "Пожалуйста, введи корректное количество.")
...         bot.register_next_step_handler(message, get_quantity)
... 
... # === ЗАПУСК ===
bot.polling()