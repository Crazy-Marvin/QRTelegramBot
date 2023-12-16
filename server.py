import os
import flask
from flask import request
from flask import redirect

import telebot
from telebot.util import parse_web_app_data
from telebot.util import validate_web_app_data
from telebot.types import InputTextMessageContent
from telebot.types import InlineQueryResultArticle
from telebot.types import InlineQueryResultCachedPhoto

API_TOKEN = os.getenv("API_TOKEN")
STORAGE_CHANNEL = os.getenv("STORAGE_CHANNEL")

app = flask.Flask(__name__, static_url_path="static")
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

from io import BytesIO
from qrcode import make

def generate_qr(data):
    with BytesIO() as qr:
        qr_data = make(data)
        qr_data.save(qr, format="PNG")
        return qr.getvalue()

@app.route('/')
def index():
    return redirect('https://t.me/QRCodeTelegramBot')

@app.route('/qrCodeEvent')
def qrCodeEvent():
    return flask.render_template("event.html")

@app.route('/qrcallback', methods=["POST"])
def qrcallback():

	raw_data = request.json

	summary = raw_data["summary"]
	location = raw_data["location"]
	startDate = raw_data["startDate"]
	endDate = raw_data["endDate"]
	description = raw_data["description"]

	initData = raw_data["initData"]

	isValid = validate_web_app_data(API_TOKEN, initData)

	if isValid:
		web_app_data = parse_web_app_data(API_TOKEN, initData)
		query_id = web_app_data["query_id"]
		
		data = f"""BEGIN:VEVENT\
              \nSUMMARY:{summary}\
              \nLOCATION:{location}\
              \nDTSTART: {startDate}\
              \nDTEND:{endDate}\
              \nDESCRIPTION:{description}\
              \nEND:VEVENT"""

		photo = bot.send_photo(STORAGE_CHANNEL, generate_qr(data))
		file_id = bot.get_file(photo.photo[-1].file_id).file_id

		bot.answer_web_app_query(query_id, InlineQueryResultCachedPhoto(query_id, file_id))

	return "200"

# ------------------- QR Code Scanner ------------------- #

@app.route('/qrCode')
def qrCode():
    return flask.render_template("qrCode.html")

@app.route('/qrCodeResponse', methods=["POST"])
def qrCodeResponse():
    raw_data = flask.request.json
    initData = raw_data["initData"]

    isValid = validate_web_app_data(API_TOKEN, initData)

    if isValid:
        web_app_data = parse_web_app_data(API_TOKEN, initData)

        query_id = web_app_data["query_id"]

        bot.answer_web_app_query(query_id, InlineQueryResultArticle(
            id=query_id, title="QR DETECTED!",
            input_message_content=InputTextMessageContent(
                f"<i>QR Code scanned successfully! 👇🏻\n\
				\n{raw_data['qr']}</i>", parse_mode="HTML")))

    return redirect("/")

# ------------------- QR Code Scanner ------------------- #

if __name__ == '__main__':
    app.run()
