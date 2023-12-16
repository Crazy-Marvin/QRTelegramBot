import os

# QR Code Modules

import cv2
import numpy
from io import BytesIO
from qrcode import make

# Telegram Bot API modules

import telebot
from telebot.types import WebAppInfo
from telebot.types import KeyboardButton
from telebot.types import ReplyKeyboardMarkup
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from telebot.types import InputTextMessageContent
from telebot.types import InlineQueryResultArticle
from telebot.types import InlineQueryResultCachedPhoto

# Analytics modules

import gspread
from oauth2client.service_account import ServiceAccountCredentials

API_TOKEN = os.getenv("API_KEY")
STORAGE_CHANNEL = os.getenv("STORAGE_CHANNEL")
WEB_APP_URL = "https://telegramqrcodetelegrambot.herokuapp.com/"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

database = client.open("DATABASE").worksheet("QR BOT")
analytics = client.open("ANALYTICS").worksheet("QR BOT")

def add_logs(cell):
    analytics.update_acell(cell,
        str(int(analytics.acell(cell).value) + 1).replace("'", " "))

@bot.message_handler(commands=["start"])
def start(message):

    add_logs("F3")
    col = database.col_values(1)

    if str(message.chat.id) not in col:
        database.append_row([message.chat.id])
        analytics.update_acell('F10', str(len(col)).replace("'", " "))

    bot.send_message(message.chat.id, "<b>Hi there! Welcome to the world of QR Codes!\n\
        \nI can help you to make /new QR codes or even /read existing ones!\n\
        \nYou can also use me inline in any chat! Just type @QRCodeTelegramBot followed by any text you want and I will generate a QR Code for you!\n\
        \nFor more information, send /help. Enjoy 🎉</b>")

@bot.message_handler(commands=["read"])
def read(message):
    add_logs("F4")
    bot.send_message(message.chat.id,
        "<b>To read a QR Code, simply send the image containing the QR Code!\n\
        \nNOTE: Send good resolution images for better results 😄\n\
        \nYou can also scan QR Codes live using the button below 👇🏻</b>",
        reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(
            "SCAN NOW 🔍", callback_data="web_app")))

@bot.message_handler(commands=["help"])
def help(message):
    add_logs("F6")
    bot.send_message(message.chat.id, "<b>/new - Generate all sorts of QR Code\n\
        \n/read - Read a QR Code\n\
        \nUse the Web App to scan live QR Codes. [It has some bugs 🥴]\n\
        \nGive me a feedback on the web app ➜ @tech_savvy_guy</b>")

@bot.message_handler(commands=["contact"])
def contact(message):
    contact_info = '''
        <b>CONTACT :\n\
        \n➤ Telegram: https://t.me/Marvin_Marvin\n\
        \n➤ E-Mail: marvin@poopjournal.rocks\n\
        \n➤ Issue: https://github.com/Crazy-Marvin/QRTelegramBot/issues\n\
        \n➤ Source: https://github.com/Crazy-Marvin/QRTelegramBot</b>
    '''

    add_logs("F7")
    bot.send_message(message.chat.id, contact_info)

@bot.message_handler(commands=["feedback"])
def feedback(message):
    add_logs("F8")
    bot.send_message(message.chat.id, "<b>Send a feedback ➜ @Marvin_Marvin</b>")

@bot.message_handler(commands=["new"])
def new(message):
    add_logs("F5")
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(*[
        InlineKeyboardButton("TEXT 📝", callback_data="text"),
        InlineKeyboardButton("SMS 📳", callback_data="sms"),
        InlineKeyboardButton("WIFI 📶", callback_data="wifi"),
        InlineKeyboardButton("CONTACT 📞", callback_data="contact"),
        InlineKeyboardButton("EMAIL 📧", callback_data="email"),
        InlineKeyboardButton("EVENT 🎉", callback_data="event"),
        InlineKeyboardButton("CRYPTO 🤑", callback_data="crypto"),
        InlineKeyboardButton("LOCATION 📍", callback_data="location")])
    bot.send_message(message.chat.id, reply_markup=markup,
        text="<b>Choose the type of QR you want to generate 👇🏻</b>")

