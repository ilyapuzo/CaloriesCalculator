import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('recipes.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ingredients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        weight REAL,
        calories100 REAL,
        total real)""")
        self.conn.commit()

    def add_ingredient(self, name, weight, calories100, total):
        self.cursor.execute("""INSERT INTO ingredients(name, weight, calories100, total)
        VALUES (?, ?, ?, ?)
        """, (name, weight, calories100, total))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_ingredients(self):
        self.cursor.execute("""SELECT id, name, weight, calories100, total
        FROM ingredients""")
        return self.cursor.fetchall()

    def update_ingredient(self, ingredient_id, name, weight, calories100, total):
        self.cursor.execute("""UPDATE ingredients
        SET name = ?, weight = ?, calories100 = ?, total = ?
        WHERE id = ?""", (name, weight, calories100, total, ingredient_id))
        self.conn.commit()

    def delete_ingredient(self, ingredient_id):
        self.cursor.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
        self.conn.commit()