# Billing Application

A desktop billing application built with PySide6 and MySQL.

## Features

- Customer management
- Bill creation and management
- Item tracking for each bill
- Customer and bill search functionality
- Status tracking (Pending, Paid, Overdue)
- Clean and intuitive user interface

## Requirements

- Python 3.8+
- PySide6
- MySQL 5.7+
- mysql-connector-python

## Installation

1. Clone the repository:

```bash
git clone https://github.com/harshkgpian/billing-app.git
cd billing-app
```

2. Install dependencies:

```bash
pip install PySide6 mysql-connector-python
```

3. Configure database:
   - Create a MySQL database
   - Update the database connection details in `database.py`
   - The application will automatically create necessary tables on first run

## Running the Application

```bash
python main.py
```

## Project Structure

- `main.py`: Main entry point for the application
- `database.py`: Database connection and utilities
- `ui/`: UI components
  - `main_window.py`: Main window with navigation
  - `customer_form.py`: Customer management form
  - `billing_form.py`: Billing form
  - `bills_view.py`: Bills view/report
  - `customers_view.py`: Customers view/report
- `models/`: Data models
  - `customer.py`: Customer model
  - `bill.py`: Bill model
- `schema.sql`: Database schema

## License

This project is licensed under the MIT License - see the LICENSE file for details.
