from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QFileDialog
from PyQt5.uic import loadUi
from database import Database
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt,QSettings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("calculator.ui", self)
        with open("style.qss", "r", encoding="utf-8") as file:
            self.setStyleSheet(file.read())

        self.setup_table()
        self.connect_signals()

        self.total_weight = 0
        self.total_calories = 0

        self.db = Database()
        self.current_id = None
        self.load_ingredients()

        self.settings = QSettings("RecipeApp", "Calculator")
        people = self.settings.value("people", 1, type=int)
        self.spinPeople.setValue(people)

        self.setup_icons()

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

    def update_per_serving(self):
        people = self.spinPeople.value()
        calories = self.total_calories / people
        self.labelPerServing.setText(f"Калорий на порцию: {calories:.1f} ккал")

    def save_people(self):
        self.settings.setValue("people", self.spinPeople.value())

    def setup_icons(self):
        self.btnAdd.setIcon(QIcon(QIcon("images/icons8-добавить-32.png")))
        self.btnLoadPhoto.setIcon(QIcon("images/icons8-фото-24.png"))
        self.btnEdit.setIcon(QIcon("images/icons8-редактировать-24.png"))
        self.btnDelete.setIcon(QIcon("images/icons8-мусорка-48.png"))
        self.labelPhoto.setPixmap(QPixmap("images/icons8-нет-изображения-96.png"))