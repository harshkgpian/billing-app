# ui/billing_form.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QMessageBox, QComboBox,
    QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, Slot, QDate
from models.bill import Bill
from models.customer import Customer
import locale

# Set locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

class BillingForm(QWidget):
    """Form for creating and editing bills"""
    
    # Signal emitted when bill is saved
    saved = Signal()
    
    def __init__(self):
        super().__init__()
        self.bill = None
        self.setup_ui()
        self.showEvent = self.refresh_customers_on_show 
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Form title
        title = QLabel("Billing Information")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Main form layout
        main_form_layout = QHBoxLayout()
        
        # Left form
        left_form = QFormLayout()
        left_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Bill number
        self.txt_bill_number = QLineEdit()
        self.txt_bill_number.setReadOnly(True)
        left_form.addRow("Bill Number:", self.txt_bill_number)
        
        # Customer selector
        self.cmb_customer = QComboBox()
        self.load_customers()
        left_form.addRow("Customer:", self.cmb_customer)
        
        # Date fields
        self.date_bill = QDateEdit()
        self.date_bill.setCalendarPopup(True)
        self.date_bill.setDate(QDate.currentDate())
        
        self.date_due = QDateEdit()
        self.date_due.setCalendarPopup(True)
        self.date_due.setDate(QDate.currentDate().addDays(30))
        
        left_form.addRow("Bill Date:", self.date_bill)
        left_form.addRow("Due Date:", self.date_due)
        
        # Right form
        right_form = QFormLayout()
        right_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Status
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["PENDING", "PAID", "OVERDUE"])
        right_form.addRow("Status:", self.cmb_status)
        
        # Totals
        self.lbl_total = QLabel("0.00")
        self.lbl_tax = QLabel("0.00")
        self.lbl_grand_total = QLabel("0.00")
        
        self.lbl_total.setStyleSheet("font-weight: bold;")
        self.lbl_tax.setStyleSheet("font-weight: bold;")
        self.lbl_grand_total.setStyleSheet("font-weight: bold;")
        
        right_form.addRow("Total:", self.lbl_total)
        right_form.addRow("Tax (10%):", self.lbl_tax)
        right_form.addRow("Grand Total:", self.lbl_grand_total)
        
        # Add forms to main layout
        main_form_layout.addLayout(left_form)
        main_form_layout.addLayout(right_form)
        
        layout.addLayout(main_form_layout)
        
        # Line items section
        items_layout = QVBoxLayout()
        items_label = QLabel("Bill Items")
        items_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        items_layout.addWidget(items_label)
        
        # Line items table
        self.table_items = QTableWidget()
        self.table_items.setColumnCount(5)
        self.table_items.setHorizontalHeaderLabels(["Description", "Quantity", "Unit Price", "Amount", ""])
        self.table_items.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_items.verticalHeader().setVisible(False)
        self.table_items.setSelectionBehavior(QTableWidget.SelectRows)
        
        header = self.table_items.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        items_layout.addWidget(self.table_items)
        
        # Add item section
        add_item_layout = QHBoxLayout()
        self.txt_description = QLineEdit()
        self.txt_description.setPlaceholderText("Description")
        
        self.txt_quantity = QLineEdit()
        self.txt_quantity.setPlaceholderText("Quantity")
        self.txt_quantity.setMaximumWidth(100)
        
        self.txt_unit_price = QLineEdit()
        self.txt_unit_price.setPlaceholderText("Unit Price")
        self.txt_unit_price.setMaximumWidth(100)
        
        self.btn_add_item = QPushButton("Add Item")
        
        add_item_layout.addWidget(self.txt_description)
        add_item_layout.addWidget(self.txt_quantity)
        add_item_layout.addWidget(self.txt_unit_price)
        add_item_layout.addWidget(self.btn_add_item)
        
        items_layout.addLayout(add_item_layout)
        layout.addLayout(items_layout)
        
        # Notes
        notes_layout = QVBoxLayout()
        notes_label = QLabel("Notes")
        self.txt_notes = QTextEdit()
        self.txt_notes.setMaximumHeight(100)
        
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.txt_notes)
        
        layout.addLayout(notes_layout)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Bill")
        self.btn_cancel = QPushButton("Cancel")
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Connect signals
        self.btn_save.clicked.connect(self.save_bill)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_add_item.clicked.connect(self.add_item)
    
    def load_customers(self):
        """Load customers into combo box"""
        self.cmb_customer.clear()
        customers = Customer.get_all()
        
        for customer in customers:
            # Store customer ID as user data
            self.cmb_customer.addItem(customer['name'], customer['id'])


    def refresh_customers_on_show(self, event):
        """Ensure the customer list is refreshed when the form is displayed"""
        self.load_customers()
        super().showEvent(event)

    
    def clear(self):
        """Clear the form"""
        self.bill = Bill()
        self.txt_bill_number.setText(self.bill.bill_number)
        self.date_bill.setDate(QDate.currentDate())
        self.date_due.setDate(QDate.currentDate().addDays(30))
        self.cmb_status.setCurrentText("PENDING")
        self.txt_notes.clear()
        self.clear_items_table()
        self.update_totals()
    
    def load(self, bill_id):
        """Load bill data into form"""
        self.bill = Bill.get_by_id(bill_id)
        if self.bill:
            self.txt_bill_number.setText(self.bill.bill_number)
            
            # Set customer
            index = self.cmb_customer.findData(self.bill.customer_id)
            if index >= 0:
                self.cmb_customer.setCurrentIndex(index)
            
            # Set dates
            self.date_bill.setDate(QDate.fromString(str(self.bill.bill_date), "yyyy-MM-dd"))
            self.date_due.setDate(QDate.fromString(str(self.bill.due_date), "yyyy-MM-dd"))
            
            # Set status
            self.cmb_status.setCurrentText(self.bill.status)
            
            # Set notes
            self.txt_notes.setText(self.bill.notes)
            
            # Load items
            self.load_items()
            
            # Update totals
            self.update_totals()
    
    def clear_items_table(self):
        """Clear items table"""
        self.table_items.setRowCount(0)
        if self.bill:
            self.bill.items.clear()
    
    def load_items(self):
        """Load bill items into table"""
        self.table_items.setRowCount(0)
        
        for index, item in enumerate(self.bill.items):
            self.table_items.insertRow(index)
            
            self.table_items.setItem(index, 0, QTableWidgetItem(item.description))
            self.table_items.setItem(index, 1, QTableWidgetItem(str(item.quantity)))
            self.table_items.setItem(index, 2, QTableWidgetItem(f"{item.unit_price:.2f}"))
            self.table_items.setItem(index, 3, QTableWidgetItem(f"{item.amount:.2f}"))
            
            # Delete button
            btn_delete = QPushButton("Delete")
            btn_delete.clicked.connect(lambda checked, row=index: self.delete_item(row))
            self.table_items.setCellWidget(index, 4, btn_delete)
    
    def update_totals(self):
        """Update totals display"""
        if self.bill:
            self.lbl_total.setText(f"{self.bill.total_amount:.2f}")
            self.lbl_tax.setText(f"{self.bill.tax_amount:.2f}")
            self.lbl_grand_total.setText(f"{self.bill.grand_total:.2f}")
    
