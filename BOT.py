import telebot
from telebot.types import InputMediaPhoto
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
#from telebot.types import ReplyKeyboardMarkup, KeyboardButton
# import json
# from PIL import Image
# import sqlite3
# import requests
# import base64
import os
from model import extract_signatures_from_documents
from model import text_output_signatures
from model import visualize_best_signatures
from model import add_employee_signatures

import glob

docs_path = 'Docs'
predict_path = 'Predicts/Signs'
employee_signs_path = 'Signatures/' 
predicts_signs_path = 'Predicts/Signs'
#predicts_docs_path = 'Predicts/Docs'

os.system('python model.py')

TOKEN = '5328174448:AAEy1Lc5zYDHT6Gd7RALkH_44IAae-ZxyS4'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    # markup.add(InlineKeyboardButton("Загрузить подписи пользователя в базу данных", callback_data='upload_signatures'),
    #            InlineKeyboardButton("Идентифицировать подпись пользователя", callback_data='identify_signature'))
    bot.send_message(message.chat.id, "Используйте /identify для подтверждения подписи сотрудника\nИспользуйте /add для добавления новых подписей сотрудника")
    
    #Создание клавиатуры с кнопками
    # keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # keyboard.add(KeyboardButton('Загрузить подписи пользователя в базу данных'))
    # keyboard.add(KeyboardButton('Идентифицировать подпись пользователя'))
    # bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)


@bot.message_handler(content_types=['photo'])
def handle_identifing(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        check_user = message.caption

        with open("Docs/photo.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
    
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при загрузке фото. Пожалуйста, попробуйте еще раз.")

    try:
        res_extract = extract_signatures_from_documents(docs_path, predict_path)
        bot.reply_to(message, res_extract)
    except Exception as e:
        bot.reply_to(message, "Ошибка при распознавании документа")
    try:
        text_output = text_output_signatures(check_user, employee_signs_path+check_user, predicts_signs_path)
        bot.reply_to(message, text_output) 
    except Exception as e:
        bot.reply_to(message, "Ошибка при выводе информации по валидности подписи. Вероятно, вы забыли указать фамилию.")
    try:
        img_output = visualize_best_signatures(employee_signs_path + check_user, predicts_signs_path)
        media_group = []
        for img_path in img_output:
            with open(img_path, 'rb') as photo:
                media_group.append(InputMediaPhoto(photo.read()))  # Важно использовать read(), чтобы передать содержимое файла
        if media_group:
            bot.send_media_group(message.chat.id, media_group)
    except Exception as e:
        bot.reply_to(message, "Ошибка при выводе изображения сравнения подписей")
    



@bot.message_handler(commands=['identify'])
def identify_signature(message):
    bot.send_message(message.chat.id, "Пришлите фото с документом на котором стоит подпись сотрудника и укажите его фаимилию (латинецей)")
    bot.register_next_step_handler(message, handle_identifing)

@bot.message_handler(commands=['add'])
def add_user_signature(message):
    bot.send_message(message.chat.id, "Пришлите фото с подписями сотрудника и укажите его фамилию (латиницей)")
    bot.register_next_step_handler(message, handle_addin)

@bot.message_handler(content_types=['photo'])
def handle_addin(message):
    # try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        check_user = message.caption
        if os.path.isdir(f'Signatures/{check_user}') == False:
            os.makedirs(f'Signatures/{check_user}')

        filez = [f for f in glob.glob(f'Signatures/*.jpg')]

        number = None

        if len(filez) > 0:
            number = len(filez)+1
        else:
            number = 1


        with open(f'Signatures/downloaded_photo_{number}.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)


        add_employee_signatures(f'Signatures/', check_user, f'downloaded_photo_{number}.jpg')

    
    # except Exception as e:
        # bot.reply_to(message, "Произошла ошибка при загрузке фото. Пожалуйста, попробуйте еще раз.")



bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

bot.infinity_polling()