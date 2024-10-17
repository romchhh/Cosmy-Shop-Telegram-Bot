from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from main import bot, dp
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
import asyncio
from keyboards.admin_keyboards import get_admin_keyboard, get_back_keyboard, get_preview_markup, get_back2_keyboard
from database.admin_db import *
from filters.filters import IsAdmin, IsManager
from states.admin_states import BroadcastState, AdminStates
from states.user_states import SupportStates
from data.config import administrators, managers
from database.user_db import end_dialog_in_db
from keyboards.user_keyboards import send_menu, send_menu, send_review_menu
from keyboards.admin_keyboards import get_admin_keyboard, get_manager_keyboard, start_admin_keyboard, start_manager_keyboard, get_cancel_keyboard

    
@dp.callback_query_handler(IsAdmin(), text='user_statistic')
async def statistic_handler(callback_query: CallbackQuery):
    total_users = get_users_count()
    active_users = get_active_users_count()

    response_message = (
            f"👥 Загальна кількість користувачів: {total_users}\n"
            f"📱 Кількість активних користувачів: {active_users}\n"
        )
    
    keyboard = get_back2_keyboard()
    await callback_query.message.edit_text(response_message, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query_handler(IsAdmin(), text='mailing')
async def send_broadcast_prompt(call: CallbackQuery):
    keyboard = get_back_keyboard()
    await call.message.edit_text(
        "Введіть текст розсилки (ви можете використовувати HTML-теги для форматування, але вони будуть відображатися як текст):\n\n"
        "&lt;b&gt;жирний&lt;/b&gt; — <b>жирний</b>\n"
        "&lt;i&gt;курсив&lt;/i&gt; — <i>курсив</i>\n"
        "&lt;u&gt;підкреслений&lt;/u&gt; — <u>підкреслений</u>\n"
        "&lt;s&gt;закреслений&lt;/s&gt; — <s>закреслений</s>\n"
        "&lt;pre&gt;моноширинний&lt;/pre&gt; — <pre>моноширинний</pre>\n"
        "&lt;a href='https://example.com'&gt;посилання&lt;/a&gt; — <a href='https://example.com'>посилання</a>\n\n", 
        reply_markup=keyboard, parse_mode="HTML"
    )
    await BroadcastState.text.set()


@dp.message_handler(state=BroadcastState.text)
async def process_broadcast_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await message.answer("Будь ласка, надішліть фото для повідомлення або натисніть /skip, щоб пропустити цей крок:")
    await BroadcastState.photo.set()


@dp.message_handler(content_types=['photo', 'video', 'animation'], state=BroadcastState.photo)
async def process_broadcast_media(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.content_type == 'photo':
            data['photo'] = message.photo[-1].file_id
            data['video'] = None
        elif message.content_type in ['video', 'animation']:  # Обробляємо відео і гіфки як відео
            data['video'] = message.video.file_id if message.content_type == 'video' else message.animation.file_id
            data['photo'] = None
            
    await message.answer("Будь ласка, введіть назву кнопки або натисніть /skip, щоб пропустити цей крок:")
    await BroadcastState.button_name.set()



@dp.message_handler(state=BroadcastState.button_name)
async def process_button_name(message: types.Message, state: FSMContext):
    if message.text == '/skip':
        async with state.proxy() as data:
            data['button_name'] = None
        await message.answer("Будь ласка, введіть URL для кнопки або натисніть /skip, щоб пропустити цей крок:")
        await BroadcastState.button_url.set()
    else:
        async with state.proxy() as data:
            data['button_name'] = message.text
        await message.answer("Будь ласка, введіть URL для кнопки або натисніть /skip, щоб пропустити цей крок:")
        await BroadcastState.button_url.set()


@dp.message_handler(state=BroadcastState.button_url)
async def process_button_url(message: types.Message, state: FSMContext):
    if message.text == '/skip':
        async with state.proxy() as data:
            data['button_url'] = None
        await send_preview(message.chat.id, data, state)
        await BroadcastState.preview.set()
    else:
        async with state.proxy() as data:
            data['button_url'] = message.text
        await send_preview(message.chat.id, data, state)
        await BroadcastState.preview.set()


async def send_preview(chat_id, data, state: FSMContext):
    preview_markup = InlineKeyboardMarkup()
    if 'button_name' in data and 'button_url' in data and data['button_name'] and data['button_url']:
        button = InlineKeyboardButton(text=data['button_name'], url=data['button_url'])
        preview_markup.add(button)
        
    text = "📣 *Попередній перегляд розсилки:*\n\n"
    text += data.get('text', '')

    if 'photo' in data and data['photo'] is not None:
        await bot.send_photo(chat_id, data['photo'], caption=text, parse_mode='HTML', reply_markup=preview_markup)
    elif 'video' in data and data['video'] is not None:
        await bot.send_video(chat_id, data['video'], caption=text, parse_mode='HTML', reply_markup=preview_markup)
    else:
        await bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=preview_markup)

    await bot.send_message(chat_id, "Все в порядку?", reply_markup=get_preview_markup())

    async with state.proxy() as stored_data:
        stored_data.update(data)


@dp.callback_query_handler(text="send_broadcast", state=BroadcastState.preview)
async def send_broadcast_to_users_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('text', '')
    photo = data.get('photo')
    video = data.get('video')
    button_name = data.get('button_name')
    button_url = data.get('button_url')
    await send_broadcast_to_users(text, photo, video, button_name, button_url, call.message.chat.id)
    await call.answer()
    await state.finish()


@dp.message_handler(commands=['skip'], state=[BroadcastState.text, BroadcastState.photo, BroadcastState.button_name, BroadcastState.button_url])
async def skip_step(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'text' not in data:
            data['text'] = None
        if 'photo' not in data:
            data['photo'] = None
        if 'button_name' not in data:
            data['button_name'] = None
        if 'button_url' not in data:
            data['button_url'] = None
            
    current_state = await state.get_state()
    if current_state == BroadcastState.text.state:
        await BroadcastState.photo.set()
        await message.answer("Будь ласка, надішліть фото для повідомлення або натисніть /skip, щоб пропустити цей крок:")
    elif current_state == BroadcastState.photo.state:
        await BroadcastState.button_name.set()
        await message.answer("Будь ласка, введіть назву кнопки або натисніть /skip, щоб пропустити цей крок:")
    elif current_state == BroadcastState.button_name.state:
        await BroadcastState.button_url.set()
        await message.answer("Будь ласка, введіть URL для кнопки або натисніть /skip, щоб пропустити цей крок:")
    elif current_state == BroadcastState.button_url.state:
        await send_preview(message.chat.id, data, state)
        await BroadcastState.preview.set()


async def send_broadcast_to_users(text, photo, video, button_name, button_url, chat_id):
    try:
        user_ids = get_all_user_ids()
        for user_id in user_ids:
            if text.strip():
                try:
                    # Initialize the markup
                    markup = InlineKeyboardMarkup()
                    
                    # Add the optional button if provided
                    if button_name and button_url:
                        button = InlineKeyboardButton(text=button_name, url=button_url)
                        markup.add(button)
                    
                    # Always add the "🅼 Меню" button
                    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="send_menu")
                    markup.add(menu_button)

                    # Send the appropriate message with photo, video, or just text
                    if photo:
                        await bot.send_photo(user_id, photo, caption=text, parse_mode='HTML', reply_markup=markup)
                    elif video:
                        await bot.send_video(user_id, video, caption=text, parse_mode='HTML', reply_markup=markup)
                    else:
                        await bot.send_message(user_id, text, parse_mode='HTML', reply_markup=markup)
                except Exception as e:
                    print(f"Помилка при надсиланні повідомлення користувачу з ID {user_id}: {str(e)}")

        await bot.send_message(chat_id, f"Розсилка успішно надіслана {len(user_ids)} користувачам.")
        admin_keyboard = get_admin_keyboard()
        await bot.send_message(chat_id, "Адмін-панель", reply_markup=admin_keyboard)
    except Exception as e:
        await bot.send_message(chat_id, f"Сталася помилка: {str(e)}")
     
        

@dp.callback_query_handler(text="cancel_broadcast", state=BroadcastState.preview)
async def cancel_broadcast_callback(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    await state.finish()
    await call.message.answer("Розсилка скасована.")
    admin_keyboard = get_admin_keyboard()
    await bot.send_message(user_id, "Адмін-панель 👨🏼‍💻", reply_markup=admin_keyboard)
    await call.answer()


@dp.callback_query_handler(text="back", state=BroadcastState.text)
async def handle_back(callback_query: CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)
    admin_keyboard = get_admin_keyboard()
    await callback_query.message.edit_text("Адмін-панель 👨🏼‍💻", reply_markup=admin_keyboard)
    
@dp.callback_query_handler(text="back2")
async def handle_back(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    admin_keyboard = get_admin_keyboard()
    await callback_query.message.edit_text("Адмін-панель 👨🏼‍💻", reply_markup=admin_keyboard)
    
####################################################################


@dp.callback_query_handler(IsManager(), lambda c: c.data.startswith('start_dialog:'), state="*")
async def start_dialog(callback_query: CallbackQuery, state: FSMContext):
    question_id = int(callback_query.data.split(':')[1])
    result = check_dialog(question_id)
    user_id = callback_query.from_user.id
    asker_id = get_user_id_by_question_id(question_id)

    # if has_active_dialog(user_id):
    #     await callback_query.answer("Нельзя начинать два диалога одновременно.", show_alert=True)
    #     return

    if result:
        manager_id, ended = result
        if manager_id is not None and manager_id != callback_query.from_user.id:
            await callback_query.answer("Інший менеджер вже веде переписку.", show_alert=True)
            return

        if user_id == asker_id:
            await callback_query.answer("Не можна починати переписку з самим з собою.", show_alert=True)
            return
        
        if ended == 1:
            await callback_query.answer("Діалог закінчений.", show_alert=True)
            return

    await callback_query.message.answer("Ви почали діалог. Введіть вашу відповідь.", reply_markup=get_cancel_keyboard())
    await AdminStates.waiting_for_first_answer.set()
    await state.update_data(question_id=question_id)
    
    await dp.current_state(chat=asker_id, user=asker_id).set_state(SupportStates.waiting_for_new_question)
    await dp.current_state(chat=asker_id, user=asker_id).update_data(manager_id=user_id, question_id=question_id)


@dp.message_handler(state=AdminStates.waiting_for_first_answer, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'video_note', 'media_group'])
async def forward_admin_message_to_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question_id = data.get('question_id')
    user_id = get_user_id_by_question_id(question_id)
    if user_id in administrators:
        keyboard = start_admin_keyboard()
    elif user_id in managers:
        keyboard = start_manager_keyboard()
    else:
        keyboard = start_manager_keyboard()

    if message.text and message.text.lower() == "завершити діалог":
        end_dialog_in_db(question_id)
        
        await state.finish()

        await message.answer("Діалог завершений.", reply_markup=keyboard)
        
        user_state = dp.current_state(chat=user_id, user=user_id)
        await user_state.finish()

        await bot.send_message(user_id, "Чат завершено ✔️. \n\n Оцініть, будь ласка, роботу нашого менеджера - це допоможе нам стати краще 💚", reply_markup=send_review_menu())
        return

    if message.text:
        await bot.send_message(user_id, message.text)
    elif message.photo:
        await bot.send_photo(user_id, message.photo[-1].file_id) 
    elif message.video:
        await bot.send_video(user_id, message.video.file_id)
    elif message.document:
        await bot.send_document(user_id, message.document.file_id)
    elif message.audio:
        await bot.send_audio(user_id, message.audio.file_id)
    elif message.voice:
        await bot.send_voice(user_id, message.voice.file_id)
    elif message.video_note:
        await bot.send_video_note(user_id, message.video_note.file_id)
    elif message.media_group:
        for media in message.media_group:
            media_type = media['type']
            if media_type == 'photo':
                await bot.send_photo(user_id, media['file_id'])
            elif media_type == 'video':
                await bot.send_video(user_id, media['file_id'])
            elif media_type == 'document':
                await bot.send_document(user_id, media['file_id'])
            elif media_type == 'audio':
                await bot.send_audio(user_id, media['file_id'])
            elif media_type == 'voice':
                await bot.send_voice(user_id, media['file_id'])
            elif media_type == 'video_note':
                await bot.send_video_note(user_id, media['file_id'])

    save_answer(message.from_user.id, message.text or 'Media file', question_id)
    
    # await state.finish()


#############################

@dp.callback_query_handler(lambda c: c.data.startswith('reply_'))
async def process_reply_button(callback_query: types.CallbackQuery, state: FSMContext):
    question_id = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id

    user_state = dp.current_state(chat=user_id, user=user_id)
    print(user_state)
    if user_state:
        await user_state.finish()
        print("finished")
        
    result = check_dialog(question_id)
    if result:
        manager_id, ended = result
        if manager_id is not None and manager_id != callback_query.from_user.id:
            await callback_query.answer("Вже інший менеджер веде переписку", show_alert=True)
            return

        if ended == 1:
            await callback_query.answer("Діалог вже закінчений.", show_alert=True)
            return

    
    await AdminStates.waiting_for_answer.set()
    await state.update_data(question_id=question_id)
    await callback_query.message.answer("Введіть вашу відповідь:", reply_markup=get_cancel_keyboard())


@dp.message_handler(state=AdminStates.waiting_for_answer, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'video_note', 'media_group'])
async def forward_admin_message_to_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question_id = data.get('question_id')
    user_id = get_user_id_by_question_id(question_id)
    if user_id in administrators:
        keyboard = start_admin_keyboard()
    elif user_id in managers:
        keyboard = start_manager_keyboard()
    else:
        keyboard = start_manager_keyboard()

    if message.text and message.text.lower() == "завершити діалог":
        end_dialog_in_db(question_id)
        await state.finish()
        await message.answer("Діалог завершений.", reply_markup=keyboard)
        
        user_state = dp.current_state(chat=user_id, user=user_id)
        await user_state.finish()
        await bot.send_message(user_id, "Чат завершено ✔️. \n\n Оцініть, будь ласка, роботу нашого менеджера - це допоможе нам стати краще 💚", reply_markup=send_review_menu())
        return

    if message.text:
        await bot.send_message(user_id, message.text)
    elif message.photo:
        await bot.send_photo(user_id, message.photo[-1].file_id) 
    elif message.video:
        await bot.send_video(user_id, message.video.file_id)
    elif message.document:
        await bot.send_document(user_id, message.document.file_id)
    elif message.audio:
        await bot.send_audio(user_id, message.audio.file_id)
    elif message.voice:
        await bot.send_voice(user_id, message.voice.file_id)
    elif message.video_note:
        await bot.send_video_note(user_id, message.video_note.file_id)
    elif message.media_group:
        for media in message.media_group:
            media_type = media['type']
            if media_type == 'photo':
                await bot.send_photo(user_id, media['file_id'])
            elif media_type == 'video':
                await bot.send_video(user_id, media['file_id'])
            elif media_type == 'document':
                await bot.send_document(user_id, media['file_id'])
            elif media_type == 'audio':
                await bot.send_audio(user_id, media['file_id'])
            elif media_type == 'voice':
                await bot.send_voice(user_id, media['file_id'])
            elif media_type == 'video_note':
                await bot.send_video_note(user_id, media['file_id'])

    save_answer(message.from_user.id, message.text or 'Media file', question_id)


@dp.callback_query_handler(IsManager(), lambda c: c.data in ["active_dialogs", "completed_dialogs"], state="*")
async def handle_dialogs(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data_type = callback_query.data

    if data_type == "adminactive_dialogs":
        dialogs = get_admin_active_dialogs()
        title = "Aктивні діалоги:"
    elif data_type == "admincompleted_dialogs":
        dialogs = get_admin_completed_dialogs()
        title = "Завершені діалоги:"

    keyboard = InlineKeyboardMarkup(row_width=1)
    # Add buttons for each dialog
    for dialog_id, _ in dialogs:
        keyboard.add(InlineKeyboardButton(text=f"Діалог {dialog_id}", callback_data=f"dialog_{dialog_id}"))
    
    if dialogs:
        await callback_query.message.edit_text(text=title, reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(text=f"{title}: \n\nНемає доступних діалогів.")
    
    await callback_query.answer()


@dp.callback_query_handler(IsManager(), lambda c: c.data.startswith("dialog_"), state="*")
async def handle_specific_dialog(callback_query: CallbackQuery, state: FSMContext):
    dialog_id = int(callback_query.data.split("_")[1])
    
    dialog = get_admin_dialog_details(dialog_id)
    
    if dialog:
        user_name, time, questions, answers, manager_id, is_active = dialog  # Add 'is_active' field
        
        questions_list = questions.split(", ")
        answers_list = answers.split(", ") if answers else ["(без відповіді)"] * len(questions_list)

        dialog_parts = []
        for i, (question, answer) in enumerate(zip(questions_list, answers_list)):
            dialog_parts.append(f"<b>Питання {i+1}:</b> {question}")
            dialog_parts.append(f"<b>Відповідь {i+1}:</b> {answer}")
        
        formatted_dialog = "\n\n".join(dialog_parts)
        
        manager_name = get_manager_name(manager_id)
        
        message_text = (
            f"<b>Діалог №{dialog_id}</b>\n"
            f"<b>Користувач:</b> @{user_name}\n"
            f"<b>Менеджер:</b> @{manager_name}\n"
            f"<b>Початок діалогу:</b> {time}\n\n"
            f"{formatted_dialog}"
        )

        keyboard = InlineKeyboardMarkup(row_width=1)
        if not is_active:  
            keyboard.add(InlineKeyboardButton(text="Завершити діалог", callback_data=f"managerenddialog_{dialog_id}"))
        keyboard.add(InlineKeyboardButton(text="Назад", callback_data="manager_back"))

        await callback_query.message.edit_text(message_text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(f"Діалог {dialog_id} не знайдений.", parse_mode="HTML")
    
    await callback_query.answer()



@dp.callback_query_handler(lambda c: c.data.startswith("managerenddialog_"), state="*")
async def handle_end_dialog(callback_query: CallbackQuery, state: FSMContext):
    dialog_id = int(callback_query.data.split("_")[1])

    end_dialog_in_db(dialog_id)
    asker_id = get_user_id_by_question_id(dialog_id)
    keyboard = send_menu()
    await bot.send_message(asker_id, "Діалог завершений, дякую що звернулися в підтримку.", reply_markup=keyboard)
        
    await callback_query.answer(f"Діалог №{dialog_id} успішно завершено.", show_alert=True)
    await asyncio.sleep(2)
    admin_keyboard = get_admin_keyboard()
    await callback_query.message.edit_text("Адмін панель", reply_markup=admin_keyboard)

    

    
@dp.callback_query_handler(lambda c: c.data == "manager_back", state="*")
async def handle_admin_back(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id in administrators:
        manager_keyboard = get_manager_keyboard()
        await callback_query.message.edit_text("Менеджер панель", reply_markup=manager_keyboard)
    else:
        await callback_query.answer("У вас немає прав доступу до адмін панелі.", show_alert=True)
    await callback_query.answer()

####################################################################


@dp.callback_query_handler(IsAdmin(), lambda c: c.data in ["adminactive_dialogs", "admincompleted_dialogs"], state="*")
async def handle_dialogs(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data_type = callback_query.data

    if data_type == "adminactive_dialogs":
        dialogs = get_admin_active_dialogs()
        title = "Aктивні діалоги:"
    elif data_type == "admincompleted_dialogs":
        dialogs = get_admin_completed_dialogs()
        title = "Завершені діалоги:"

    keyboard = InlineKeyboardMarkup(row_width=1)
    # Add buttons for each dialog
    for dialog_id, _ in dialogs:
        keyboard.add(InlineKeyboardButton(text=f"Діалог {dialog_id}", callback_data=f"admindialog_{dialog_id}"))
    
    if dialogs:
        await callback_query.message.edit_text(text=title, reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(text=f"{title}: \n\nНемає доступних діалогів.")
    
    await callback_query.answer()


@dp.callback_query_handler(IsAdmin(), lambda c: c.data.startswith("admindialog_"), state="*")
async def handle_specific_dialog(callback_query: CallbackQuery, state: FSMContext):
    dialog_id = int(callback_query.data.split("_")[1])
    
    dialog = get_admin_dialog_details(dialog_id)
    
    if dialog:
        user_name, time, questions, answers, manager_id, is_active = dialog  # Add 'is_active' field
        
        questions_list = questions.split(", ")
        answers_list = answers.split(", ") if answers else ["(без відповіді)"] * len(questions_list)

        dialog_parts = []
        for i, (question, answer) in enumerate(zip(questions_list, answers_list)):
            dialog_parts.append(f"<b>Питання {i+1}:</b> {question}")
            dialog_parts.append(f"<b>Відповідь {i+1}:</b> {answer}")
        
        formatted_dialog = "\n\n".join(dialog_parts)
        
        manager_name = get_manager_name(manager_id)
        
        message_text = (
            f"<b>Діалог №{dialog_id}</b>\n"
            f"<b>Користувач:</b> @{user_name}\n"
            f"<b>Менеджер:</b> @{manager_name}\n"
            f"<b>Початок діалогу:</b> {time}\n\n"
            f"{formatted_dialog}"
        )

        keyboard = InlineKeyboardMarkup(row_width=1)
        if not is_active:  
            keyboard.add(InlineKeyboardButton(text="Завершити діалог", callback_data=f"adminenddialog_{dialog_id}"))
        keyboard.add(InlineKeyboardButton(text="Назад", callback_data="admin_back"))

        await callback_query.message.edit_text(message_text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(f"Діалог {dialog_id} не знайдений.", parse_mode="HTML")
    
    await callback_query.answer()
    


@dp.callback_query_handler(lambda c: c.data.startswith("adminenddialog_"), state="*")
async def handle_end_dialog(callback_query: CallbackQuery, state: FSMContext):
    dialog_id = int(callback_query.data.split("_")[1])

    end_dialog_in_db(dialog_id)
    asker_id = get_user_id_by_question_id(dialog_id)
    keyboard = send_menu()
    await bot.send_message(asker_id, "Діалог завершений, дякую що звернулися в підтримку.", reply_markup=keyboard)
        
    await callback_query.answer("Діалог успішно завершено.", show_alert=True)
    await asyncio.sleep(2)
    admin_keyboard = get_admin_keyboard()
    await callback_query.message.edit_text("Адмін панель", reply_markup=admin_keyboard)

    
@dp.callback_query_handler(lambda c: c.data == "admin_back", state="*")
async def handle_admin_back(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id in administrators:
        admin_keyboard = get_admin_keyboard()
        await callback_query.message.edit_text("Адмін панель", reply_markup=admin_keyboard)
    else:
        await callback_query.answer("У вас немає прав доступу до адмін панелі.", show_alert=True)
    await callback_query.answer()

def register_admin_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(statistic_handler, lambda c: c.data == 'check')