import qrcode, cv2, time, telepot
from telepot.loop import MessageLoop

TOKEN = ""

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)


    if chat_type == "private":
        if content_type == 'text':
            if "/start" in msg['text']:
                bot.sendMessage(chat_id, "Welcome to the QR Code Telegram bot! 🤳\n\nYou can send a photo from your gallery or take a new one and the bot sends you all information from included QR codes it sees or you can send text to let the bot generate a QR code for you.\n\nEnjoy! 🎉")

            elif "/help" in msg['text']:
                bot.sendDocument(chat_id, open(f"/var/www/html/qrcode/animation.gif", "rb"))
                bot.sendMessage(chat_id, "This bot can read and create QR codes.\n\nRead a QR code:\nBy clicking on the staple you can take a new photo or choose one from your gallery. The bot will send you the information it recognizes then.\n\nGenerate a QR code:\nSimply type some text and send it to the bot. It will then send you a QR code image after a few seconds.\n\nPlease checkout the attached .gif for a little introduction to its features.\n\nThe source can be found on GitHub (https://github.com/Crazy-Marvin/QRTelegramBot). Feel free to contact me with feedback and questions.")

            elif "https" in msg['text'] or "http" in msg['text']:
                filename = f"/var/www/html/qrcode/database/{chat_id}.png"
                img = qrcode.make(msg['text'])
                img.save(filename)
                bot.sendPhoto(chat_id, open(f"/var/www/html/qrcode/database/{chat_id}.png", "rb"))
            else:
                filename = f"/var/www/html/qrcode/database/{chat_id}.png"
                img = qrcode.make(msg['text'])
                img.save(filename)
                bot.sendMessage(chat_id, "This is a normal text and won't be recognized as an URL that opens in the browser when scanned.")
                bot.sendPhoto(chat_id, open(f"/var/www/html/qrcode/database/{chat_id}.png", "rb"))

        elif content_type == 'photo':
            bot.download_file(msg['photo'][-1]['file_id'], f"/var/www/html/qrcode/database/{chat_id}.png")
            img = cv2.imread(f"/var/www/html/qrcode/database/{chat_id}.png")
            detector = cv2.QRCodeDetector()
            data, bbox, straight_qrcode = detector.detectAndDecode(img)

            if bbox is not None:
                bot.sendMessage(chat_id, f"{data}")
            else:
                bot.sendMessage(chat_id, f"QR Code not recognized.")

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()

while 1:
    time.sleep(10)
