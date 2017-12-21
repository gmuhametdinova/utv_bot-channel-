# -*- coding: utf-8 -*-
import telebot
import sqlite3
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen
from telebot import types

# Главная страница (все новости)
html_doc = urlopen('http://utv.ru/ufa/t/novosti/').read()
soup = BeautifulSoup(html_doc, "lxml")

token = '425483264:AAFswytQW1DjoadoramgTTs2A7_4FYxiyx0'
URL = 'https://api.telegram.org/bot' + token + '/'
utv = 'http://utv.ru'

bot = telebot.TeleBot(token)

# Получаем первую ссылку из списка
link = soup.findAll('div', attrs={'class': 'item-title text-short'})
for div in link:
    a = div.find('a')
    if a:
        links = (a['href'])
        break

# Cтраница самой новости
news = utv + links

html = urlopen(news).read()
sourse = BeautifulSoup(html, "lxml")

# Найти картинку
image = sourse.findAll('div', attrs={'class': 'container-item__shortland'})
for div in image:
    img = div.find('img')
    if img:
        im_link = (img['src'])
        break


# Обработка исключения. Если нет картинки - отправляем заглушку
try:
    images = utv + im_link
except NameError:
    images = news


def main():
    markup = types.InlineKeyboardMarkup()
    my_btn = types.InlineKeyboardButton(text='Читать новость', url=news)
    markup.add(my_btn)
    message = [
        (soup.find('div', class_='item-title text-short').get_text()) + '.',
        (soup.find('div', class_='item-desc text-short').get_text())
    ]
    title = news
    conn = sqlite3.connect('name.db')
    cursor = conn.cursor()
    channel_id = -1001268749913
    # Проверка на наличие записи. Если запись имеется, то сообщение не отправляем.
    try:
        cursor.execute("INSERT INTO title(title_news) VALUES (%r)" % title)
        bot.send_chat_action(channel_id, 'upload_photo')
        bot.send_photo(channel_id, images, caption=(''.join(message)), reply_to_message_id=None, reply_markup=markup)
    except sqlite3.IntegrityError:
        print('Такая запись уже есть')
    conn.commit()
    cursor.execute("SELECT title_news FROM title ORDER BY title_news")
    results = cursor.fetchall()
    conn.close()


if __name__ == '__main__':
    main()
