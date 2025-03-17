# database.py
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

class Database:
    """Database connection and operations class"""
    
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.connect()
        
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',         # Replace with your MySQL username
                password='9899', # Replace with your MySQL password
                database='billing_app'
            )
            
            if self.connection.is_connected():
                logging.info("Connected to MySQL database")
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("MySQL connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query with no return value"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            logging.error(f"Error executing query: {e}")
            return False
    
    def fetch_all(self, query, params=None):
        """Execute a query and return all results"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            logging.error(f"Error fetching data: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        """Execute a query and return one result"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            logging.error(f"Error fetching data: {e}")
            return None
    
    def insert(self, query, params=None):
        """Insert a record and return the last inserted ID"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            logging.error(f"Error inserting data: {e}")
            return None
    
    def initialize_database(self):
        """Initialize database with schema if not exists"""
        try:
            # Read schema file
            with open('schema.sql', 'r') as f:
                sql_commands = f.read()
            
            # Execute each command
            cursor = self.connection.cursor()
            for command in sql_commands.split(';'):
                if command.strip():
                    cursor.execute(command + ';')
            
            self.connection.commit()
            cursor.close()
            logging.info("Database initialized successfully")
            return True
        except Error as e:
            logging.error(f"Error initializing database: {e}")
            return False
        except FileNotFoundError:
            logging.error("Schema file not found")
            return False