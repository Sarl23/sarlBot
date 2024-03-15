from dotenv import load_dotenv
from telebot import TeleBot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import os
import re

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
# Retrieve API token from environment variable
API_TOKEN = os.getenv('API_TOKEN')
bot = TeleBot(API_TOKEN)
# Cantidad máxima de intentos permitidos
MAX_ATTEMPTS = 3
# Diccionario para almacenar los intentos de validación por usuario
user_attempts = {}


@bot.message_handler(func=lambda message: re.search(r'\bhola|hi\b', message.text, re.IGNORECASE) is not None)
def bot_message_start(message):
    first_name = message.chat.first_name
    message_hi = f"Hola {first_name}, soy SarBot 🤖\n" \
                 f"Estoy para ayudarte en lo que necesites,\n" \
                 f"pero por ahora solo puedo con estas opciones 🥺:\n" \
                 f"📦 /revisar_mi_envio\n" \
                 f"💬 /habla_con_chatGPT\n" \
                 f"📔 /mis_recordatorios"
    bot.send_message(message.chat.id, message_hi)


# Comando /start
@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot_message_start(message)


@bot.message_handler(commands=['revisar_mi_envio'])
def cmd_scraping(message):
    chat_id = message.chat.id
    if chat_id not in user_attempts:
        user_attempts[chat_id] = 0
    if user_attempts[chat_id] >= MAX_ATTEMPTS:
        bot.send_message(chat_id, "Has superado el límite de intentos. Inténtalo más tarde.")
        del user_attempts[chat_id]
        bot_message_start(message)
        return
    # Prompt user to enter shipping code
    bot.send_message(chat_id, "Por favor, ingresa el código de envío:")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    # Verify if the previous message was a request for a sending code
    if chat_id in user_attempts and user_attempts[chat_id] < MAX_ATTEMPTS:
        # Validate the code to be sent to make the scrape page
        if message.text.strip() == "1234":
            bot.send_message(chat_id, "El código de envío es correcto.")
            scraping_with_code(message.text.strip())
            del user_attempts[chat_id]
        else:
            user_attempts[chat_id] += 1
            attempts_left = MAX_ATTEMPTS - user_attempts[chat_id]
            if attempts_left > 0:
                bot.send_message(chat_id, f"Código incorrecto. Te quedan {attempts_left} intentos.")
            else:
                bot.send_message(chat_id, "Has superado el límite de intentos. Inténtalo más tarde.")
                del user_attempts[chat_id]
                bot_message_start(message)
    else:
        bot.send_message(chat_id, "Por ahora no te entiendo 😭, solo puedo hacer esas opciones")


def scraping_with_code(code):
    print(code)
    options = Options()
    options.add_argument("--disable-web-security")
    options.add_argument("--disabled-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--headless")
    options.add_argument("disable-gpu")
    options.add_argument("no-sandbox")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get('https://coordinadora.com/rastreo/rastreo-de-guia/detalle-de-rastreo-de-guia/')
        sleep(3)
        print('abrio el link')
    finally:
        sleep(4)
        driver.quit()
        print('cerro el link')


if __name__ == '__main__':
    print('Start Bot')
    bot.polling()
    print("End Bot")
