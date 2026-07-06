import os.path

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QFileDialog, QShortcut
from PyQt5.uic import loadUi
from database import Database
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSettings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("calculator.ui", self)
        with open("style.qss", "r", encoding="utf-8") as file:
            self.setStyleSheet(file.read())

        if not os.path.exists("recipes.db"):
            QSettings("RecipeApp", "Calculator").clear()

        self.settings = QSettings("RecipeApp", "Calculator")
        theme = self.settings.value("theme", "light")
        self.apply_theme(theme)


        self.setup_table()
        self.connect_signals()
        self.total_weight = 0
        self.total_calories = 0
        self.db = Database()
        self.current_id = None
        self.load_ingredients()

        people = self.settings.value("people", 1, type=int)
        self.spinPeople.setValue(people)
        self.setup_icons()
        self.setup_shortcuts()
        self.load_saved_photo()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.toggle_theme)
        QShortcut(QKeySequence("Return"), self).activated.connect(self.add_ingredient)
        QShortcut(QKeySequence("Backspace"), self).activated.connect(self.delete_ingredient)

    def setup_table(self):
        self.tableIngredients.setColumnCount(5)
        self.tableIngredients.setHorizontalHeaderLabels(["ID", "Ингредиент", "Вес (г)", "Ккал / 100 г", "Всего ккал"])
        self.tableIngredients.setColumnHidden(0, True)
        self.tableIngredients.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableIngredients.verticalHeader().setVisible(False)

    def connect_signals(self):
        self.btnAdd.clicked.connect(self.add_ingredient)
        self.btnDelete.clicked.connect(self.delete_ingredient)
        self.btnEdit.clicked.connect(self.edit_ingredient)
        self.tableIngredients.cellClicked.connect(self.load_to_fields)
        self.btnLoadPhoto.clicked.connect(self.load_photo)
        self.spinPeople.valueChanged.connect(self.update_per_serving)
        self.spinPeople.valueChanged.connect(self.save_people)
        self.btnExport.clicked.connect(self.export_data)
        self.btnImport.clicked.connect(self.import_data)

    def add_ingredient(self):
        ingredient = self.lineIngredient.text().strip()
        if ingredient == "":
            return

        weight = self.spinWeight.value()
        calories100 = self.spinCalories100.value()
        total_calories = weight * calories100 / 100

        ingredient_id = self.db.add_ingredient(ingredient, weight, calories100, total_calories)

        row = self.tableIngredients.rowCount()
        self.tableIngredients.insertRow(row)
        self.tableIngredients.setItem(row, 0, QtWidgets.QTableWidgetItem(str(ingredient_id)))
        self.tableIngredients.setItem(row, 1, QtWidgets.QTableWidgetItem(ingredient))
        self.tableIngredients.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{weight:.0f}"))
        self.tableIngredients.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{calories100:.0f}"))
        self.tableIngredients.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total_calories:.1f}"))


        self.lineIngredient.clear()
        self.spinWeight.setValue(0)
        self.spinCalories100.setValue(0)

        self.update_totals()

    def update_totals(self):
        self.total_weight = 0
        self.total_calories = 0

        for row in range(self.tableIngredients.rowCount()):
            item_weight = self.tableIngredients.item(row, 2)
            item_calories = self.tableIngredients.item(row, 4)
            if item_weight is None or item_calories is None:
                continue
            try:
                weight = float(item_weight.text())
                calories = float(item_calories.text())
            except:
                continue

            self.total_weight += weight
            self.total_calories += calories

        if hasattr(self, "labelTotalWeight"):
            self.labelTotalWeight.setText(f"Общий вес: {self.total_weight:.0f} г")

        if hasattr(self, "labelTotalCalories"):
            self.labelTotalCalories.setText(f"Общая калорийность: {self.total_calories:.1f} ккал")

        self.update_per_serving()

    def delete_ingredient(self):
        row = self.tableIngredients.currentRow()
        if row == -1:
            return
        ingredient_id = int(self.tableIngredients.item(row, 0).text())
        self.db.delete_ingredient(ingredient_id)
        self.tableIngredients.removeRow(row)
        self.update_totals()

    def edit_ingredient(self):
        row = self.tableIngredients.currentRow()
        if row == -1:
            return
        if self.current_id is None:
            return

        ingredient = self.lineIngredient.text().strip()
        if ingredient == "":
            return

        weight = self.spinWeight.value()
        calories100 = self.spinCalories100.value()
        total_calories = weight * calories100 / 100

        self.tableIngredients.setItem(row, 1, QtWidgets.QTableWidgetItem(ingredient))
        self.tableIngredients.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{weight:.0f}"))
        self.tableIngredients.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{calories100:.0f}"))
        self.tableIngredients.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total_calories:.1f}"))

        self.db.update_ingredient(self.current_id, ingredient, weight, calories100, total_calories)

        self.update_totals()

        self.lineIngredient.clear()
        self.spinWeight.setValue(0)
        self.spinCalories100.setValue(0)
        self.current_id = None

    def load_to_fields(self, row, column):
        self.current_id = int(self.tableIngredients.item(row, 0).text())
        self.lineIngredient.setText(self.tableIngredients.item(row, 1).text())
        self.spinWeight.setValue(float(self.tableIngredients.item(row, 2).text()))
        self.spinCalories100.setValue(float(self.tableIngredients.item(row, 3).text()))

    def load_ingredients(self):
        self.tableIngredients.setRowCount(0)
        ingredients = self.db.get_ingredients()
        for ingredient in ingredients:
            row = self.tableIngredients.rowCount()
            self.tableIngredients.insertRow(row)

            self.tableIngredients.setItem(row, 0, QtWidgets.QTableWidgetItem(str(ingredient[0])))
            self.tableIngredients.setItem(row, 1, QtWidgets.QTableWidgetItem(str(ingredient[1])))
            self.tableIngredients.setItem(row, 2, QtWidgets.QTableWidgetItem(str(ingredient[2])))
            self.tableIngredients.setItem(row, 3, QtWidgets.QTableWidgetItem(str(ingredient[3])))
            self.tableIngredients.setItem(row, 4, QtWidgets.QTableWidgetItem(str(ingredient[4])))

        self.update_totals()

    def load_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите фотографию", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.labelPhoto.setPixmap(pixmap.scaled(self.labelPhoto.width(),self.labelPhoto.height(),Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.settings.setValue("photo_path", file_name)

    def load_saved_photo(self):
        photo_path = self.settings.value("photo_path", "")
        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            self.labelPhoto.setPixmap(pixmap.scaled(self.labelPhoto.width(),self.labelPhoto.height(),Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def update_per_serving(self):
        people = self.spinPeople.value()
        calories = self.total_calories / people
        self.labelPerServing.setText(f"Калорий на порцию: {calories:.1f} ккал")

    def save_people(self):
        self.settings.setValue("people", self.spinPeople.value())

    def setup_icons(self):
        self.btnAdd.setIcon(QIcon("images/icons8-добавить-32.png")))
        self.btnLoadPhoto.setIcon(QIcon("images/icons8-фото-24.png"))
        self.btnEdit.setIcon(QIcon("images/icons8-редактировать-24.png"))
        self.btnDelete.setIcon(QIcon("images/icons8-мусорка-48.png"))
        self.labelPhoto.setPixmap(QPixmap("images/icons8-нет-изображения-96.png"))
        self.btnImport.setIcon(QIcon("images/icons8-сохранить-48.png"))
        self.btnExport.setIcon(QIcon("images/icons8-загрузить-48.png"))

    def apply_theme(self, theme):
        self.settings.setValue("theme", theme)
        style_file = "style_dark.qss" if theme == "dark" else "style.qss"
        try:
            with open(style_file, "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print("Ошибка")
            self.setStyleSheet("")

    def toggle_theme(self):
        current_theme = self.settings.value("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def import_data(self):
        file_path, file_tipe = QFileDialog.getSaveFileName(self, "Экспорт данных", "", "CSV файлы(*.csv);;JSON файлы(*.json)")
        if not file_path:
            return
        try:
            if file_path.endswith('.csv'):
                count = self.db.export_to_csv(file_path)
            elif file_path.endswith('.json'):
                count = self.db.export_to_json(file_path)
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неподдерживаемый формат файла")
                return

            QtWidgets.QMessageBox.information(self, "Успех", f"Экспортировано {count} ингредиентов в {file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")

    def export_data(self):
        file_path, file_tipe = QFileDialog.getOpenFileName(self, "Импорт данных", "", "CSV файлы(*.csv);;JSON файлы(*.json)")
        if not file_path:
            return
        reply = QtWidgets.QMessageBox.question(self, "Импорт данных", "Очистить текущие ингредиенты?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            ingredients = self.db.get_ingredients()
            for ing in ingredients:
                self.db.delete_ingredient(ing[0])
            self.tableIngredients.setRowCount(0)
        try:
            if file_path.endswith('.csv'):
                count = self.db.import_from_csv(file_path)
            elif file_path.endswith('.json'):
                count = self.db.import_from_json(file_path)
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неподдерживаемый формат файла")
                return
            self.load_ingredients()
            QtWidgets.QMessageBox.information(self, "Успех", f"Импортировано {count} ингредиентов в {file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка импорта: {str(e)}")