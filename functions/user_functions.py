import logging
from database.admin_db import get_all_user_phones
from database.user_db import save_order_to_db, get_order_status, get_user_id, fetch_posts_for_mailing
from functions.cosmyapi import *
import asyncio, pytz, datetime
from main import bot, dp
from keyboards.user_keyboards import send_menu, send_review_menu, send_order_review_menu

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def order_history():
    logging.info("Запуск функції order_history")
    
    api_token = login()
    if not api_token:
        logging.error("Не вдалося отримати токен API")
        return

    user_phones = get_all_user_phones()
    logging.info(f"Отримано {len(user_phones)} телефонних номерів користувачів")

    for phone in user_phones:
        phone = str(phone)
        if phone.startswith("38"):
            phone = phone[2:]  

        logging.info(f"Отримання замовлення для телефону: {phone}")
        order_data = get_last_order_by_telephone(api_token, phone)
        
        if order_data is None or (isinstance(order_data, dict) and 'order' not in order_data):
            logging.warning(f"Замовлення для телефону {phone} не знайдено або воно порожнє")
            continue

        order = order_data.get('order')
        if order_data:
            logging.info(f"Форматування замовлення для телефону {phone}")
            order_details = format_order_data(order_data)
            
            order_id = order['order_id']
            logging.info(f"Замовлення № {order_id} отримано успішно")
            
            order_date = order['date_added'].split(" ")[0]  # Отримуємо дату
            order_time = order['date_added'].split(" ")[1][:5]  # Час без секунд
            formatted_date = f"{order_date[8:10]}.{order_date[5:7]}.{order_date[0:4][2:]}"  # Формат DD.MM.YY
            total_amount = float(order['total'])  # Конвертуємо у float для форматування
            formatted_total = f"{total_amount:.2f}".rstrip('0').rstrip('.')  # Формат і видалення нулів
            order_status = order['order_status'] if order['order_status'] else 'Не вказано'
            city = order['payment_city']
            address = order['payment_address_1']

            products = [{'name': product['product_info']['name'],
                         'quantity': product['product_info']['quantity'],
                         'price': product['product_info']['price']}
                        for product in order['order_products']]

            previous_status = get_order_status(order_id)  
            if previous_status is None:
                save_order_to_db(phone, order_id, formatted_date, order_time, formatted_total, order_status, city, address, products)
                logging.info(f"Замовлення № {order_id} успішно збережено.")
                
                if order_status == "Відправлено":
                    await send_order_update_message(phone, order_id, order_status, formatted_total, order_date, order_time, city, address, products)
                    
                elif order_status == "Доставлено":
                    save_order_to_db(phone, order_id, formatted_date, order_time, formatted_total, order_status, city, address, products)
            else:
                if previous_status != order_status and order_status == "Відправлено":
                    await send_order_update_message(phone, order_id, order_status, formatted_total, order_date, order_time, city, address, products)
                    logging.info(f"Статус замовлення № {order_id} змінено на 'Відправлено'. Повідомлення надіслано.")
                    
                elif previous_status != order_status and order_status == "Доставлено":
                    save_order_to_db(phone, order_id, formatted_date, order_time, formatted_total, order_status, city, address, products)
                    logging.info(f"Статус замовлення № {order_id} змінено на 'Доставлено'. Повідомлення надіслано.")
                else:
                    logging.info(f"Замовлення № {order_id} вже існує. Статус не змінився.")


async def send_order_update_message(phone, order_id, order_status, formatted_total, order_date, order_time, city, address, products):
    # order_message = (
    #     f"<b>№ замовлення:</b> {order_id}\n\n"  
    #     f"<b>Сума замовлення:</b> {formatted_total} грн\n\n"
    #     f"<b>Статус замовлення:</b> {order_status}\n\n"
    #     f"<b>Дата замовлення:</b> {order_time} ({order_date})\n\n"
    #     f"<b>Місто:</b> {city}\n\n"
    #     f"<b>Адреса:</b> {address}\n\n"
    #     f"<b>Товари у замовленні:</b>\n\n"
    # )

    # for product in products:
    #     order_message += (
    #         f"- {product['name']} - {product['quantity']}шт {product['price']}грн\n\n"
    #     )
        
    order_message = (f"Привіт, ваше замовлення №{order_id} відправлено, очікуйте на доставку найблищим часом.🤍")
        
    user_id = get_user_id(phone)
        
    try:
        await bot.send_message(chat_id=user_id, text=order_message, parse_mode='HTML', reply_markup=send_menu())
        logging.info(f"Повідомлення успішно надіслано на телефон: {phone}")
    except Exception as e:
        logging.error(f"Не вдалося надіслати повідомлення на телефон {phone}: {e}")




async def send_mailing():
    tz = pytz.timezone('Europe/Kyiv')
    now = datetime.datetime.now(tz)

    current_date = now.strftime('%Y-%m-%d')  
    current_hour = now.strftime('%H')      
    current_minute_tens = now.minute  
    
    print(current_minute_tens)
    orders = fetch_posts_for_mailing(current_date, current_hour, current_minute_tens)

    if orders:
        
        for order in orders:
            phone = order[1]
            order_id = order[2]
            
            user_id = get_user_id(phone)
            print("trying")
            print(user_id)
            await bot.send_message(user_id, "Дякуємо, що обираєте Cosmy ❤️. \n\n Поділіться, будь ласка, своїми враженнями про покупку, це допоможе нам стати ще краще !", reply_markup=send_order_review_menu())

    else:
        print("NO ORDERS")