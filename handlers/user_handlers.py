from main import bot, dp, scheduler
from functions.user_functions import order_history, send_mailing
from data.config import *
from filters.filters import *

from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from keyboards.user_keyboards import get_start_keyboard
from keyboards.admin_keyboards import get_admin_keyboard, get_manager_keyboard
from database.user_db import *

html = 'HTML'


async def scheduler_jobs():
    scheduler.add_job(order_history, "interval", minutes=60)
    scheduler.add_job(send_mailing, "cron", minute=0)
    # scheduler.add_job(send_mailing, "interval", minutes=1) 
    
    
    
    
async def antiflood(*args, **kwargs):
    m = args[0]
    await m.answer("Не поспішай :)")

async def on_startup(dp):
    await scheduler_jobs()
    from handlers.user_handlers import dp as user_dp
    from callbacks.user_callbacks import register_callbacks
    from callbacks.admin_callbacks import register_admin_callbacks
    register_callbacks(dp)
    register_admin_callbacks(dp)


async def on_shutdown(dp):
    me = await bot.get_me()
    print(f'Bot: @{me.username} зупинений!')

@dp.message_handler(IsPrivate(), commands=["start"])
@dp.throttled(antiflood, rate=1)
async def start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    user_first_name = message.from_user.first_name
    create_orders_table()
    # create_questions_table()
    user = message.from_user
    
    add_user(user_id, user_name)
    
    if not check_phone_number(user_id):
        share_contact_button = KeyboardButton("📞 Поділитися номером телефону", request_contact=True)
        share_contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(share_contact_button)
        await message.answer("<b>Будь ласка, поділіться своїм номером телефону для авторизації.</b>", parse_mode="html", reply_markup=share_contact_keyboard)
    else:
        keyboard = get_start_keyboard()
        greeting_message = f"Вітаю🌷, {user.username}! На зв’язку Cosmy асистент 👱🏻‍♀️\n Чим можу бути тобі корисною?"
        photo_path = 'data/hello.jpg'
        with open(photo_path, 'rb') as photo:
            await message.answer_photo(photo=photo, caption=greeting_message, reply_markup=keyboard)

        menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        if user_id in administrators:
            admin_button = KeyboardButton(text="Адмін-панель 👨🏼‍💻")
            menu_keyboard.add(admin_button)
            await message.answer("Вітаємо в боті!", reply_markup=menu_keyboard)
        elif user_id in managers:
            admin_button = KeyboardButton(text="Manager Panel👨🏼‍💻")
            menu_keyboard.add(admin_button)
            await message.answer("Вітаємо в боті!", reply_markup=menu_keyboard)

            
            
@dp.message_handler(content_types=['contact'])
async def process_contact(message: types.Message):
    if message.contact:
        user_id = message.from_user.id
        phone_number = message.contact.phone_number
        update_user_phone(user_id, phone_number)

        remove_keyboard = ReplyKeyboardRemove()

        await message.answer("Дякуємо! Ваш номер телефону збережено.", reply_markup=remove_keyboard)

        keyboard = get_start_keyboard()
        greeting_message = f"Вітаю🌷, {message.from_user.username}! На зв’язку Cosmy асистент 👱🏻‍♀️\n Чим можу бути тобі корисною?"
        photo_path = 'data/hello.jpg'
        with open(photo_path, 'rb') as photo:
            await message.answer_photo(photo=photo, caption=greeting_message, reply_markup=keyboard)




@dp.message_handler(IsPrivate(), commands=["admin"])
@dp.throttled(antiflood, rate=1)
async def admin_panel(message: types.Message):
    user = message.from_user
    if user.id in administrators:
        admin_keyboard = get_admin_keyboard()
        await message.answer("Адмін панель", reply_markup=admin_keyboard)


@dp.message_handler(lambda message: message.text == "Адмін-панель 👨🏼‍💻")
@dp.throttled(antiflood, rate=1)
async def admin_panel(message: types.Message):
    user_id = message.from_user.id
    if user_id in administrators:
        admin_keyboard = get_admin_keyboard()
        await message.answer("Адмін-панель 👨🏼‍💻", reply_markup=admin_keyboard)
        
        
@dp.message_handler(IsManager(), text="Manager Panel👨🏼‍💻")
async def admin_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    user = message.from_user

    if user_id in managers:
        greeting_message = f"Привіт, {user.username}! \nВи є менеджером. Будь ласка, виберіть дію нижче:"
        await message.answer(greeting_message, reply_markup=get_manager_keyboard())