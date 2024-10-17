import logging
from database.admin_db import get_all_user_phones
from database.user_db import save_order_to_db
from functions.cosmyapi import *
import asyncio

# Налаштовуємо логування
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
            phone = phone[2:]  # Видаляємо префікс '38'

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

            save_order_to_db(phone, order_id, formatted_date, order_time, formatted_total, order_status, city, address, products)
            
            order_message = (
                f"<b>№ замовлення:</b> {order_id}\n\n"  
                f"<b>Сума замовлення:</b> {formatted_total} грн\n\n"
                f"<b>Статус замовлення:</b> {order_status}\n\n"
                f"<b>Дата замовлення:</b> {order_time} ({formatted_date})\n\n"
                f"<b>Спосіб доставки:</b> {order['shipping_method']}\n\n"
                f"<b>Місто:</b> {city}\n\n"
                f"<b>Адреса:</b> {address}\n\n"
                f"<b>Товари у замовленні:</b>\n\n"
            )

            for product in products:
                order_message += (
                    f"- {product['name']} - {product['quantity']}шт {product['price']}грн\n\n"
                )

            order_message += "\n" + "=" * 20 + "\n"
            logging.info(f"Повідомлення для замовлення № {order_id} згенеровано успішно")
            print(order_message)


if __name__ == "__main__":
    asyncio.run(order_history())
