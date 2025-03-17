# ui/customers_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QCursor
from models.customer import Customer

class CustomersView(QWidget):
    """View to display and manage customers"""
    
    # Signal to edit a customer
    edit_customer_signal = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
# ui/customers_view.py (continued)
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Customers")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search customers...")
        self.btn_search = QPushButton("Search")
        self.btn_refresh = QPushButton("Refresh")
        
        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(search_layout)
        
        # Customers table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "Address"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.table)
        
        # Connect signals
        self.btn_search.clicked.connect(self.search_customers)
        self.btn_refresh.clicked.connect(self.refresh)
        self.txt_search.returnPressed.connect(self.search_customers)
        self.table.cellDoubleClicked.connect(self.on_row_double_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Load customers
        self.refresh()
    
    def refresh(self):
        """Refresh customers table"""
        self.load_customers(Customer.get_all())
    
    def search_customers(self):
        """Search customers"""
        search_term = self.txt_search.text().strip()
        if search_term:
            results = Customer.search(search_term)
            self.load_customers(results)
        else:
            self.refresh()
    
    def load_customers(self, customers):
        """Load customers into table"""
        self.table.setRowCount(0)
        
        for row, customer in enumerate(customers):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(customer['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(customer['name']))
            self.table.setItem(row, 2, QTableWidgetItem(customer['email'] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(customer['phone'] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(customer['address'] or ""))
    
    def on_row_double_clicked(self, row, column):
        """Handle row double click"""
        customer_id = int(self.table.item(row, 0).text())
        self.edit_customer_signal.emit(customer_id)
    
    def show_context_menu(self, position):
        """Show context menu"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        customer_id = int(self.table.item(row, 0).text())
        
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec_(self.table.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_customer_signal.emit(customer_id)
        elif action == delete_action:
            self.delete_customer(customer_id)
    
    def delete_customer(self, customer_id):
        """Delete a customer"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this customer?\nThis will also delete all related bills.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            customer = Customer.get_by_id(customer_id)
            if customer and customer.delete():
                QMessageBox.information(self, "Success", "Customer deleted successfully.")
                self.refresh()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete customer.")