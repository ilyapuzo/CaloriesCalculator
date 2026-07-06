import sqlite3, csv, json

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

    def export_to_csv(self, file_path):
        ingredients = self.get_ingredients()
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'weight', 'calories100', 'total'])
            writer.writerows(ingredients)
        return len(ingredients)

    def export_to_json(self, file_path):
        ingredients = self.get_ingredients()
        data = []
        for ing in ingredients:
            data.append({'id': ing[0],'name': ing[1],'weight': ing[2],'calories100': ing[3],'total': ing[4]})
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return len(ingredients)

    def import_from_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            count = 0
            for row in reader:
                if len(row) >= 5:
                    try:
                        name = row[1]
                        weight = float(row[2])
                        calories100 = float(row[3])
                        total = float(row[4])
                        self.add_ingredient(name, weight, calories100, total)
                        count += 1
                    except (ValueError, IndexError) as e:
                        print(f"Ошибка в строке {row}: {e}")
                        continue
        return count

    def import_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            count = 0
            for item in data:
                try:
                    self.add_ingredient(item['name'],item['weight'],item['calories100'],item['total'])
                    count += 1
                except (KeyError, TypeError) as e:
                    print(f"Ошибка в записи {item}: {e}")
                    continue
        return count
