from deeppavlov import build_model
from deeppavlov.core.common.file import read_json
from flask import jsonify
from enum import Enum
import requests
import telebot
import json


class Modes(Enum):
    INITIAL = 1
    QUESTINGANSWERING = 2


user_states = {}

token = open("token.txt").readline().strip()
bot = telebot.TeleBot(token)


def date_facts():
    url = 'http://numbersapi.com/random/date?json'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['text']
    else:
        return "Что-то пошло не так.."


def anime_img():
    url = 'https://api.waifu.im/search'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['images'][0]['url']
    else:
        return "Что-то пошло не так.."


def shreck(question):
    url = "http://127.0.0.1:5002/"
    data = {"data": question}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return "Ошибка при попытке узнать о Шрэке.."

def intent_get(text):
    url = "http://127.0.0.1:5000/"
    data = {"data": text}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return "Ошибка при попытке узнать намерение"


@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.chat.id
    user_states[user_id] = Modes.INITIAL
    bot.reply_to(message, "Можешь спросить у меня факт о Шреке, узнать случайную дату и факт о ней, а также получить случайную аниме картинку")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = message.chat.id
    mode = user_states.get(user_id, Modes.INITIAL)
    intent = intent_get(message.text)

    if intent == "date_facts" and mode == Modes.INITIAL:
        print("Ищу дату")
        bot.reply_to(message, date_facts())
    elif intent == "anime_img" and mode == Modes.INITIAL:
        print("Отправляю случайное изображение")
        bot.reply_to(message, anime_img())
    elif mode == Modes.QUESTINGANSWERING and intent != "init":
        print("Отвечаю на вопрос")
        bot.reply_to(message, shrek(message.text))
    elif intent == "shrek" and mode == Modes.INITIAL:
        print("Перехожу в режим ответа на вопросы")
        user_states[user_id] = Modes.QUESTINGANSWERING
        bot.reply_to(message, "Сейчас ты можешь начать задавать мне вопросы о Шреке. Для остановки напиши Хватит")
    elif intent == "init" and mode == Modes.QUESTINGANSWERING:
        print("Ок, хватит")
        user_states[user_id] = Modes.INITIAL
        bot.reply_to(
            message, "Можешь спросить у меня факт о Шреке, узнать случайную дату и факт о ней, а также получить случайную аниме картинку")


bot.infinity_polling()
