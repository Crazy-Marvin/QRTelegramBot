import os
import flask
from flask import request

import telebot
from telebot.util import parse_web_app_data
from telebot.util import validate_web_app_data
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from telebot.types import InputTextMessageContent
from telebot.types import InlineQueryResultArticle

API_TOKEN = os.getenv("API_TOKEN")
STORAGE_CHANNEL = os.getenv("STORAGE_CHANNEL")

app = flask.Flask(__name__)
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

		bot.send_photo(STORAGE_CHANNEL, generate_qr(data))

		bot.answer_web_app_query(query_id, InlineQueryResultArticle(
			query_id, "QR Code Scanner", InputTextMessageContent(
				f'<b><i>Data Received:\n\nSummary ➜ {summary}\n\
					\nLocation ➜ {location}\n\nStartDate ➜ {startDate}\n\
					\nEndDate ➜ {endDate}\n\nDescription ➜ {description}</i></b>',
					parse_mode="HTML"), reply_markup=InlineKeyboardMarkup().row(
					InlineKeyboardButton("GENERATE EVENT QR CODE", callback_data="event-callbacks"))))

if __name__ == '__main__':
    app.run()
