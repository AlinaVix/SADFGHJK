import sqlite3

class SQL:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # Добавление пользователя в БД
    def add_user(self, id):
        query = "INSERT INTO users (id) VALUES(?)"
        with self.connection:
            return self.cursor.execute(query, (id,))

    # Проверка, есть ли пользователь в БД
    def user_exist(self, id):
        query = "SELECT * FROM users WHERE id = ?"
        with self.connection:
            result = self.cursor.execute(query, (id,)).fetchall()
            return bool(len(result))

    # Получить значение поля
    def get_field(self, table, id, field):
        query = f"SELECT {field} FROM {table} WHERE id = ?"
        with self.connection:
            result = self.cursor.execute(query, (id,)).fetchone()
            if result:
                return result[0]

    # Обновить значение поля
    def update_field(self, table, id, field, value):
        query = f"UPDATE {table} SET {field} = ? WHERE id = ?"
        with self.connection:
            self.cursor.execute(query, (value, id))

    def add_rec(self, name, rec, spisok, status):
        query = "INSERT INTO recept (name, rec, spisok, status) VALUES(?, ?, ?, ?)"
        with self.connection:
            self.cursor.execute(query, (name, rec, spisok, status))

    def get_recept_id(self, name):
        query = "SELECT id FROM recept WHERE name = ? ORDER BY id DESC LIMIT 1"
        with self.connection:
            result = self.cursor.execute(query, (name,)).fetchone()
            if result:
                return result[0]
            return None
    def add_my_rec(self, user_id, recipe_id):
        query = "INSERT INTO favourite_recipe (user_id, recipe_id) VALUES(?, ?)"
        with self.connection:
            self.cursor.execute(query, (user_id, recipe_id))

    def get_items_by_status(self, status):
        query = "SELECT * FROM items WHERE status = ?"
        with self.connection:
            return self.cursor.execute(query, (status,)).fetchall()

    def close(self):
        self.connection.close()

