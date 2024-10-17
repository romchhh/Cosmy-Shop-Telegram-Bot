from aiogram import types, Dispatcher
from main import bot, dp
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from keyboards.user_keyboards import *
from data.config import managers, logs
from functions.cosmyapi import *
from database.admin_db import get_manager_name
from states.user_states import SupportStates, ReviewStates, ReviewOrderStates
from aiogram.dispatcher import FSMContext
from database.user_db import get_manager_id_from_db, add_question_to_db, check_if_question_exists,  get_user_phone
from states.user_states import SupportStates
from keyboards.admin_keyboards import get_reply_keyboard, get_start_dialog_keyboard
import asyncio, pytz
from datetime import datetime

# Define working hours
WORKING_HOURS = {
    "Monday": (9, 20),
    "Tuesday": (9, 20),
    "Wednesday": (9, 20),
    "Thursday": (9, 20),
    "Friday": (10, 20),
    "Saturday": (10, 18)
}

def is_within_working_hours():
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    now = datetime.now(kyiv_tz)
    current_day = now.strftime('%A')
    current_hour = now.hour

    if current_day in WORKING_HOURS:
        start_hour, end_hour = WORKING_HOURS[current_day]
        return start_hour <= current_hour < end_hour
    return False


@dp.callback_query_handler(lambda c: c.data == 'centre')
async def send_contacts_info(callback_query: types.CallbackQuery):
    new_caption = "Оберіть, що вас цікавить 👇🏻"
    keyboard = get_contacts_keyboard()
    
    await callback_query.message.edit_caption(
        caption=new_caption,
        reply_markup=keyboard
    )
    
@dp.callback_query_handler(lambda c: c.data == "main_menu")
async def go_to_main_menu(callback_query: types.CallbackQuery):
    keyboard = get_start_keyboard()  
    await callback_query.message.edit_caption(
        caption="Вітаю! На зв’язку Cosmy асистент 👱🏻‍♀️\n Чим можу бути тобі корисною?",
        reply_markup=keyboard
    )
    

