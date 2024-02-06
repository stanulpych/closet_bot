import telebot
from functools import partial
from models import *

bot = telebot.TeleBot('6629791393:AAF9w6GZZmIBK9h7zcfOGmiII65QJkXvLFc', parse_mode='HTML')


markup = telebot.types.ReplyKeyboardMarkup()
item1 = telebot.types.KeyboardButton('Список')
item2 = telebot.types.KeyboardButton('Взять предмет')
item3 = telebot.types.KeyboardButton('Вернуть предметы')
item4 = telebot.types.KeyboardButton('Создать предмет')
item5 = telebot.types.KeyboardButton('Взятые')
item6 = telebot.types.KeyboardButton('Изменить кол-во предмета')
item7 = telebot.types.KeyboardButton('Удалить предмет')
markup.add(item1, item2, item3, item4, item5, item6, item7)

@bot.message_handler(commands=['start'])

def answer(message):
    bot.send_message(message.chat.id, 'Это Шкаф-бот!',reply_markup=markup)
    
@bot.message_handler(content_types='text')
def Ans(message):
    if message.text == "Список":
        bot.send_message(message.chat.id, ListOfItems())
    if message.text == "Создать предмет":
        bot.send_message(message.chat.id, "Введите название \n(Название должно быть в одно слово, например Название_предмета)")
        bot.register_next_step_handler(message, NameOfItem)
    if message.text == "Взять предмет":
        bot.send_message(message.chat.id, "Введите название предмета")
        bot.register_next_step_handler(message, TakeItemDetailBot)
    if message.text == "Вернуть предметы":
        bot.send_message(message.chat.id, ReturnItemDetail(message.from_user.username))
        bot.register_next_step_handler(message, ReturnItemNameBot)
    if message.text == "Взятые":
        bot.send_message(message.chat.id, "Введите название предмета или тег пользователя\nВведите Все, если хотите посмотреть весь список")
        bot.register_next_step_handler(message, NameOrTagListBot)
    if message.text == "Изменить кол-во предмета":
        bot.send_message(message.chat.id, "Введите название предмета")
        bot.register_next_step_handler(message, NameOfEditBot)
    if message.text == "Удалить предмет":
        bot.send_message(message.chat.id, "Введите название предмета")
        bot.register_next_step_handler(message, DeleteItemBot)



def NameOrTagListBot(message):
    Name = message.text
    if "@" in Name:
        bot.send_message(message.chat.id, ListOfTakenByTag(Name[1::1]))
    elif Name == "Все":
        bot.send_message(message.chat.id, ListOfTaken())
    else:
        bot.send_message(message.chat.id, ListOfTakenByName(Name))

#Создание предмета в шкафу
def NameOfItem(message):
    Name = message.text
    if len(Name) >=50 :
        bot.send_message(message.chat.id, "Длинновато")
    else:
        bot.send_message(message.chat.id, "Введите описание (опционально)")
        bot.register_next_step_handler(message,partial(discr, Name))
def discr(Name, message):
    Discription = message.text
    if len(Discription) >=200:
        bot.send_message(message.chat.id, "Длинновато")
    else:
        bot.send_message(message.chat.id, "Введите кол-во предмета")
        bot.register_next_step_handler(message, partial(FinalCreate, Name, Discription))
def FinalCreate(Name, Discription,  message):
    try:
        Quantity = int(message.text)
    except ValueError:
        Quantity = 0
        bot.send_message(message.chat.id, "Неправильное значение\nКол-во будет 0")
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение")
    else:
        bot.send_message(message.chat.id, CreateItem(Name, Discription, Quantity))



#Взятие предмета из шкафа
def TakeItemDetailBot(message):
    Name = message.text
    bot.send_message(message.chat.id, TakeItemDetail(Name))
    if TakeItemDetail(Name) == "Такого предмета нет":
        pass
    else:
        bot.register_next_step_handler(message, partial(TakeItemBot, Name))
def TakeItemBot(Name, message):
    try:
        Quantity = int(message.text)
    except ValueError:
        Quantity = 0
        bot.send_message(message.chat.id, "Неправильное значение\nКол-во будет 0")
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение")
    else:
        bot.send_message(message.chat.id, TakeItem(Name, Quantity, message.from_user.username))


#Возврат предмета в шкаф 
def ReturnItemNameBot(message):
    Name = message.text
    bot.send_message(message.chat.id, "Введите кол-во предмета, которое хотите вернуть")
    bot.register_next_step_handler(message, partial(ReturnItemBot, Name))
def ReturnItemBot(Name, message):
    try:
        Quantity = int(message.text)
    except ValueError:
        Quantity = 0
        bot.send_message(message.chat.id, "Неправильное значение\nКол-во будет 0")
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение")
    else:
        ReturnItems(Name, Quantity, message.from_user.username)
        bot.send_message(message.chat.id, "Успешно")


#
def NameOfEditBot(message):
    Name = message.text
    bot.send_message(message.chat.id, "Введите новое кол-во")
    bot.register_next_step_handler(message, partial(EditBot, Name))
def EditBot(Name, message):
    Quantity = int(message.text)
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение")
    else:
        EditQuantity(Name, Quantity)
        bot.send_message(message.chat.id, "Success")

#
def DeleteItemBot(message):
    Name = message.text
    bot.send_message(message.chat.id, DeleteItem(Name))
bot.infinity_polling()
