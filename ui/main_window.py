# ui/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QMessageBox, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QIcon, QFont, QAction

from ui.customer_form import CustomerForm
from ui.billing_form import BillingForm
from ui.customers_view import CustomersView
from ui.bills_view import BillsView
from database import Database

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize database
        self.db = Database()
        self.db.initialize_database()
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Billing Application")
        self.resize(1024, 768)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create sidebar for navigation
        sidebar = QFrame()
        sidebar.setMaximumWidth(200)
        sidebar.setMinimumWidth(200)
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # App title
        app_title = QLabel("Billing App")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setFont(QFont("Arial", 14, QFont.Bold))
        app_title.setContentsMargins(0, 20, 0, 30)
        
        # Navigation buttons
        self.btn_customers = QPushButton("Customers")
        self.btn_customers.setMinimumHeight(40)
        self.btn_new_customer = QPushButton("New Customer")
        self.btn_new_customer.setMinimumHeight(40)
        
        self.btn_bills = QPushButton("Bills")
        self.btn_bills.setMinimumHeight(40)
        self.btn_new_bill = QPushButton("New Bill")
        self.btn_new_bill.setMinimumHeight(40)
        
        # Add navigation buttons to sidebar
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addWidget(QLabel("Customers"))
        sidebar_layout.addWidget(self.btn_customers)
        sidebar_layout.addWidget(self.btn_new_customer)
        sidebar_layout.addSpacing(20)
        sidebar_layout.addWidget(QLabel("Bills"))
        sidebar_layout.addWidget(self.btn_bills)
        sidebar_layout.addWidget(self.btn_new_bill)
        sidebar_layout.addStretch()
        
        # Create stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.customers_view = CustomersView()
        self.bills_view = BillsView()
        self.customer_form = CustomerForm()
        self.billing_form = BillingForm()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.customers_view)
        self.stacked_widget.addWidget(self.bills_view)
        self.stacked_widget.addWidget(self.customer_form)
        self.stacked_widget.addWidget(self.billing_form)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)
        
        # Connect signals/slots
        self.btn_customers.clicked.connect(self.show_customers)
        self.btn_new_customer.clicked.connect(self.new_customer)
        self.btn_bills.clicked.connect(self.show_bills)
        self.btn_new_bill.clicked.connect(self.new_bill)
        
        self.customers_view.edit_customer_signal.connect(self.edit_customer)
        self.bills_view.edit_bill_signal.connect(self.edit_bill)
        
        # Show customers by default
        self.show_customers()
    
    @Slot()
    def show_customers(self):
        """Show customers view"""
        self.customers_view.refresh()
        self.stacked_widget.setCurrentWidget(self.customers_view)
    
    @Slot()
    def new_customer(self):
        """Create new customer"""
        self.customer_form.clear()
        self.customer_form.saved.connect(self.show_customers)
        self.stacked_widget.setCurrentWidget(self.customer_form)
    
    @Slot(int)
    def edit_customer(self, customer_id):
        """Edit existing customer"""
        self.customer_form.load(customer_id)
        self.customer_form.saved.connect(self.show_customers)
        self.stacked_widget.setCurrentWidget(self.customer_form)
    
    @Slot()
    def show_bills(self):
        """Show bills view"""
        self.bills_view.refresh()
        self.stacked_widget.setCurrentWidget(self.bills_view)
    
    @Slot()
    def new_bill(self):
        """Create new bill"""
        self.billing_form.clear()
        self.billing_form.saved.connect(self.show_bills)
        self.stacked_widget.setCurrentWidget(self.billing_form)
    
    @Slot(int)
    def edit_bill(self, bill_id):
        """Edit existing bill"""
        self.billing_form.load(bill_id)
        self.billing_form.saved.connect(self.show_bills)
        self.stacked_widget.setCurrentWidget(self.billing_form)