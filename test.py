#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
from telegram.ext import Updater
import logging
import json
import requests
import threading
import time
import datetime
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

teleKey = "YOUR TELEGRAM API KEY HERE"
apiKey = "YOU OPENWEATHER API KEY HERE"

updater = Updater(token=teleKey, use_context=True)

dispatcher = updater.dispatcher
cityList = {}
subList = {}
doExit = False
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def getClothes(temp, wind, id):
    if id >= 200 and id <= 232:
        return "Оденьте непромокаемую одежду покрепче или дождевик и не берите с собой зонтик."
    if id >= 300 and id <= 531:
        if wind > 10:
            return "Оденьте непромокаемую одежду покрепче или дождевик и не берите с собой зонтик."
        else:
            if temp > 15:
                return "Можете лекго одеться, но возьмите с собой зонтик."
            else:
                return "Оденьтесь потеплее и возьмите с собой зонтик."
    if id >= 600 and id <= 622:
        if temp >= -10 and wind < 10:
            return "Можно идти без шарфа, но желательно надеть ботинки повыше."
        else:
            return "Завернитесь в шарф, и оденьте ботинки повыше."
    if id >= 701 and id < 781 and id != 741:
        return "Обязательно наденьте маску перед выходом на улицу."
    if id == 781:
        return "На стоит выходить на улицу."
    if id == 803 or id == 804:
        if wind < 10:
            return "Стоит взять с собой зонтик."
        else:
            return "Зонтик лучше с собой не брать."
    if temp < -10 or temp < 0 and wind > 10:
        return "Завернитесь в шарф и оденьтесь потеплее."
    return "Никаких особых рекомендаций нет."


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я умный погодный бот разработанный, как тестовое задание для 'Школы будущих СТО. \nДля получения помощи напиши /help")

def setCity(update, context):
    if len(context.args) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите свой город!")
    else:
        oldtime = 0
        if str(update.effective_chat.id) in cityList:
            res1 = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + cityList[str(update.effective_chat.id)] + "&appid=" + apiKey + "&lang=ru")
            dat1 = json.loads(res1.text)
            oldtime = int(dat1["timezone"])
        res = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + ' '.join(context.args) + "&appid=" + apiKey + "&lang=ru")
        dat = json.loads(res.text)
        if dat["cod"] == "404":
            context.bot.send_message(chat_id=update.effective_chat.id, text="Ваш город не найден!")
        else:
            cityList[str(update.effective_chat.id)] = ' '.join(context.args)
            if str(update.effective_chat.id) in subList:
                timeUTC = subList[str(update.effective_chat.id)] - int(dat["timezone"]) + oldtime
                if timeUTC < 0:
                    subList[str(update.effective_chat.id)] = 24*3600 + timeUTC
                elif timeUTC > 23*3600 + 59*60:
                    subList[str(update.effective_chat.id)] = timeUTC - 24*3600
                else:
                    subList[str(update.effective_chat.id)] = timeUTC
            context.bot.send_message(chat_id=update.effective_chat.id, text="Город установлен!")

def weather(update, context):
    if not str(update.effective_chat.id) in cityList and len(context.args) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Установите свой город с помощью команды /setcity или введите /weather <город>, чтобы получить погоду")
    elif len(context.args) > 0:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + ' '.join(context.args) + "&appid=" + apiKey + "&lang=ru")
        dat = json.loads(res.text)
        if dat["cod"] == "404":
            context.bot.send_message(chat_id=update.effective_chat.id, text="Ваш город не найден!")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="В городе " + dat["name"] + " на улице " + dat['weather'][0]['description'] + ".\nТемпература: " + str(float('{:.2f}'.format(float(dat['main']['temp']) - 273))) + " градусов цельсия.\nСкорость ветра: " + str(dat["wind"]["speed"]) + " метров в секунду.\nДавление: " + str(dat["main"]["pressure"]) + " гПа.\nВлажность: " + str(dat["main"]["humidity"]) + "%\nРекомендации: " + getClothes(float('{:.2f}'.format(float(dat['main']['temp']) - 273)),dat["wind"]["speed"],dat["weather"][0]["id"]))
    else:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + cityList[str(update.effective_chat.id)] + "&appid=" + apiKey + "&lang=ru")
        dat = json.loads(res.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text="В городе " + dat["name"] + " на улице " + dat['weather'][0]['description'] + ".\nТемпература: " + str(float('{:.2f}'.format(float(dat['main']['temp']) - 273))) + " градусов цельсия.\nСкорость ветра: " + str(dat["wind"]["speed"]) + " метров в секунду.\nДавление: " + str(dat["main"]["pressure"]) + " гПа.\nВлажность: " + str(dat["main"]["humidity"]) + "%\nРекомендации: " + getClothes(float('{:.2f}'.format(float(dat['main']['temp']) - 273)),dat["wind"]["speed"],dat["weather"][0]["id"]))

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Неизвестная команда!\nИспользуйте /help для получения списка команд")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Для получения погоды для вашего города используйте /weather\nДля получения погоды для любого города используйте /weather <город>\nДля установки своего города используйте /setcity <город>\nДля получения помощи напишите /help\nЧтобы получать информацию о погоде в рассылке напишите /subscribe <часы> <минуты>, где часы минуты обозначают время, в которое вам необходимо получать погоду.\nЧтобы отписаться от рассылки используйте /unsubscribe.")