def read_qr(image):

    image_np = numpy.frombuffer(image, numpy.uint8)
    ImageData = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(ImageData)

    if bbox is not None:
        return f"<b>{data}</b>"
    else:
        return "<b>Sorry I could not recognize the QR Code!\n\
            \nTry using an image with a better resolution :)</b>"

def generate_qr(data):
    with BytesIO() as qr:
        qr_data = make(data)
        qr_data.save(qr, format="PNG")
        return qr.getvalue()

def analyze_qr(message, type):

    if type == "text":
        if message.content_type != "text":
            bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
        else:
            bot.send_photo(message.chat.id, generate_qr(message.text))

    elif type == "sms":
        if message.content_type != "text":
            bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
        else:   bot.send_photo(message.chat.id, generate_qr(f"smsto:{message.text}"))

    elif type == "crypto":
        if message.content_type != "text":
            bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
        else:
            crypto = message.text.split("::")
            if len(crypto) != 3:
                bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
            else:
                coin, wallet, amount = crypto
                bot.send_photo(message.chat.id, generate_qr(f"{coin}:{wallet}?amount={amount}"))        

    elif type == "event":
        if message.content_type != "text":
            bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
        else:
            event = message.text.split("::")
            if len(event) != 5:
                bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
            else:
                title, location, start, end, description = event
                bot.send_photo(message.chat.id, generate_qr(
            f"""BEGIN:VEVENT\
              \nSUMMARY:{title}\
              \nLOCATION:{location}\
              \nDTSTART: {start}\
              \nDTEND:{end}\
              \nDESCRIPTION:{description}\
              \nEND:VEVENT"""))

    elif type == "email":
        if message.content_type != "text":
            bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
        else:   bot.send_photo(message.chat.id, generate_qr(f"mailto:{message.text}"))

    elif type == "contact":
        if message.content_type != "contact":
            bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
        else:   
            bot.send_photo(message.chat.id, generate_qr(
      f"""BEGIN:VCARD\
        \nVERSION:3.0\
        \nN:{message.contact.first_name};{message.contact.last_name}\
        \nTEL:{message.contact.phone_number}\
        \nEND:VCARD"""))

    elif type == "location":
        if message.content_type != "location":
            bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
        else:   bot.send_photo(message.chat.id, generate_qr(
            f"geo:{message.location.latitude},{message.location.longitude}"))

    elif type == "wifi":
        if message.content_type != "text":
            bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
        else:
            wifi = message.text.split("::")
            if len(wifi) not in [2, 3]:
                bot.send_message(message.chat.id, "<b>INVALID INPUT! 😓</b>")
            else:
                if len(wifi) == 2:
                    wifi = f"WIFI:S:{wifi[0]};T:WPA;P:{wifi[-1]};;"
                elif len(wifi) == 3:
                    wifi = f"WIFI:S:{wifi[0]};T:{wifi[1]};P:{wifi[-1]};;"
                bot.send_photo(message.chat.id, generate_qr(wifi))

