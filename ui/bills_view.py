# ui/bills_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QCursor
from models.bill import Bill
import locale

# Set locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

class BillsView(QWidget):
    """View to display and manage bills"""
    
    # Signal to edit a bill
    edit_bill_signal = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Bills")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search bills...")
        self.btn_search = QPushButton("Search")
        self.btn_refresh = QPushButton("Refresh")
        
        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(search_layout)
        
        # Bills table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Bill #", "Customer", "Date", "Due Date", "Total", "Status"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Connect signals
        self.btn_search.clicked.connect(self.search_bills)
        self.btn_refresh.clicked.connect(self.refresh)
        self.txt_search.returnPressed.connect(self.search_bills)
        self.table.cellDoubleClicked.connect(self.on_row_double_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Load bills
        self.refresh()
    
    def refresh(self):
        """Refresh bills table"""
        self.load_bills(Bill.get_all())
    
    def search_bills(self):
        """Search bills"""
        search_term = self.txt_search.text().strip()
        if search_term:
            results = Bill.search(search_term)
            self.load_bills(results)
        else:
            self.refresh()
    
    def load_bills(self, bills):
        """Load bills into table"""
        self.table.setRowCount(0)
        
        for row, bill in enumerate(bills):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(bill['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(bill['bill_number']))
            self.table.setItem(row, 2, QTableWidgetItem(bill['customer_name']))
            self.table.setItem(row, 3, QTableWidgetItem(str(bill['bill_date'])))
            self.table.setItem(row, 4, QTableWidgetItem(str(bill['due_date'])))
            self.table.setItem(row, 5, QTableWidgetItem(f"{float(bill['grand_total']):.2f}"))
            
            status_item = QTableWidgetItem(bill['status'])
            if bill['status'] == 'PAID':
                status_item.setBackground(Qt.green)
            elif bill['status'] == 'OVERDUE':
                status_item.setBackground(Qt.red)
            else:  # PENDING
                status_item.setBackground(Qt.yellow)
            
            self.table.setItem(row, 6, status_item)
    
    def on_row_double_clicked(self, row, column):
        """Handle row double click"""
        bill_id = int(self.table.item(row, 0).text())
        self.edit_bill_signal.emit(bill_id)
    
    def show_context_menu(self, position):
        """Show context menu"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        bill_id = int(self.table.item(row, 0).text())
        
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec_(self.table.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_bill_signal.emit(bill_id)
        elif action == delete_action:
            self.delete_bill(bill_id)
    
    def delete_bill(self, bill_id):
        """Delete a bill"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this bill?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            bill = Bill.get_by_id(bill_id)
            if bill and bill.delete():
                QMessageBox.information(self, "Success", "Bill deleted successfully.")
                self.refresh()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete bill.")