def subscribe(update, context):
    if not str(update.effective_chat.id) in cityList:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Вы не выбрали свой город!\nИспользуйте /setcity <город>, чтобы выбрать свой город")
    elif len(context.args) < 2:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите /subscribe <часы> <минуты>")
    else:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + cityList[str(update.effective_chat.id)] + "&appid=" + apiKey + "&lang=ru")
        dat = json.loads(res.text)
        try:
            timeUTC = 3600 * int(context.args[0]) + 60 * int(context.args[1]) - int(dat["timezone"])
            if timeUTC < 0:
                subList[str(update.effective_chat.id)] = 24*3600 + timeUTC
            elif timeUTC > 23*3600 + 59*60:
                subList[str(update.effective_chat.id)] = timeUTC - 24*3600
            else:
                subList[str(update.effective_chat.id)] = timeUTC
            context.bot.send_message(chat_id=update.effective_chat.id, text="Вы успешно добавлены в список для рассылки!")
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка при попытке добавить вас в список для рассылки. Проверьте правильность введенного вермени!")

def unsubscribe(update, context):
    if not str(update.effective_chat.id) in subList:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Вы не подписаны на рассылку.")
    else:
        del subList[str(update.effective_chat.id)]
        context.bot.send_message(chat_id=update.effective_chat.id, text="Вы успешно отписались от рассылки!")

def timeCounter():
    while not doExit:
        curtime = datetime.datetime.now().hour * 3600 + datetime.datetime.now().minute * 60 + datetime.datetime.now().second
        for k in subList:
            if curtime == subList[k]:
                res = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + cityList[k] + "&appid=" + apiKey + "&lang=ru")
                dat1 = json.loads(res.text)
                res = requests.get("https://api.openweathermap.org/data/2.5/onecall?lon=" + str(dat1["coord"]["lon"]) + "&lat=" + str(dat1["coord"]["lat"]) + "&appid=" + apiKey + "&lang=ru")
                dat = json.loads(res.text)
                updater.bot.send_message(chat_id=int(k), text="В городе " + cityList[k] + " сегодня на улице " + dat["daily"][0]["weather"][0]["description"] + ".\nТемпература от " + str(float('{:.2f}'.format(float(dat['daily'][0]['temp']["min"]) - 273))) + " до " + str(float('{:.2f}'.format(float(dat['daily'][0]['temp']["max"]) - 273))) + " градусов цельсия.\nСкорость ветра " + str(dat["daily"][0]["wind_speed"]) + " метров в секунду\nДавление: " + str(dat["daily"][0]["pressure"]) + " гПа\nВлажность: " + str(dat["daily"][0]["humidity"]) + "%\nРекомендации: " + getClothes(float('{:.2f}'.format(float(dat["daily"][0]['temp']['day']) - 273)),dat["daily"][0]["wind_speed"],dat["daily"][0]["weather"][0]["id"]))
        time.sleep(1)

start_handler = CommandHandler('start', start)
weather_handler = CommandHandler('weather', weather)
setcity_handler = CommandHandler('setcity', setCity)
help_handler = CommandHandler('help',help)
sub_handler = CommandHandler('subscribe',subscribe)
unsub_handler = CommandHandler('unsubscribe',unsubscribe)
echo_handler = MessageHandler(Filters.text, unknown)
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(weather_handler)
dispatcher.add_handler(setcity_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(sub_handler)
dispatcher.add_handler(unsub_handler)
dispatcher.add_handler(unknown_handler)
dispatcher.add_handler(echo_handler)
try:
    with open("conf.json","r") as f:
        cityList = json.load(f)
except IOError:
    print("Log is not accesible")
try:
    with open("subconf.json","r") as f:
        subList = json.load(f)
except IOError:
    print("SubLog is not accesible")
x = threading.Thread(target=timeCounter)
x.start()
updater.start_polling()
updater.idle()
with open("conf.json","w") as f:
    json.dump(cityList, f)
with open("subconf.json","w") as f:
    json.dump(subList, f)
doExit = True