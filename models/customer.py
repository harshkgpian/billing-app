# models/customer.py
from database import Database

class Customer:
    """Customer model class"""
    
    def __init__(self, id=None, name="", email="", phone="", address="", created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.created_at = created_at
        self.db = Database()
    
    def save(self):
        """Save customer to database"""
        if self.id is None:
            # Insert new customer
            query = """
                INSERT INTO customers (name, email, phone, address)
                VALUES (%s, %s, %s, %s)
            """
            params = (self.name, self.email, self.phone, self.address)
            self.id = self.db.insert(query, params)
            return self.id is not None
        else:
            # Update existing customer
            query = """
                UPDATE customers
                SET name = %s, email = %s, phone = %s, address = %s
                WHERE id = %s
            """
            params = (self.name, self.email, self.phone, self.address, self.id)
            return self.db.execute_query(query, params)
    
    def delete(self):
        """Delete customer from database"""
        if self.id is None:
            return False
            
        query = "DELETE FROM customers WHERE id = %s"
        return self.db.execute_query(query, (self.id,))
    
    def load(self, id):
        """Load customer data from database by ID"""
        query = "SELECT * FROM customers WHERE id = %s"
        data = self.db.fetch_one(query, (id,))
        
        if data:
            self.id = data['id']
            self.name = data['name']
            self.email = data['email']
            self.phone = data['phone']
            self.address = data['address']
            self.created_at = data['created_at']
            return True
        return False
    
    @staticmethod
    def get_all():
        """Get all customers from database"""
        db = Database()
        query = "SELECT * FROM customers ORDER BY name"
        return db.fetch_all(query)
    
    @staticmethod
    def search(term):
        """Search customers by name, email or phone"""
        db = Database()
        query = """
            SELECT * FROM customers
            WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
            ORDER BY name
        """
        search_term = f"%{term}%"
        params = (search_term, search_term, search_term)
        return db.fetch_all(query, params)
    
    @staticmethod
    def get_by_id(id):
        """Get customer by ID"""
        customer = Customer()
        customer.load(id)
        return customer if customer.id else None