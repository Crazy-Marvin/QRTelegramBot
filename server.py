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

app = flask.Flask(__name__)
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

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

		bot.answer_web_app_query(query_id, InlineQueryResultArticle(
			query_id, "QR Code Scanner", InputTextMessageContent(
				f'<b><i>Data Received:\n\nSummary ➜ {summary}\n\
					\nLocation ➜ {location}\n\nStartDate ➜ {startDate}\n\
					\nEndDate ➜ {endDate}\n\nDescription ➜ {description}</i></b>',
					parse_mode="HTML"), reply_markup=InlineKeyboardMarkup().row(
					InlineKeyboardButton("GENERATE EVENT QR CODE", callback_data="event-callbacks"))))

if __name__ == '__main__':
    app.run()