@bot.message_handler(content_types=["photo"])
def image_handler(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    image = bot.download_file(file_info.file_path)
    bot.send_message(message.chat.id, read_qr(image),
        reply_to_message_id=message.id)

def fetch_qr(image):
    photo = bot.send_photo(STORAGE_CHANNEL, image)
    return bot.get_file(photo.photo[-1].file_id).file_id

@bot.inline_handler(func=lambda query: True)
def inline_qr(query):
    try:
        info = InlineQueryResultArticle("info", "Create your own QR now!",
            input_message_content=InputTextMessageContent("<b>Welcome to the world of QR Codes!\n\
        \nI can help you to make new QR codes or even read existing ones!\n\
        \nYou can also use me inline in any chat! Just type @QRCodeTelegramBot followed by any text you want and I will generate a QR Code for you!\n\
        \nEnjoy 🎉 ➜ @QRCodeTelegramBot</b>", parse_mode="HTML"),
            description="Create amazing and personalized QR codes! 🤩",
            reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(
                "🔥 CHECK OUT OUR WEBSITE 🔥", url="https://crazymarvin.com/")),
                thumb_url="https://i.imgur.com/GelCxa8.png")
        if query.query == "":
            results = [info]
        else:
            storage_qr = InlineQueryResultCachedPhoto("storage_qr",
                fetch_qr(generate_qr(query.query)), title="Send the QR 👇🏻",
                description="Here's your generated QR Code",
                reply_markup=InlineKeyboardMarkup().row(
                    InlineKeyboardButton("Create your own personalized QR Codes!",
                    url="https://t.me/QRCodeTelegramBot")))
            results = [info, storage_qr]
        bot.answer_inline_query(query.id, results, 1,
        switch_pm_text="Create your own QR Codes!", switch_pm_parameter="inline")
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):

    chat_id = call.message.chat.id
    data, msg_id = call.data, call.message.id

    if data == "text":
        bot.delete_message(chat_id, msg_id)
        response = bot.send_message(chat_id, "<b>Send the text to encode 👉🏻</b>")
        bot.register_next_step_handler(response, analyze_qr, "text")
    
    elif data == "email":
        bot.delete_message(chat_id, msg_id)
        response = bot.send_message(chat_id, "<b>Send the E-Mail ID 👉🏻</b>")
        bot.register_next_step_handler(response, analyze_qr, "email")

    elif data == "sms":
        bot.delete_message(chat_id, msg_id)
        response = bot.send_message(chat_id,
            "<b>Send the phone number where you want to send the SMS 👉🏻</b>")
        bot.register_next_step_handler(response, analyze_qr, "sms")

    elif data == "crypto":
        bot.delete_message(chat_id, msg_id)
        response = bot.send_message(chat_id,
            "<b>Send the coin name, wallet address and the amount as shown below 👉🏻\n\
                \n<code>Coin::Wallet::Amount</code>\n\
                \nExamples: bitcoin, litecoin, dash, ethereum</b>")
        bot.register_next_step_handler(response, analyze_qr, "crypto")  

    elif data == "event":
        bot.delete_message(chat_id, msg_id)
        bot.send_message(chat_id, "Use this Web App to create a QR Code for an Event", 
            reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton("GENERATE QR CODE",
                web_app=WebAppInfo(WEB_APP_URL))))

    elif data == "contact":
        bot.delete_message(chat_id, msg_id)
        response = bot.send_message(chat_id, reply_markup=ReplyKeyboardMarkup(True, True).row(
            KeyboardButton("SHARE YOUR CONTACT ☎️", request_contact=True)),
        text="<b>Share your contact using the button below 👉🏻</b>")
        bot.register_next_step_handler(response, analyze_qr, "contact")

    elif data == "location":
        bot.delete_message(chat_id, msg_id)
        response = bot.send_message(chat_id, reply_markup=ReplyKeyboardMarkup(True, True).row(
            KeyboardButton("SHARE YOUR LOCATION 📍", request_location=True)),
        text="<b>Share your loaction using the button below 👉🏻</b>")
        bot.register_next_step_handler(response, analyze_qr, "location")
    
    elif data == "wifi":
        bot.delete_message(chat_id, msg_id)
        response = bot.send_message(chat_id,
            "<b>Send the Wi-Fi details as shown below 👉🏻\n\
            \n<code>Network::Password::Type</code>\n\
            \n➤ Network - Your network name\n\
            \n➤ Password - Your network password\n\
            \n➤ Type - Encryption (Optional - Default: WPA/WPA2)</b>")
        bot.register_next_step_handler(response, analyze_qr, "wifi")

    elif data == "web_app":
        bot.delete_message(chat_id, msg_id)
        bot.send_message(chat_id, "Scan QR Codes Live 👇🏻", 
            reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton("SCAN NOW 🔍",
                web_app=WebAppInfo(WEB_APP_URL + "qrCode"))))

bot.infinity_polling(skip_pending=True)
