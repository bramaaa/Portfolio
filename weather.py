import telebot
from telebot import types
import requests
from datetime import datetime

BOT_TOKEN = "8579257495:AAGKMA_hLougp73J_ByteA6bKPSqgOXDKn8"
API_KEY = "3dd1e89da7e43f78823e7b4c18c6a809"

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🌍 Моя локація", request_location=True)
    btn2 = types.KeyboardButton("🏙 Введи місто")

    markup.add(btn1)
    markup.add(btn2)

    bot.send_message(
        message.chat.id,
        "Вибери опцію:",
        reply_markup=markup
    )



@bot.message_handler(content_types=["location"])
def get_location(message):
    lat = message.location.latitude
    lon = message.location.longitude

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&units=metric&lang=ua&appid={API_KEY}"
    )

    send_weather(message.chat.id, url)



@bot.message_handler(func=lambda message: message.text == "🏙 Введи місто")
def ask_city(message):
    msg = bot.send_message(message.chat.id, "Введи назву міста:")
    bot.register_next_step_handler(msg, city_weather)



def city_weather(message):
    city = message.text

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&units=metric&lang=ua&appid={API_KEY}"
    )

    send_weather(message.chat.id, url)


def send_weather(chat_id, url):
    try:
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            bot.send_message(chat_id, "❌ Місто не знайдено.")
            return

        city = data["name"]
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        description = data["weather"][0]["description"].capitalize()

        sunrise = datetime.fromtimestamp(
            data["sys"]["sunrise"]
        ).strftime("%H:%M")

        sunset = datetime.fromtimestamp(
            data["sys"]["sunset"]
        ).strftime("%H:%M")

        text = (
            f"🌍 <b>{city}</b>\n\n"
            f"🌡 Температура: {temp}°C\n"
            f"🤗 Відчуваеться як: {feels}°C\n"
            f"💧 Вологість: {humidity}%\n"
            f"💨 Вітер: {wind} m/s\n"
            f"☁  Небо: {description}\n"
            f"🌅 Схід Сонця: {sunrise}\n"
            f"🌇 Захід: {sunset}"
        )

        bot.send_message(chat_id, text, parse_mode="HTML")

    except Exception as e:
        bot.send_message(chat_id, f"Error:\n{e}")



@bot.message_handler(func=lambda message: True)
def text_handler(message):
    city_weather(message)

print("Bot started...")

bot.infinity_polling(skip_pending=True)