# ui/billing_form.py (continued)
    def add_item(self):
        """Add item to bill"""
        description = self.txt_description.text().strip()
        quantity_text = self.txt_quantity.text().strip()
        unit_price_text = self.txt_unit_price.text().strip()
        
        if not description:
            QMessageBox.warning(self, "Warning", "Please enter a description.")
            self.txt_description.setFocus()
            return
        
        try:
            quantity = float(quantity_text)
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter a valid quantity.")
            self.txt_quantity.setFocus()
            return
        
        try:
            unit_price = float(unit_price_text)
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter a valid unit price.")
            self.txt_unit_price.setFocus()
            return
        
        # Add item to bill
        item = self.bill.add_item(description, quantity, unit_price)
        
        # Add item to table
        row = self.table_items.rowCount()
        self.table_items.insertRow(row)
        
        self.table_items.setItem(row, 0, QTableWidgetItem(item.description))
        self.table_items.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
        self.table_items.setItem(row, 2, QTableWidgetItem(f"{item.unit_price:.2f}"))
        self.table_items.setItem(row, 3, QTableWidgetItem(f"{item.amount:.2f}"))
        
        # Delete button
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(lambda checked, r=row: self.delete_item(r))
        self.table_items.setCellWidget(row, 4, btn_delete)
        
        # Clear inputs
        self.txt_description.clear()
        self.txt_quantity.clear()
        self.txt_unit_price.clear()
        self.txt_description.setFocus()
        
        # Update totals
        self.update_totals()
    
    def delete_item(self, row):
        """Delete item from bill"""
        if 0 <= row < len(self.bill.items):
            self.bill.remove_item(row)
            self.load_items()  # Reload all items
            self.update_totals()
    
    def save_bill(self):
        """Save bill data"""
        if not self.validate():
            return
        
        if not self.bill:
            self.bill = Bill()
        
        # Update bill data
        customer_index = self.cmb_customer.currentIndex()
        if customer_index >= 0:
            self.bill.customer_id = self.cmb_customer.itemData(customer_index)
        
        self.bill.bill_date = self.date_bill.date().toString("yyyy-MM-dd")
        self.bill.due_date = self.date_due.date().toString("yyyy-MM-dd")
        self.bill.status = self.cmb_status.currentText()
        self.bill.notes = self.txt_notes.toPlainText()
        
        # Save to database
        if self.bill.save():
            QMessageBox.information(self, "Success", "Bill saved successfully.")
            self.saved.emit()
        else:
            QMessageBox.critical(self, "Error", "Failed to save bill.")
    
    def validate(self):
        """Validate form data"""
        if self.cmb_customer.currentIndex() < 0:
            QMessageBox.warning(self, "Warning", "Please select a customer.")
            return False
        
        if not self.bill.items:
            QMessageBox.warning(self, "Warning", "Please add at least one item to the bill.")
            return False
        
        return True
    
    def cancel(self):
        """Cancel form"""
        self.saved.emit()