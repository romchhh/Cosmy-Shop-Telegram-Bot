from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)

    buttons = [
        InlineKeyboardButton(text="👆 Консультація", callback_data="consultation"),
        InlineKeyboardButton(text="📞 Контактний центр", callback_data="centre"),
        InlineKeyboardButton(text="🎁 Моє замовлення", callback_data="my_order"),
        InlineKeyboardButton(text="📜 Історія замовлень", callback_data="my_order_history"),
        InlineKeyboardButton(text="🔍 Перейти на сайт", url="https://cosmy.com.ua/")
    ]

    keyboard.add(*buttons)

    keyboard.row(
        InlineKeyboardButton(text="❓ Інформація", callback_data="info"),
        InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings")
    )

    return keyboard


def get_contacts_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton(text="📞 Контакти", callback_data="contacts"),
        InlineKeyboardButton(text="❓ Інформація", callback_data="info"),
        InlineKeyboardButton(text="📷 Інстаграм", url="https://www.instagram.com/cosmy/"),
        InlineKeyboardButton(text="🔍 Наш сайт", url="https://cosmy.com.ua/")
    ]
    
    keyboard.add(*buttons)
    
    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="main_menu")
    keyboard.add(menu_button)
    
    return keyboard


def get_contacts_contacts_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    view_map_button = InlineKeyboardButton(text="🗺 Переглянути карту", url="https://www.google.com/maps/place/%D0%9C%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD+%D0%BF%D1%80%D0%BE%D1%84%D0%B5%D1%81%D1%96%D0%B9%D0%BD%D0%BE%D1%97+%D0%BA%D0%BE%D1%81%D0%BC%D0%B5%D1%82%D0%B8%D0%BA%D0%B8+COSMY/@50.4279339,30.5253258,19z/data=!4m6!3m5!1s0x40d4cf36c605736d:0xf0302d0ee66dba6f!8m2!3d50.4278642!4d30.5252742!16s%2Fg%2F11vf1c5z1f?entry=ttu&g_ep=EgoyMDI0MTAwMi4xIKXMDSoASAFQAw%3D%3D")

    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="main_menu")
    
    keyboard.add(view_map_button)
    keyboard.add(menu_button)
    
    return keyboard


def get_info_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)

    buttons = [
        InlineKeyboardButton(text="🚚 Доставка і оплата", web_app=WebAppInfo(url="https://cosmy.com.ua/dostavka-i-oplata-ua")),
        InlineKeyboardButton(text="🦄 Космі клаб", web_app=WebAppInfo(url="https://cosmy.com.ua/cosmy-club-ua")),
        InlineKeyboardButton(text="📃 Сертифікати якості", web_app=WebAppInfo(url="https://cosmy.com.ua/sertifikati-jakosti-ua")),
        InlineKeyboardButton(text="💌 Подарункові сертифікати", web_app=WebAppInfo(url="https://cosmy.com.ua/podarochnie-sertifikati-ua")),
        InlineKeyboardButton(text="🤍 Наш космі", web_app=WebAppInfo(url="https://cosmy.com.ua/pro-magazin-ua")),
        InlineKeyboardButton(text="📋 Політика конфіденційності", web_app=WebAppInfo(url="https://cosmy.com.ua/povernennja-tovaru-ua")),
        InlineKeyboardButton(text="🤝 Публічна угода", web_app=WebAppInfo(url="https://cosmy.com.ua/umovi-zgodi-ua")),
        InlineKeyboardButton(text="👩‍💻 Блог", web_app=WebAppInfo(url="https://cosmy.com.ua/blog-ua"))
    ]

    keyboard.add(*buttons)

    keyboard.add(InlineKeyboardButton(text="🅼 Меню", callback_data="main_menu"))

    return keyboard


def get_settings_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    buttons = [
        InlineKeyboardButton(text="🔄 Оновити номер телефону", callback_data="change_number"),
    ]
    
    keyboard.add(*buttons)
    
    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="main_menu")
    keyboard.add(menu_button)
    
    return keyboard

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    back_button = InlineKeyboardButton("Назад", callback_data="back")
    keyboard.add(back_button)
    return keyboard

def get_cancel_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    back_button = InlineKeyboardButton("Назад", callback_data="cancel")
    keyboard.add(back_button)
    return keyboard


def get_cancel_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    back_button = InlineKeyboardButton("🅼 Меню", callback_data="cancell")
    keyboard.add(back_button)
    return keyboard

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="main_menu")
    keyboard.add(menu_button)
    
    return keyboard

def send_review_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    review_button = InlineKeyboardButton(text="🤍 Залишити відгук", callback_data="send_review")
    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="send_menu")
    keyboard.add(review_button, menu_button)
    
    return keyboard

def send_order_review_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    review_button = InlineKeyboardButton(text="🤍 Залишити відгук", callback_data="send_orderreview")
    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="send_menu")
    keyboard.add(review_button, menu_button)
    
    return keyboard

def send_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="send_menu")
    keyboard.add(menu_button)
    
    return keyboard

def our_site_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    site_button = InlineKeyboardButton(text="🔍 Перейти на сайт", url="https://cosmy.com.ua/")
    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="main_menu")
    
    keyboard.add(site_button, menu_button)
    
    return keyboard


def create_navigation_keyboard(current_index, total_orders):
    keyboard = InlineKeyboardMarkup(row_width=3)
    if current_index > 0:
        keyboard.insert(InlineKeyboardButton(text="<", callback_data=f"prev_order_{current_index-1}"))
    if current_index < total_orders - 1:
        keyboard.insert(InlineKeyboardButton(text=">", callback_data=f"next_order_{current_index+1}"))
    keyboard.add(InlineKeyboardButton(text="Меню", callback_data="main_menu"))
    return keyboard


def get_rating_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i in range(1, 6):
        button = InlineKeyboardButton(text=f"{i}", callback_data=f"rate_{i}")
        keyboard.insert(button)
    cancel_button = InlineKeyboardButton(text="← Назад", callback_data="cancelreview")
    keyboard.add(cancel_button)
    
    return keyboard


def get_order_rating_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i in range(1, 6):
        button = InlineKeyboardButton(text=f"{i}", callback_data=f"orderrate_{i}")
        keyboard.insert(button)
    cancel_button = InlineKeyboardButton(text="← Назад", callback_data="cancelreview")
    keyboard.add(cancel_button)
    
    return keyboard


def send_review():
    keyboard = InlineKeyboardMarkup(row_width=1)
    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="sendreview")
    keyboard.add(menu_button)
    
    return keyboard


def send_order_review():
    keyboard = InlineKeyboardMarkup(row_width=1)
    menu_button = InlineKeyboardButton(text="🅼 Меню", callback_data="ordersendreview")
    keyboard.add(menu_button)
    
    return keyboard