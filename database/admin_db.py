import sqlite3

conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()


def get_users_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    return count

def get_active_users_count():
    cursor.execute("SELECT COUNT(*) FROM users WHERE phone IS NOT NULL")
    count = cursor.fetchone()[0]
    return count


def get_all_user_ids():
    cursor.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in cursor.fetchall()]
    return user_ids

def get_all_user_phones():
    cursor.execute('SELECT phone FROM users')
    user_ids = [row[0] for row in cursor.fetchall()]
    return user_ids


def save_answer(admin_id, answer, question_id):
    cursor = conn.cursor()
    
    # Отримуємо існуючі відповіді
    cursor.execute('SELECT answers FROM questions WHERE id = ?', (question_id,))
    row = cursor.fetchone()

    if row:
        existing_answers = row[0]
        if existing_answers:
            # Якщо відповіді вже є, додаємо нову через кому
            updated_answers = f"{existing_answers}, {answer}"
        else:
            # Якщо відповідей немає, просто зберігаємо нову
            updated_answers = answer
        
        cursor.execute('''
            UPDATE questions
            SET manager_id = ?, answers = ?
            WHERE id = ?
        ''', (admin_id, updated_answers, question_id))
        
        conn.commit()


def get_user_id_by_question_id(question_id):
    cursor.execute('SELECT user_id FROM questions WHERE id = ?', (question_id,))
    user_id = cursor.fetchone()[0]
    return user_id

def get_manager_id_by_question_id(question_id):
    cursor.execute('SELECT manager_id FROM questions WHERE id = ?', (question_id,))
    manager_id = cursor.fetchone()[0]
    return manager_id

def check_dialog(question_id):
    cursor.execute('SELECT manager_id, ended FROM questions WHERE id = ?', (question_id,))
    result = cursor.fetchone()
    return result


def has_active_dialog(manager_id):
    cursor.execute('SELECT id FROM questions WHERE manager_id = ? AND ended = 0 ORDER BY id DESC LIMIT 1', (manager_id,))
    result = cursor.fetchone()
    return result is not None


def get_active_dialogs(manager_id):
    cursor.execute('SELECT id, user_name FROM questions WHERE manager_id = ? AND ended = 0', (manager_id,))
    dialogs = cursor.fetchall()
    return dialogs

def get_completed_dialogs(manager_id):
    cursor.execute('SELECT id, user_name FROM questions WHERE manager_id = ? AND ended = 1', (manager_id,))
    dialogs = cursor.fetchall()
    return dialogs

def get_dialog_details(dialog_id):
    cursor.execute('SELECT user_name, time, questions, answers FROM questions WHERE id = ?', (dialog_id,))
    dialog = cursor.fetchone()
    return dialog


def get_admin_dialog_details(dialog_id):
    cursor.execute('SELECT user_name, time, questions, answers, manager_id, ended FROM questions WHERE id = ?', (dialog_id,))
    dialog = cursor.fetchone()
    return dialog

def get_manager_name(manager_id):
    cursor.execute('SELECT user_name FROM users WHERE user_id = ?', (manager_id,))
    manager_name = cursor.fetchone()
    return manager_name[0] if manager_name else "(менеджер не найден)"


def get_admin_active_dialogs():
    cursor.execute('SELECT id, user_name FROM questions WHERE  ended = 0', ())
    dialogs = cursor.fetchall()
    return dialogs

def get_admin_completed_dialogs():
    cursor.execute('SELECT id, user_name FROM questions WHERE ended = 1', ())
    dialogs = cursor.fetchall()
    return dialogs


def get_users_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    return count

def get_all_user_ids():
    cursor.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in cursor.fetchall()]
    return user_ids
