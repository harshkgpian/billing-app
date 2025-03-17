# ui/customer_form.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot
from models.customer import Customer

class CustomerForm(QWidget):
    """Customer form for adding/editing customers"""
    
    # Signal emitted when customer is saved
    saved = Signal()
    
    def __init__(self):
        super().__init__()
        self.customer = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Form title
        title = QLabel("Customer Information")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Form fields
        self.txt_name = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_phone = QLineEdit()
        self.txt_address = QTextEdit()
        self.txt_address.setMaximumHeight(100)
        
        # Add fields to form
        form_layout.addRow("Name:", self.txt_name)
        form_layout.addRow("Email:", self.txt_email)
        form_layout.addRow("Phone:", self.txt_phone)
        form_layout.addRow("Address:", self.txt_address)
        
        # Add form to layout
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Connect signals
        self.btn_save.clicked.connect(self.save_customer)
        self.btn_cancel.clicked.connect(self.cancel)
    
    def clear(self):
        """Clear the form"""
        self.customer = Customer()
        self.txt_name.setText("")
        self.txt_email.setText("")
        self.txt_phone.setText("")
        self.txt_address.setText("")
    
    def load(self, customer_id):
        """Load customer data into form"""
        self.customer = Customer.get_by_id(customer_id)
        if self.customer:
            self.txt_name.setText(self.customer.name)
            self.txt_email.setText(self.customer.email)
            self.txt_phone.setText(self.customer.phone)
            self.txt_address.setText(self.customer.address)
    
    def save_customer(self):
        """Save customer data"""
        if not self.validate():
            return
        
        if not self.customer:
            self.customer = Customer()
        
        # Update customer data
        self.customer.name = self.txt_name.text()
        self.customer.email = self.txt_email.text()
        self.customer.phone = self.txt_phone.text()
        self.customer.address = self.txt_address.toPlainText()
        
        # Save to database
        if self.customer.save():
            QMessageBox.information(self, "Success", "Customer saved successfully.")
            self.saved.emit()
        else:
            QMessageBox.critical(self, "Error", "Failed to save customer.")
    
    def validate(self):
        """Validate form data"""
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter a name.")
            self.txt_name.setFocus()
            return False
        return True
    
    def cancel(self):
        """Cancel form"""
        self.saved.emit()