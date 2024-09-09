import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox, QHBoxLayout, QFileDialog #type:ignore
import sqlite3
import csv

class ElectricShopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SHREE UMIYA SWITCHGEAR STOCK MONITORING')
        self.setGeometry(100, 100, 800, 600)
        self.page = 1
        self.page_size = 100

        # Initialize database and create table
        self.init_db()

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by product name...")
        self.search_bar.textChanged.connect(self.search_products)
        self.layout.addWidget(self.search_bar)

        # Table to show stock
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(5)
        self.stock_table.setHorizontalHeaderLabels(['Product Name','Unit','Stock Count','Unit Price','Total Price'])
        self.layout.addWidget(self.stock_table)

        # Forms for updating, selling, and adding products
        self.create_forms()

        # Initial refresh to load data
        self.refresh_stock()

    def init_db(self):
        conn = sqlite3.connect('stock_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                unit TEXT NOT NULL,
                stock INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def create_forms(self):
        # Form layout
        self.form_layout = QFormLayout()

        # Sell product form
        self.sell_name_input = QLineEdit()
        self.sell_quantity_input = QLineEdit()
        self.form_layout.addRow('Sell Product Name:', self.sell_name_input)
        self.form_layout.addRow('Quantity:', self.sell_quantity_input)
        self.sell_button = QPushButton('Sell Product')
        self.sell_button.clicked.connect(self.sell_product)
        self.form_layout.addRow(self.sell_button)

        # Add new product form
        self.add_name_input = QLineEdit()
        self.add_unit_input = QLineEdit()
        self.add_stock_input = QLineEdit()
        self.add_unit_price = QLineEdit()
        self.form_layout.addRow('New Product Name:', self.add_name_input)
        self.form_layout.addRow('Initial Unit:', self.add_unit_input)
        self.form_layout.addRow('Initial Stock:', self.add_stock_input)
        self.form_layout.addRow('Unit Price:', self.add_unit_price)
        self.add_button = QPushButton('Add New Product')
        self.add_button.clicked.connect(self.add_product)
        self.form_layout.addRow(self.add_button)

        # Update product form
        self.update_name_input = QLineEdit()
        self.update_unit_input = QLineEdit()
        self.update_stock_input = QLineEdit()
        self.update_price_input = QLineEdit()
        self.form_layout.addRow('Product Name:', self.update_name_input)
        self.form_layout.addRow('New Unit:', self.update_unit_input)
        self.form_layout.addRow('New Stock:', self.update_stock_input)
        self.form_layout.addRow('New Unit Price:', self.update_price_input)
        self.update_button = QPushButton('Update Product')
        self.update_button.clicked.connect(self.update_product)
        self.form_layout.addRow(self.update_button)

        # Delete Data Form
        self.delete_name_input = QLineEdit()
        self.form_layout.addRow('Delete Product Name:', self.delete_name_input)
        self.delete_button = QPushButton('Delete Product')
        self.delete_button.clicked.connect(self.delete_data)
        self.form_layout.addRow(self.delete_button)

        # CSV Upload Form
        self.csv_upload_button = QPushButton('Upload CSV')
        self.csv_upload_button.clicked.connect(self.upload_csv)
        self.form_layout.addRow(self.csv_upload_button)

        self.layout.addLayout(self.form_layout)

    def upload_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if not file_name:
            return

        conn = sqlite3.connect('stock_database.db')
        cursor = conn.cursor()

        try:
            with open(file_name, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row if present
                for row in reader:
                    if len(row) < 4:
                        continue
                    name,unit, stock, unit_price = row
                    try:
                        unit_price = float(unit_price.replace(',','').strip())
                        unit=str(unit)
                        stock = int(float(str(stock).replace(',','').strip()))
                        total_price=round(unit_price*stock,4)
                        cursor.execute("SELECT stock FROM products WHERE name = ?", (name,))
                        existing_product = cursor.fetchone()
                        if existing_product:
                            cursor.execute("UPDATE products SET total_price= ?,unit_price = ?, stock = stock + ?,unit = ? WHERE name = ?", (total_price,unit_price, stock, unit, name))
                        else:
                            cursor.execute("INSERT INTO products (name, unit, stock, unit_price,total_price) VALUES (?, ?, ?, ?, ?)", (name, unit, stock, unit_price, total_price))
                    except ValueError as v:
                        print(v)
                        continue  # Skip invalid rows
            QMessageBox.information(self, "Success", "CSV data uploaded successfully.")
        except ValueError as v:
            QMessageBox.warning(self, "Error", "Please proper formate CSV Files or Data !!!")
        finally:
            conn.commit()
            conn.close()
            self.refresh_stock()
        

    def delete_data(self):
        name = self.delete_name_input.text()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a product name to delete.")
            return

        conn = sqlite3.connect('stock_database.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE name = ?", (name,))
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            QMessageBox.warning(self, "Delete Error", "Product not found.")
        else:
            QMessageBox.information(self, "Success", "Product deleted successfully.")
            self.refresh_stock()

    def refresh_stock(self):
        conn = sqlite3.connect('stock_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, unit, stock, unit_price, total_price FROM products")
        products = cursor.fetchall()
        conn.close()

        self.stock_table.setRowCount(len(products))
        for i, product in enumerate(products):
            self.stock_table.setItem(i, 0, QTableWidgetItem(product[0]))
            self.stock_table.setItem(i, 1, QTableWidgetItem(product[1]))
            self.stock_table.setItem(i, 2, QTableWidgetItem(str(product[2])))
            self.stock_table.setItem(i, 3, QTableWidgetItem(f"{product[3]:.2f}"))
            self.stock_table.setItem(i, 4, QTableWidgetItem(f"{product[4]}"))

    def update_product(self):
        name = self.update_name_input.text()
        new_unit = self.update_unit_input.text()
        new_stock = self.update_stock_input.text()
        new_unit_price = self.update_price_input.text()

        if not name or not new_unit_price or not new_stock or not new_unit:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields to update the product.")
            return

        try:
            new_unit=str(new_unit)
            new_stock = int(new_stock)
            new_unit_price = float(new_unit_price)
            total_price=round(new_unit_price*new_stock,4)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Price must be a number and stock must be an integer.")
            return

        conn = sqlite3.connect('stock_database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET total_price= ?, unit_price = ?, stock = ?, unit= ? WHERE name = ?", (total_price,new_unit_price, new_stock, new_unit, name))
        conn.commit()

        if cursor.rowcount == 0:
            QMessageBox.warning(self, "Update Error", "Product not found.")
        else:
            QMessageBox.information(self, "Success", "Product updated successfully.")
            self.refresh_stock()

        conn.close()

    def sell_product(self):
        name = self.sell_name_input.text().strip()
        quantity = self.sell_quantity_input.text().strip()

        if not name or not quantity:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields to sell the product.")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Quantity must be an integer.")
            return

        conn = sqlite3.connect('stock_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT stock,unit_price FROM products WHERE name = ?", (name,))
        result = cursor.fetchone()

        if not result:
            QMessageBox.warning(self, "Error", "Product not found.")
        elif result[0] < quantity:
            QMessageBox.warning(self, "Error", "Insufficient stock.")
        else:
            new_stock = result[0] - quantity
            if new_stock < 0:
                QMessageBox.warning(self, "Error", "*Product stock not updated properly*")
            else:
                total_price=round(result[1]*new_stock,4)
                cursor.execute("UPDATE products SET total_price= ? ,stock = ? WHERE name = ?", (total_price,new_stock, name))

            conn.commit()
            QMessageBox.information(self, "Success", "Product sold successfully.")
            self.refresh_stock()

        conn.close()

    def add_product(self):
        name = self.add_name_input.text().strip()
        unit = self.add_unit_input.text().strip()
        stock = self.add_stock_input.text().strip()
        unit_price = self.add_unit_price.text().strip()

        if not name or not unit_price or not stock:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields to add the product.")
            return

        try:
            unit_price = float(unit_price)
            stock = int(stock)
            if unit_price < 0 or stock < 0:
                unit_price=stock=0
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Price must be a number and stock must be an integer.")
            return

        conn = sqlite3.connect('stock_database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT stock FROM products WHERE name = ?", (name,))
        existing_product = cursor.fetchone()

        if existing_product:
            QMessageBox.warning(self, "Product Exists", "This product is already available in the inventory. If needed, please update the stock and price.")
        else:
            total_price=round(unit_price*stock,4)
            cursor.execute("INSERT INTO products (name, unit, stock, unit_price,total_price) VALUES (?, ?, ?, ?, ?)", (name, unit, stock, unit_price,total_price))
            QMessageBox.information(self, "Success", "Product added successfully.")

        conn.commit()
        conn.close()

        self.refresh_stock()
    
    def search_products(self):
        search_term = self.search_bar.text().strip()
        conn = sqlite3.connect('stock_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, unit, stock, unit_price,total_price FROM products WHERE name LIKE ?", ('%' + search_term + '%',))
        products = cursor.fetchall()
        conn.close()

        self.stock_table.setRowCount(len(products))
        for i, product in enumerate(products):
            # self.stock_table.setItem(i, 0, QTableWidgetItem(product[0]))
            # self.stock_table.setItem(i, 1, QTableWidgetItem(f"{product[1]:.2f}"))
            # self.stock_table.setItem(i, 2, QTableWidgetItem(str(product[2])))
            self.stock_table.setItem(i, 0, QTableWidgetItem(product[0]))
            self.stock_table.setItem(i, 1, QTableWidgetItem(product[1]))
            self.stock_table.setItem(i, 2, QTableWidgetItem(str(product[2])))
            self.stock_table.setItem(i, 3, QTableWidgetItem(f"{product[3]:.2f}"))
            self.stock_table.setItem(i, 4, QTableWidgetItem(f"{product[4]}"))
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = ElectricShopApp()
    mainWin.show()
    sys.exit(app.exec_())
