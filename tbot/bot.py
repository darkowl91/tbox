#!/usr/bin/python3

import logging
import os
import cv2
import bme280
import smbus2
from telegram.ext import Updater, CommandHandler
from io import BytesIO
from datetime import date


def command_start(update, context):
    update.message.reply_text("""Hi {}!
        I will help you observe turtle that is living in terrarium. 😁
        Use these commands to control me:
        /photo - web-cam photo
        /climate - current temperature, humidity, pressure
        /help - available commands""".format(update.message.from_user.username))


def command_help(update, context):
    update.message.reply_text("""Available commands:
        /photo - web-cam photo
        /climate - current temperature, humidity, pressure""")


def command_photo(update, context):
    cam = cv2.VideoCapture(0)  # usb camera /dev/video0
    if not cam.isOpened():
        logging.error("could not init /dev/video0")
        return

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

    check, frame = cam.read()
    if not check:
        logging.error("could not read /dev/video0")
        return

    try:
        check, buf = cv2.imencode('.png', frame)  # frame to memory buffer
        if not check:
            logging.error("could not convert to png from buffer")
            return

        bytes = BytesIO(buf.tobytes())
        title = "🐢📸 [clydethetortoise_official](https://www.instagram.com/clydethetortoise_official)"
        update.message.reply_photo(
            photo=bytes, caption=title, parse_mode="Markdown")
    except Exception as e:
        logging.error(e)

    finally:
        cam.release()


def command_climate(update, context):
    data = None
    try:
        _bus = smbus2.SMBus(bus=1)  # default i2c port for pi
        bme280.load_calibration_params(_bus, 0x76)  # bme default i2c address
        data = bme280.sample(_bus, 0x76)
    except Exception as e:
        logging.error(e)
        return
    finally:
        _bus.close()

    t = data.temperature
    tf = t * 1.8 + 32.0  # convert to fahrenheit
    h = data.humidity
    p = data.pressure
    update.message.reply_text("🌡{}°C {}°F 💧{}% 📈{}hPa".format(
        round(t), round(tf), round(h), round(p)))


def handle_error(update, context):
    logging.error('Update "%s" caused error "%s"', update, context.error)


def poll(token):
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", command_start))
    dp.add_handler(CommandHandler("help", command_help))
    dp.add_handler(CommandHandler("photo", command_photo))
    dp.add_handler(CommandHandler("climate", command_climate))

    dp.add_error_handler(handle_error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    poll(os.getenv("BOT_TOKEN"))
