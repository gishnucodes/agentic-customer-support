import sqlite3
import os
from config import Config as cfg

def create_tables(conn):
    """
    Creates the necessary tables in the SQLite database.
    """
    c = conn.cursor()

    c.execute('''
        CREATE TABLE Inventory (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            product_type TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE Customer (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone_number TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE Sales (
            sale_id INTEGER PRIMARY KEY,
            product_id INTEGER,
            customer_id INTEGER,
            quantity INTEGER NOT NULL,
            sale_date DATE,
            FOREIGN KEY(product_id) REFERENCES Inventory(product_id),
            FOREIGN KEY(customer_id) REFERENCES Customer(customer_id)
        )
    ''')

    c.execute('''
        CREATE TABLE Interaction (
            interaction_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            interaction_date DATE,
            interaction_type TEXT,
            notes TEXT,
            FOREIGN KEY(customer_id) REFERENCES Customer(customer_id)
        )
    ''')

    c.execute('''
        CREATE TABLE Complaint (
            complaint_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            complaint_date DATE,
            description TEXT,
            status TEXT,
            resolution TEXT,
            FOREIGN KEY(customer_id) REFERENCES Customer(customer_id),
            FOREIGN KEY(product_id) REFERENCES Inventory(product_id)
        )
    ''')

    conn.commit()


def insert_data(conn):
    """
    Inserts dummy data into the created tables.
    """
    c = conn.cursor()

    # Inventory
    c.executemany('''
        INSERT INTO Inventory (product_id, product_name, product_type, quantity)
        VALUES (?, ?, ?, ?)
    ''', [
        (1, 'Laptop', 'Electronics', 10),
        (2, 'Mouse', 'Electronics', 50),
        (3, 'Keyboard', 'Electronics', 40),
        (4, 'T-Shirt', 'Clothing', 100),
        (5, 'Jeans', 'Clothing', 80),
        (6, 'Book', 'Books', 200)
    ])

    # Customer
    c.executemany('''
        INSERT INTO Customer (customer_id, first_name, last_name, email, phone_number)
        VALUES (?, ?, ?, ?, ?)
    ''', [
        (1, 'John', 'Doe', 'john.doe@example.com', '555-1234'),
        (2, 'Jane', 'Smith', 'jane.smith@example.com', '555-5678'),
        (3, 'David', 'Lee', 'david.lee@example.com', '555-9012'),
        (4, 'Sarah', 'Jones', 'sarah.jones@example.com', '555-3456')
    ])

    # Sales
    c.executemany('''
        INSERT INTO Sales (sale_id, product_id, customer_id, quantity, sale_date)
        VALUES (?, ?, ?, ?, ?)
    ''', [
        (1, 1, 1, 1, '2024-11-20'),
        (2, 2, 1, 1, '2024-11-20'),
        (3, 4, 2, 2, '2024-11-22'),
        (4, 6, 3, 3, '2024-11-25'),
        (5, 1, 4, 1, '2024-11-28')
    ])

    # Interaction
    c.executemany('''
        INSERT INTO Interaction (interaction_id, customer_id, interaction_date, interaction_type, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', [
        (1, 1, '2024-11-21', 'Call', 'Inquired about shipping'),
        (2, 2, '2024-11-23', 'Email', 'Order confirmation'),
        (3, 3, '2024-11-26', 'Chat', 'Product inquiry')
    ])

    # Complaint
    c.executemany('''
        INSERT INTO Complaint (complaint_id, customer_id, product_id, complaint_date, description, status, resolution)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        (1, 2, 4, '2024-11-24', 'T-shirt size too small', 'Resolved', 'Replacement shipped'),
        (2, 4, 1, '2024-11-29', 'Laptop not working properly', 'Open', 'Awaiting return')
    ])

    conn.commit()




def populate_DB():
    # path = cfg.DB_PATH
    path = '../data/mydatabase.db'
    if not os.path.isfile(path):
        conn = sqlite3.connect(path)
        create_tables(conn)
        insert_data(conn)
        print("Data loaded successfully!")
        return 1
    return 2

if __name__ == "__main__":
    populate_DB()