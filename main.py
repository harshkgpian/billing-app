# main.py
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QDir
from ui.main_window import MainWindow
from database import Database

def setup_environment():
    """Setup application environment"""
    # Make sure database dir exists
    os.makedirs('data', exist_ok=True)

def main():
    """Main entry point"""
    # Setup environment
    setup_environment()
    
    # Initialize application
    app = QApplication(sys.argv)
    app.setApplicationName("Billing Application")
    app.setOrganizationName("InfooWare")
    
    # Initialize database
    db = Database()
    db.initialize_database()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()