# models/bill.py
from database import Database
from datetime import datetime, timedelta
import uuid

class BillItem:
    """Bill item model class"""
    
    def __init__(self, id=None, bill_id=None, description="", quantity=1.0, unit_price=0.0, amount=0.0):
        self.id = id
        self.bill_id = bill_id
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.amount = amount

class Bill:
    """Bill model class"""
    
    def __init__(self, id=None, bill_number="", customer_id=None, bill_date=None, due_date=None,
                 total_amount=0.0, tax_amount=0.0, grand_total=0.0, status="PENDING", notes="", created_at=None):
        self.id = id
        self.bill_number = bill_number if bill_number else self._generate_bill_number()
        self.customer_id = customer_id
        self.bill_date = bill_date if bill_date else datetime.now().date()
        self.due_date = due_date if due_date else (datetime.now() + timedelta(days=30)).date()
        self.total_amount = total_amount
        self.tax_amount = tax_amount
        self.grand_total = grand_total
        self.status = status
        self.notes = notes
        self.created_at = created_at
        self.items = []
        self.db = Database()
    
    def _generate_bill_number(self):
        """Generate a unique bill number"""
        today = datetime.now()
        prefix = f"INV-{today.year}{today.month:02d}"
        
        # Get last bill number with this prefix
        db = Database()
        query = "SELECT MAX(bill_number) as last_bill FROM bills WHERE bill_number LIKE %s"
        result = db.fetch_one(query, (f"{prefix}%",))
        
        if result and result['last_bill']:
            # Extract the number part and increment
            try:
                last_num = int(result['last_bill'].split('-')[-1])
                return f"{prefix}-{last_num + 1:04d}"
            except:
                pass
        
        # Default to starting number
        return f"{prefix}-0001"
    
    def add_item(self, description, quantity, unit_price):
        """Add an item to the bill"""
        amount = quantity * unit_price
        item = BillItem(
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            amount=amount
        )
        self.items.append(item)
        self._recalculate_totals()
        return item
    
    def remove_item(self, index):
        """Remove an item from the bill"""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self._recalculate_totals()
            return True
        return False
    
    def _recalculate_totals(self):
        """Recalculate bill totals"""
        self.total_amount = sum(item.amount for item in self.items)
        # Assuming tax rate of 10%
        self.tax_amount = self.total_amount * 0.10
        self.grand_total = self.total_amount + self.tax_amount
    
    def save(self):
        """Save bill to database"""
        if self.id is None:
            # Insert new bill
            query = """
                INSERT INTO bills (bill_number, customer_id, bill_date, due_date,
                                    total_amount, tax_amount, grand_total, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                self.bill_number, self.customer_id, self.bill_date, self.due_date,
                self.total_amount, self.tax_amount, self.grand_total, self.status, self.notes
            )
            self.id = self.db.insert(query, params)
            
            if self.id:
                # Save bill items
                self._save_items()
                return True
            return False
        else:
            # Update existing bill
            query = """
                UPDATE bills
                SET bill_number = %s, customer_id = %s, bill_date = %s, due_date = %s,
                    total_amount = %s, tax_amount = %s, grand_total = %s, status = %s, notes = %s
                WHERE id = %s
            """
            params = (
                self.bill_number, self.customer_id, self.bill_date, self.due_date,
                self.total_amount, self.tax_amount, self.grand_total, self.status, self.notes,
                self.id
            )
            if self.db.execute_query(query, params):
                # Delete existing items and save new ones
                self._delete_items()
                self._save_items()
                return True
            return False
    
# models/bill.py (continued)
    def _save_items(self):
        """Save bill items to database"""
        for item in self.items:
            query = """
                INSERT INTO bill_items (bill_id, description, quantity, unit_price, amount)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (self.id, item.description, item.quantity, item.unit_price, item.amount)
            item_id = self.db.insert(query, params)
            if item_id:
                item.id = item_id
                item.bill_id = self.id
    
    def _delete_items(self):
        """Delete all items for this bill"""
        query = "DELETE FROM bill_items WHERE bill_id = %s"
        return self.db.execute_query(query, (self.id,))
    
    def load(self, id):
        """Load bill data from database by ID"""
        query = "SELECT * FROM bills WHERE id = %s"
        data = self.db.fetch_one(query, (id,))
        
        if data:
            self.id = data['id']
            self.bill_number = data['bill_number']
            self.customer_id = data['customer_id']
            self.bill_date = data['bill_date']
            self.due_date = data['due_date']
            self.total_amount = float(data['total_amount'])
            self.tax_amount = float(data['tax_amount'])
            self.grand_total = float(data['grand_total'])
            self.status = data['status']
            self.notes = data['notes']
            self.created_at = data['created_at']
            
            # Load bill items
            self._load_items()
            return True
        return False
    
    def _load_items(self):
        """Load bill items from database"""
        query = "SELECT * FROM bill_items WHERE bill_id = %s"
        items_data = self.db.fetch_all(query, (self.id,))
        
        self.items = []
        for item_data in items_data:
            item = BillItem(
                id=item_data['id'],
                bill_id=item_data['bill_id'],
                description=item_data['description'],
                quantity=float(item_data['quantity']),
                unit_price=float(item_data['unit_price']),
                amount=float(item_data['amount'])
            )
            self.items.append(item)
    
    def delete(self):
        """Delete bill from database"""
        if self.id is None:
            return False
            
        # Delete bill items (cascade will work, but this is clearer)
        self._delete_items()
        
        # Delete the bill
        query = "DELETE FROM bills WHERE id = %s"
        return self.db.execute_query(query, (self.id,))
    
    @staticmethod
    def get_all():
        """Get all bills from database with customer info"""
        db = Database()
        query = """
            SELECT b.*, c.name as customer_name
            FROM bills b
            JOIN customers c ON b.customer_id = c.id
            ORDER BY b.bill_date DESC
        """
        return db.fetch_all(query)
    
    @staticmethod
    def search(term):
        """Search bills by bill number or customer name"""
        db = Database()
        query = """
            SELECT b.*, c.name as customer_name
            FROM bills b
            JOIN customers c ON b.customer_id = c.id
            WHERE b.bill_number LIKE %s OR c.name LIKE %s
            ORDER BY b.bill_date DESC
        """
        search_term = f"%{term}%"
        params = (search_term, search_term)
        return db.fetch_all(query, params)
    
    @staticmethod
    def get_by_id(id):
        """Get bill by ID"""
        bill = Bill()
        bill.load(id)
        return bill if bill.id else None
    
    @staticmethod
    def get_by_customer(customer_id):
        """Get bills for a specific customer"""
        db = Database()
        query = """
            SELECT b.*, c.name as customer_name
            FROM bills b
            JOIN customers c ON b.customer_id = c.id
            WHERE b.customer_id = %s
            ORDER BY b.bill_date DESC
        """
        return db.fetch_all(query, (customer_id,))