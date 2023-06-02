import sqlite3
import datetime

# создаем соединение с базой данных
conn = sqlite3.connect('mydatabase.db')
c = conn.cursor()

# создаем таблицу для хранения данных пользователей
c.execute('''
          CREATE TABLE IF NOT EXISTS users
          (id INTEGER PRIMARY KEY,
          kuda TEXT,
          otkuda TEXT,
          kogda TEXT,
          cena INTEGER,
          username TEXT,
          id_user INTEGER,
          timestamp DATETIME)
          ''')


# функция для получения всех записей из таблицы "users"
def get_all_users():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return rows


# функция для добавления новой записи в таблицу "users" на основе данных из словаря context.user_data
def add_user_from_context(user_data):
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (kuda, otkuda, kogda, cena, username, id_user) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_data['куда'], user_data['откуда'], user_data['когда'], user_data['цена'],
                   user_data['username'], user_data['id']))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_old_records(days=1):
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    c.execute("DELETE FROM users WHERE timestamp < ?", (cutoff_date,))
    conn.commit()
    conn.close()


def get_list(user_data):
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE kuda = ? AND otkuda = ?", (user_data['куда'], user_data['откуда']))
    rows = c.fetchall()
    conn.close()
    return rows


def get_my_list(user_data):
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id_user = ?", (user_data['id'],))
    rows = c.fetchall()
    conn.close()
    return rows


# закрываем соединение с базой данных
conn.close()
