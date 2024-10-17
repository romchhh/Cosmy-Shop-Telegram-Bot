import sqlite3
import datetime
from datetime import datetime, timedelta
import pytz

current_time = datetime.now()

conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

def create_table():
    conn = sqlite3.connect('data/data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            user_name TEXT,
            user_first_name TEXT,
            user_last_name TEXT,
            phone INTEGER
        )
    ''')
    conn.commit()

def add_user(user_id, user_name):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()
    if existing_user is None:
        cursor.execute('''
            INSERT INTO users (user_id, user_name)
            VALUES (?, ?)
        ''', (user_id, user_name))
        conn.commit()
        
def check_user(uid):
    cursor.execute(f'SELECT * FROM Users WHERE user_id = {uid}')
    user = cursor.fetchone()
    if user:
        return True
    return False
    
def check_phone_number(user_id):
    cursor.execute("SELECT phone FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user and user[0]:  # Перевіряємо, чи є номер телефону
        return True
    return False

def update_user_phone(user_id, phone_number):
    cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone_number, user_id))
    conn.commit()


def get_user_phone(user_id):
    cursor.execute("SELECT phone FROM users WHERE user_id = ?", (user_id,))
    phone = cursor.fetchone()
    
    if phone:
        phone_number = str(phone[0])
        if phone_number.startswith("38"):
            phone_number = phone_number[2:] 
        return phone_number
    return None

def get_user_id(phone):
    phone = str(phone)
    if not phone.startswith('38'):
        phone = '38' + phone

    cursor.execute("SELECT user_id FROM users WHERE phone = ?", (phone,))
    result = cursor.fetchone()

    if result:
        return result[0]  # Повертаємо перший елемент з кортежу (user_id)
    return None  # Якщо користувач не знайдений, повертаємо None




def create_questions_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            manager_id INTEGER,
            user_name TEXT,
            time NUMERIC,
            questions TEXT,
            answers TEXT,
            ended INTEGER  
        )
    ''')
    conn.commit()   

def add_question_to_db(user_id, user_name, question):
    cursor.execute('SELECT id, questions FROM questions WHERE user_id = ? AND ended = 0 ORDER BY id DESC LIMIT 1', (user_id,))
    row = cursor.fetchone()

    if row:
        # Якщо запис існує, додаємо нове питання через кому
        question_id, existing_questions = row
        updated_questions = f"{existing_questions}, {question}"
        cursor.execute('UPDATE questions SET questions = ? WHERE id = ?', (updated_questions, question_id))
    else:
        # Якщо запису немає, створюємо новий запис
        cursor.execute('''
            INSERT INTO questions (user_id, manager_id, user_name, time, questions, answers, ended)
            VALUES (?, ?, ?, datetime('now'), ?, '', 0)
        ''', (user_id, None, user_name, question))
        question_id = cursor.lastrowid

    conn.commit()

    return question_id


def check_if_question_exists(user_id):
    cursor.execute('SELECT id FROM questions WHERE user_id = ? AND ended = 0', (user_id,))
    return cursor.fetchone() is not None


def get_manager_id_from_db(user_id):
    cursor.execute('SELECT manager_id FROM questions WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
    manager_id = cursor.fetchone()[0]
    return manager_id


def end_dialog_in_db(question_id):
    cursor.execute('UPDATE questions SET ended = 1 WHERE id = ?', (question_id,))
    conn.commit()

def create_orders_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT,
        order_id TEXT,
        order_date TEXT,
        order_time TEXT,
        total_amount REAL,
        status TEXT,
        city TEXT,
        address TEXT,
        products TEXT,
        time_to_send TEXT,
        sent INTEGER DEFAULT 0
    )
    ''')
        
    conn.commit()

def save_order_to_db(phone, order_id, order_date, order_time, total_amount, status, city, address, products):
    formatted_products = "; ".join([f"{p['name']} - {p['quantity']}шт {p['price']}грн" for p in products])

    time_to_send = None
    if status == "Доставлено":
        # Отримуємо поточний час у Києві
        kyiv_tz = pytz.timezone('Europe/Kyiv')
        current_time = datetime.now(kyiv_tz)
        # Додаємо 3 дні
        time_to_send = current_time + timedelta(days=4)
        # Форматуємо час як рядок
        time_to_send = time_to_send.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
    INSERT INTO orders (phone, order_id, order_date, order_time, total_amount, status, city, address, products, time_to_send)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (phone, order_id, order_date, order_time, total_amount, status, city, address, formatted_products, time_to_send))

    conn.commit()


def get_order_status(order_id):
    cursor.execute('SELECT status FROM orders WHERE order_id = ?', (order_id,))
    result = cursor.fetchone()
    return result[0] if result else None



def fetch_posts_for_mailing(current_date, current_hour, current_minute_tens):
    current_minute_range_start = current_minute_tens - 29
    current_minute_range_end = current_minute_tens + 31
    cursor.execute('''
        SELECT * FROM orders WHERE 
        DATE(time_to_send) = ? AND 
        strftime('%H', time_to_send) = ? AND 
        CAST(strftime('%M', time_to_send) AS INTEGER) >= ? AND 
        CAST(strftime('%M', time_to_send) AS INTEGER) <= ?
    ''', (current_date, current_hour, current_minute_range_start, current_minute_range_end))
    
    print(current_minute_range_start, current_minute_range_end)
    
    print(current_minute_range_start, current_minute_range_end)
    
    posts = cursor.fetchall()
    return posts