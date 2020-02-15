#!/usr/bin/python3

import logging
import os
import cv2
import bme280
import smbus2
import RPi.GPIO as GPIO
from datetime import datetime, time
from telegram.ext import Updater, CommandHandler
from io import BytesIO
from chatbase import Message

LED_PIN = 25


def command_start(update, context):
    update.message.reply_text("""Hi {}!
        I will help you observe turtle that is living in terrarium. 😁
        Use these commands to control me:
        /photo - web-cam photo
        /climate - current temperature, humidity, pressure
        /help - available commands""".format(update.message.from_user.username))
    chatbaseMessage(
        intent="start",
        user=update.message.from_user.username).send()


def command_help(update, context):
    update.message.reply_text("""Available commands:
        /photo - web-cam photo
        /climate - current temperature, humidity, pressure""")
    chatbaseMessage(
        intent="help",
        user=update.message.from_user.username).send()


def command_photo(update, context):
    msg = chatbaseMessage(
        intent="photo",
        user=update.message.from_user.username)

    cam = cv2.VideoCapture(0)  # usb camera /dev/video0
    if not cam.isOpened():
        msg.set_as_not_handled()
        logging.error("could not init /dev/video0")
        return

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
    # skip frames to normalize cam output
    cam.set(cv2.CAP_PROP_POS_FRAMES, 25)

    flash(True)

    check, frame = cam.read()
    if not check:
        msg.set_as_not_handled()
        logging.error("could not read /dev/video0")
        return

    try:
        check, buf = cv2.imencode('.png', frame)  # frame to memory buffer
        if not check:
            msg.set_as_not_handled()
            logging.error("could not convert to png from buffer")
            return

        bytes = BytesIO(buf.tobytes())
        title = "🐢📸 [clydethetortoise_official](https://www.instagram.com/clydethetortoise_official)"
        update.message.reply_photo(
            photo=bytes, caption=title, parse_mode="Markdown")
    except Exception as e:
        msg.set_as_not_handled()
        logging.error(e)

    finally:
        flash(False)
        cam.release()
        msg.send()


def command_find(update, context):
    chatbaseMessage(
        intent="help",
        user=update.message.from_user.username)
    # todo
    pass


def command_climate(update, context):
    msg = chatbaseMessage(
        intent="climate",
        user=update.message.from_user.username)

    data = None
    try:
        _bus = smbus2.SMBus(bus=1)  # default i2c port for pi
        bme280.load_calibration_params(_bus, 0x76)  # bme default i2c address
        data = bme280.sample(_bus, 0x76)
    except Exception as e:
        logging.error(e)
        msg.set_as_not_handled()
        return
    finally:
        _bus.close()
        msg.send()

    t = data.temperature
    tf = t * 1.8 + 32.0  # convert to fahrenheit
    h = data.humidity
    p = data.pressure
    update.message.reply_text("🌡{}°C {}°F 💧{}% 📈{}hPa".format(
        round(t), round(tf), round(h), round(p)))


def handle_error(update, context):
    logging.error('Update "%s" caused error "%s"', update, context.error)

    msg = chatbaseMessage(
        intent="error",
        user=update.message.from_user.username,
        mesage=context.error)
    msg.set_as_not_handled()
    msg.send()


def flash(value=None):
    if value and isNowInTimePeriod(time(22, 0), time(5, 0)):
        GPIO.output(LED_PIN, value)
    elif not value:
        GPIO.output(LED_PIN, False)


def isNowInTimePeriod(startTime, endTime):
    nowTime = datetime.now().time()
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else:
        return nowTime >= startTime or nowTime <= endTime


def chatbaseMessage(intent, user, mesage=None):
    return Message(api_key=os.getenv("CHATBASE_TOKEN"),
                   platform="Telegram",
                   message=mesage,
                   intent=intent,
                   version="1.0",
                   user_id=user)


def poll(bot_token):
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", command_start, ))
    dp.add_handler(CommandHandler("help", command_help))
    dp.add_handler(CommandHandler("photo", command_photo))
    dp.add_handler(CommandHandler("find", command_find))
    dp.add_handler(CommandHandler("climate", command_climate))

    dp.add_error_handler(handle_error)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setwarnings(False)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    poll(os.getenv("BOT_TOKEN"))
