import sqlite3 
from db.connection import get_connection


def get_customer_names():
    conn = get_connection()
    rows = conn.execute(
        "SELECT name FROM customers ORDER BY name"
    ).fetchall()
    conn.close()
    return [row["name"] for row in rows]


def get_customer(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM customers WHERE name = ?",
        (name,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def customer_exists(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM customers WHERE name = ?",
        (name,)
    ).fetchone()
    conn.close()
    return row is not None

def add_customer(name, phone, address):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO customers (name, phone, address)
        VALUES (?, ?, ?)
        """,
        (name, phone, address)
    )
    conn.commit()
    conn.close()

def get_all_customers():
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT id, name, phone, address
        FROM customers
        ORDER BY name
    """).fetchall()

    conn.close()
    return [dict(row) for row in rows]


def get_customer_id(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM customers WHERE name = ?",
        (name,)
    ).fetchone()
    conn.close()
    return row["id"] if row else None

def get_customer_by_id(customer_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    row = conn.execute("""
        SELECT id, name, phone, address
        FROM customers
        WHERE id = ?
    """, (customer_id,)).fetchone()

    conn.close()
    return dict(row) if row else None 

def update_customer(customer_id, name, phone, address):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE customers SET
            name = ?,
            phone = ?,
            address = ?
        WHERE id = ?
    """, (name, phone, address, customer_id))

    conn.commit()
    conn.close() 

def delete_customer(customer_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM customers WHERE id = ?",
        (customer_id,)
    )

    conn.commit()
    conn.close()