@dp.callback_query_handler(lambda c: c.data == 'contacts')
async def send_contacts_info(callback_query: types.CallbackQuery):
    # Повідомлення з контактною інформацією
    contact_info = (
        "Наші контакти:\n"
        "📍 м. Київ\n"
        "Лабораторний провулок 7, офіс 14\n\n"
        "📞 Телефон:\n"
        "066 288 48 11\n"
        "073 317 54 43\n"
        "067 820 58 48\n\n"
        "📧 Електронна пошта:\n"
        "<a href='mailto:cosmy.ua@gmail.com'>cosmy.ua@gmail.com</a>\n\n"
        "🕒 Час роботи:\n"
        "Пн-Пт 9:00-20:00\n"
        "Сб-Нд 10:00-20:00\n"
    )
    
    keyboard = get_contacts_contacts_keyboard()
    await callback_query.message.edit_caption(
        caption=contact_info,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
        
@dp.callback_query_handler(lambda c: c.data == 'info')
async def send_info_menu(callback_query: types.CallbackQuery):
    info_message = "Що вас цікавить?"

    keyboard = get_info_keyboard()
    await callback_query.message.edit_caption(
        caption=info_message,
        reply_markup=keyboard
    )
    
    
@dp.callback_query_handler(lambda c: c.data == 'settings')
async def settings(callback_query: types.CallbackQuery):
    new_caption = "🔄 Бажаєте змінити номер телефону?"
    keyboard = get_settings_keyboard()
    
    await callback_query.message.edit_caption(
        caption=new_caption,
        reply_markup=keyboard
    )
    
@dp.callback_query_handler(lambda c: c.data == 'change_number')
async def process_change_number(callback_query: types.CallbackQuery):
    share_contact_button = KeyboardButton("📞 Поділитися номером телефону", request_contact=True)
    share_contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(share_contact_button)
    user_id = callback_query.from_user.id    
    await bot.answer_callback_query(callback_query.id) 
    await bot.send_message(user_id, "<b>Будь ласка, поділіться своїм номером телефону для авторизації.</b>", parse_mode="html", reply_markup=share_contact_keyboard)
    
    
async def send_order_data_to_user(callback_query: types.CallbackQuery, order_details):
    if order_details:
        response_message = "\n".join([f"{key}: {value}" for key, value in order_details.items() if key != "Товари у замовленні"])
        products_message = "Товари у замовленні:\n" + "\n".join(order_details["Товари у замовленні"])
        full_message = f"{response_message}\n\n{products_message}"

        keyboard = main_menu()

        await callback_query.message.edit_caption(
            caption=full_message,
            parse_mode="HTML",
            reply_markup=keyboard
        )

@dp.callback_query_handler(lambda c: c.data == 'my_order')
async def order_history_handler(callback_query: types.CallbackQuery):
    api_token = login()
    if not api_token:
        await callback_query.message.answer("Помилка при логіні. Спробуйте ще раз.")
        return

    user_id = callback_query.from_user.id
    telephone = get_user_phone(user_id)
    print(telephone)

    if not telephone:
        await callback_query.message.answer("Не знайдено номер телефону. Переконайтеся, що ви зареєстровані.")
        return

    order_data = get_last_order_by_telephone(api_token, telephone)
    keyboard = our_site_menu()

    if order_data is None or (isinstance(order_data, dict) and 'order' not in order_data):
        await callback_query.message.edit_caption(
            caption="<b>У вас ще не було замовлень, але це легко виправити 😉</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    order = order_data.get('order')
    if order:
        order_details = format_order_data(order_data)

        # Access the order directly without using a list
        order = order_data['order']

        # Extract order_id directly
        order_id = order['order_id']

        # Format the date as required
        order_date = order['date_added'].split(" ")[0]  # Get the date part
        order_time = order['date_added'].split(" ")[1][:5]  # Get the time part without seconds
        formatted_date = f"{order_date[8:10]}.{order_date[5:7]}.{order_date[0:4][2:]}"  # Format to DD.MM.YY
        total_amount = float(order['total'])  # Convert to float for formatting
        formatted_total = f"{total_amount:.2f}".rstrip('0').rstrip('.')  # Format and remove trailing zeros
        # Prepare the message with order details
        order_message = (
            f"<b>№ замовлення:</b> {order_id}\n\n"  # Use the extracted order_id directly
            f"<b>Сума замовлення:</b> {formatted_total} грн\n\n"
            f"<b>Статус замовлення:</b> {order['order_status'] if order['order_status'] else 'Не вказано'}\n\n"
            f"<b>Дата замовлення:</b> {order_time} ({formatted_date})\n\n"
            f"<b>Спосіб доставки:</b> {order['shipping_method']}\n\n"
            f"<b>Місто:</b> {order['payment_city']}\n\n"
            f"<b>Адреса:</b> {order['payment_address_1']}\n\n"
            f"<b>Товари у замовленні:</b>\n\n"
        )

        for product in order['order_products']:
            product_info = product['product_info']
            order_message += (
                f"- {product_info['name']} - {product_info['quantity']}шт {product_info['price']}грн\n\n"
                f"<b>Посилання на товар:</b> {product_info['url']}\n\n"
            )

        order_message += "\n" + "=" * 20 + "\n"
        
        print(order_message)
        keyboard2 = main_menu()
        await callback_query.message.edit_caption(
            caption=order_message,
            parse_mode="HTML",
            reply_markup=keyboard2
        )
        
        # await send_order_data_to_user(callback_query, order_details)
    else:
        await callback_query.message.edit_caption(
            caption="<b>У вас ще не було замовлень, але це легко виправити 😉</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )


user_orders_data = {}

@dp.callback_query_handler(lambda c: c.data == 'my_order_history')
async def order_history_handler(callback_query: types.CallbackQuery):
    api_token = login()
    if not api_token:
        await callback_query.message.answer("Помилка при логіні. Спробуйте ще раз.")
        return

    user_id = callback_query.from_user.id
    telephone = get_user_phone(user_id)

    if not telephone:
        await callback_query.message.answer("Не знайдено номер телефону. Переконайтеся, що ви зареєстровані.")
        return

    orders_data = get_all_last_orders_by_telephone(api_token, telephone)
    print(orders_data)
    keyboard = our_site_menu()

    if 'error' in orders_data:
        await callback_query.message.edit_caption(
            caption="<b>У вас ще не було замовлень, але це легко виправити 😉</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    # Store the orders data in the user's state
    user_orders_data[user_id] = {'orders_data': orders_data, 'keyboard': keyboard}

    # Initialize the order index and send the first order
    await show_order(callback_query, orders_data, 0, keyboard)

async def show_order(callback_query, orders_data, index, keyboard):
    # Total number of orders
    total_orders = len(orders_data['orders'])

    # Get the current order based on the index
    order_id = list(orders_data['orders'].keys())[index]
    order = orders_data['orders'][order_id]

    # Format the date as required
    order_date = order['date_added'].split(" ")[0]  # Get the date part
    order_time = order['date_added'].split(" ")[1][:5]  # Get the time part without seconds
    formatted_date = f"{order_date[8:10]}.{order_date[5:7]}.{order_date[0:4][2:]}"  # Format to DD.MM.YY
    total_amount = float(order['total'])  # Convert to float for formatting
    formatted_total = f"{total_amount:.2f}".rstrip('0').rstrip('.')  # Format and remove trailing zeros
    # Prepare the message with order details
    order_message = (
        f"<b>№ замовлення:</b> {order['order_id']}\n\n"
        f"<b>Сума замовлення:</b> {formatted_total} грн\n\n"
        f"<b>Статус замовлення:</b> {order['order_status'] if order['order_status'] else 'Не вказано'}\n\n"
        f"<b>Дата замовлення:</b> {order_time} ({formatted_date})\n\n"
        f"<b>Спосіб доставки:</b> {order['shipping_method']}\n\n"
        f"<b>Місто:</b> {order['payment_city']}\n\n"
        f"<b>Адреса:</b> {order['payment_address_1']}\n\n"
        f"<b>Товари у замовленні:</b>\n\n"
    )

    for product in order['order_products']:
        product_info = product['product_info']
        order_message += (
            f"- {product_info['name']} - {product_info['quantity']}шт {product_info['price']}грн\n\n"
            f"<b>Посилання на товар:</b> {product_info['url']}\n\n"
        )

    order_message += "\n" + "=" * 20 + "\n"

    # Create navigation buttons
    navigation_buttons = [
        types.InlineKeyboardButton("←", callback_data=f"prev_order:{index}"),
        types.InlineKeyboardButton("→", callback_data=f"next_order:{index}"),
        types.InlineKeyboardButton(text="🅼 Меню", callback_data="main_menu")
    ]

    keyboard_navigation = types.InlineKeyboardMarkup(row_width=2)
    keyboard_navigation.add(*navigation_buttons)

    # Use edit_message_caption to update the caption of the original message
    await callback_query.message.edit_caption(order_message, parse_mode="HTML", reply_markup=keyboard_navigation)


@dp.callback_query_handler(lambda c: c.data.startswith('prev_order:') or c.data.startswith('next_order:'))
async def navigate_orders(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Retrieve the stored orders data and keyboard for the user
    if user_id not in user_orders_data:
        await callback_query.answer("Дані замовлень не знайдено. Спробуйте ще раз.")
        return

    orders_data = user_orders_data[user_id]['orders_data']
    keyboard = user_orders_data[user_id]['keyboard']

    # Extract the action and current index
    action, index = callback_query.data.split(':')
    index = int(index)

    # Determine the new index based on the action
    if action == 'prev_order' and index > 0:
        index -= 1
    elif action == 'next_order' and index < len(orders_data['orders']) - 1:
        index += 1

    # Re-display the order for the new index
    await show_order(callback_query, orders_data, index, keyboard)



@dp.callback_query_handler(lambda c: c.data == "send_menu")
async def go_to_main_menu(callback_query: types.CallbackQuery):
    keyboard = get_start_keyboard()
    photo_path = 'data/hello.jpg'

    await callback_query.message.answer_photo(
        photo=types.InputFile(photo_path),
        caption="Вітаю! На зв’язку Cosmy асистент 👱🏻‍♀️\n Чим можу бути тобі корисною?",
        reply_markup=keyboard
    )




@dp.callback_query_handler(lambda c: c.data == 'send_review')
async def start_review_process(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Будь ласка оцініть якість спілкування від 1 до 5🤍.", reply_markup=get_rating_keyboard())


@dp.callback_query_handler(lambda c: c.data == 'cancelreview')
async def start_review_process(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Діалог завершений, дякую що звернулися в підтримку. Бажаєте залишити відгук?", reply_markup=send_review_menu())
    
@dp.callback_query_handler(lambda c: c.data.startswith('rate_'), state='*')
async def process_rating(callback_query: types.CallbackQuery, state: FSMContext):
    rating = int(callback_query.data.split('_')[1])
    await state.update_data(rating=rating)
    await ReviewStates.text.set()
    await callback_query.message.edit_text("Будь ласка, введіть текст відгуку:", reply_markup=send_review())
    
    
@dp.callback_query_handler(lambda c: c.data.startswith('sendreview'), state=ReviewStates.text)
async def process_rating(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_name = get_manager_name(user_id)
    user_data = await state.get_data()
    rating = user_data.get('rating')
    await bot.send_message(logs, f"<b>Відгук з консультації від користувача</b> @{user_name}, ID:{user_id}\n\n <b>Оцінка:</b> {rating}", parse_mode='HTML' )
    await bot.send_message(user_id, f"Дякуємо за зворотній зв’язок. Ми цінуємо вашу думку 💚", reply_markup=send_menu())
    await state.finish()
    
    # await asyncio.sleep(2)
    # keyboard = get_start_keyboard()
    # photo_path = 'data/hello.jpg'

    # await callback_query.message.answer_photo(
    #     photo=types.InputFile(photo_path),
    #     caption="Вітаю! На зв’язку Cosmy асистент 👱🏻‍♀️\n Чим можу бути тобі корисною?",
    #     reply_markup=keyboard
    # )

@dp.message_handler(state=ReviewStates.text)
async def process_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = get_manager_name(user_id)
    user_data = await state.get_data()
    rating = user_data.get('rating')
    text = message.text
    await bot.send_message(logs, f"<b>Відгук з консультації від користувача</b> @{user_name}, ID:{user_id}\n\n <b>Оцінка:</b> {rating}\n <b>Текст:</b> {text}", parse_mode='HTML')
    await bot.send_message(message.chat.id, f"Дякуємо за зворотній зв’язок. Ми цінуємо вашу думку 💚", reply_markup=send_menu())
    await state.finish()
    
    
    
    
    
    
    


@dp.callback_query_handler(lambda c: c.data == 'send_orderreview')
async def start_review_process(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Будь ласка оцініть якість спілкування від 1 до 5🤍.", reply_markup=get_order_rating_keyboard())


@dp.callback_query_handler(lambda c: c.data == 'cancelreview')
async def start_review_process(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Діалог завершений, дякую що звернулися в підтримку. Бажаєте залишити відгук?", reply_markup=send_review_menu())
    
@dp.callback_query_handler(lambda c: c.data.startswith('orderrate_'), state='*')
async def process_rating(callback_query: types.CallbackQuery, state: FSMContext):
    rating = int(callback_query.data.split('_')[1])
    await state.update_data(rating=rating)
    await ReviewOrderStates.text.set()
    await callback_query.message.edit_text("Будь ласка, введіть текст відгуку:", reply_markup=send_order_review())
    
    
@dp.callback_query_handler(lambda c: c.data.startswith('ordersendreview'), state=ReviewOrderStates.text)
async def process_rating(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_name = get_manager_name(user_id)
    user_data = await state.get_data()
    rating = user_data.get('rating')
    await bot.send_message(logs, f"<b>Відгук з замовлення від користувача</b> @{user_name}, ID:{user_id}\n\n <b>Оцінка:</b> {rating}", parse_mode='HTML' )
    await bot.send_message(user_id, f"Дякуємо за відгук! Ваша думка важлива для нас.🤍", reply_markup=send_menu())
    await state.finish()
    
    # await asyncio.sleep(2)
    # keyboard = get_start_keyboard()
    # photo_path = 'data/hello.jpg'

    # await callback_query.message.answer_photo(
    #     photo=types.InputFile(photo_path),
    #     caption="Вітаю! На зв’язку Cosmy асистент 👱🏻‍♀️\n Чим можу бути тобі корисною?",
    #     reply_markup=keyboard
    # )

@dp.message_handler(state=ReviewOrderStates.text)
async def process_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = get_manager_name(user_id)
    user_data = await state.get_data()
    rating = user_data.get('rating')
    text = message.text
    await bot.send_message(logs, f"<b>Відгук з замовлення від користувача</b> @{user_name}, ID:{user_id}\n\n <b>Оцінка:</b> {rating}\n <b>Текст:</b> {text}", parse_mode='HTML')
    await bot.send_message(message.chat.id, f"Дякуємо за відгук, ваша думка дужка важлива 🩶", reply_markup=send_menu())
    await state.finish()

###########################################################################################


@dp.callback_query_handler(lambda c: c.data == 'consultation')
async def order_history_handler(callback_query: types.CallbackQuery, state: FSMContext):
    
    
    if is_within_working_hours():
        greeting_message = (
            "Вітаю! З вами Cosmy асистент 👩‍💼\n Чи можу бути корисною? Напишіть своє питання, і я з радістю допоможу! "
        )
    else:
        greeting_message = (
            "Вітаємо! Наразі ми не на зв’язку, але обов’язково допоможемо. Будь ласка, залиште своє запитання, і ми відповімо вам у найближчий робочий час 🙂\n\n"
            "<b>Графік роботи:</b>\n"
            "Пн - Пт: 09:00 - 20:00\n"
            "Сб - Нд: 10:00 - 20:00"
        )
    
    
    await callback_query.message.answer(greeting_message, parse_mode='HTML', reply_markup=get_cancel_menu_keyboard())
    await SupportStates.waiting_for_question.set()


@dp.callback_query_handler(lambda c: c.data == "cancell", state=SupportStates.waiting_for_question)
async def go_to_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = get_start_keyboard()
    photo_path = 'data/hello.jpg'

    await callback_query.message.answer_photo(
        photo=types.InputFile(photo_path),
        caption="Вітаю! На зв’язку Cosmy асистент 👱🏻‍♀️\n Чим можу бути тобі корисною?",
        reply_markup=keyboard
    )
    await state.finish()

@dp.message_handler(state=SupportStates.waiting_for_question, content_types=types.ContentTypes.ANY)
async def receive_question(message: types.Message, state: FSMContext):
    keyboard = send_menu()
    if message.text and message.text.lower() == "відмінити":
        await state.finish()
        await message.answer("Щоб зв’язатися з нашою підтримкою, натисніть кнопку нижче🤗.", reply_markup=keyboard)
        return

    user_id = message.from_user.id
    user_name = message.from_user.username or message.from_user.full_name

    if message.text:
        user_question = message.text
    elif message.photo:
        user_question = "Прикріплене фото"
    elif message.video:
        user_question = "Прикріплене відео"
    elif message.document:
        user_question = "Прикріплений документ"
    elif message.audio:
        user_question = "Прикріплений аудіофайл"
    elif message.voice:
        user_question = "Голосове повідомлення"
    elif message.video_note:
        user_question = "Відеозаметка"
    elif message.media_group:
        user_question = "Медіагрупа"
    else:
        user_question = "Невідоме повідомлення"



    question_id = add_question_to_db(user_id, user_name, user_question)

    manager_id = get_manager_id_from_db(user_id)


    # Prepare manager message
    for manager_id in managers:
        manager_message = (
            f"Питання від користувача @{user_name}:\n"
            f"\n<b>{user_question}</b>\n"
        )

        if message.text:
            await bot.send_message(manager_id, manager_message, reply_markup=get_start_dialog_keyboard(question_id))
        elif message.photo:
            await bot.send_photo(manager_id, message.photo[-1].file_id, caption=manager_message, reply_markup=get_start_dialog_keyboard(question_id))
        elif message.video:
            await bot.send_video(manager_id, message.video.file_id, caption=manager_message, reply_markup=get_start_dialog_keyboard(question_id))
        elif message.document:
            await bot.send_document(manager_id, message.document.file_id, caption=manager_message, reply_markup=get_start_dialog_keyboard(question_id))
        elif message.audio:
            await bot.send_audio(manager_id, message.audio.file_id, caption=manager_message, reply_markup=get_start_dialog_keyboard(question_id))
        elif message.voice:
            await bot.send_voice(manager_id, message.voice.file_id, caption=manager_message, reply_markup=get_start_dialog_keyboard(question_id))
        elif message.video_note:
            await bot.send_video_note(manager_id, message.video_note.file_id, reply_markup=get_start_dialog_keyboard(question_id))
            
        await state.finish()

    # Determine response based on working hours
    if is_within_working_hours():
        greeting_message = (
            "Дякуємо за ваше питання! Наші менеджери зв'яжуться з вами найближчим часом. 🙌"
        )
    else:
        greeting_message = (
            "<b>Дякуємо за Ваше звернення 🤍</b>\n\n"
            "Наразі в нас неробочий час і наші менеджери не на зв’язку.\n"
            "Ми прийняли Ваш запит і відповімо якнайшвидше в робочі години. \n\n"
            "Бережіть себе! 🙌"
        )
        
        # Send greeting message
    await asyncio.sleep(1)
    await bot.send_chat_action(message.chat.id, action="typing")
    await asyncio.sleep(2)
    
    photo_path = 'data/hello.jpg'

    await message.answer(
        greeting_message,
        reply_markup=keyboard
    )






            
            
            
@dp.message_handler(state=SupportStates.waiting_for_new_question, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'video_note', 'media_group'])
async def forward_user_message_to_admin(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username or message.from_user.full_name

    data = await state.get_data()
    question_id = data.get('question_id')
    print(question_id)
    manager_id = get_manager_id_from_db(user_id)
    await state.update_data(manager_id=manager_id)

    reply_keyboard = get_reply_keyboard(question_id)

    if message.text:
        await bot.send_message(manager_id, f"Нове повідомлення від користувача @{user_name}:\n\n{message.text}", reply_markup=reply_keyboard)
    elif message.photo:
        await bot.send_photo(manager_id, message.photo[-1].file_id, caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
    elif message.video:
        await bot.send_video(manager_id, message.video.file_id, caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
    elif message.document:
        await bot.send_document(manager_id, message.document.file_id, caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
    elif message.audio:
        await bot.send_audio(manager_id, message.audio.file_id, caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
    elif message.voice:
        await bot.send_voice(manager_id, message.voice.file_id, caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
    elif message.video_note:
        await bot.send_video_note(manager_id, message.video_note.file_id, reply_markup=reply_keyboard)
    elif message.media_group:
        for media in message.media_group:
            media_type = media['type']
            if media_type == 'photo':
                await bot.send_photo(manager_id, media['file_id'], caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
            elif media_type == 'video':
                await bot.send_video(manager_id, media['file_id'], caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
            elif media_type == 'document':
                await bot.send_document(manager_id, media['file_id'], caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
            elif media_type == 'audio':
                await bot.send_audio(manager_id, media['file_id'], caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
            elif media_type == 'voice':
                await bot.send_voice(manager_id, media['file_id'], caption=f"Нове повідомлення від користувача @{user_name}", reply_markup=reply_keyboard)
            elif media_type == 'video_note':
                await bot.send_video_note(manager_id, media['file_id'], reply_markup=reply_keyboard)

    add_question_to_db(user_id, user_name, message.text or 'Media file')

    manager_state = dp.current_state(chat=manager_id, user=manager_id)
    await manager_state.finish()

    
def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(send_contacts_info, lambda c: c.data == 'check')