from db.connection import get_connection


# ---------------- GET CUSTOMER NAMES ----------------
def get_customer_names():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM customers ORDER BY name")
    rows = cur.fetchall()

    conn.close()
    return [r[0] for r in rows]


# ---------------- GET CUSTOMER BY NAME ----------------
def get_customer(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, phone, address FROM customers WHERE name = %s",
        (name,)
    )
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]

    conn.close()
    return dict(zip(columns, row)) if row else None


# ---------------- CHECK CUSTOMER EXISTS ----------------
def customer_exists(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM customers WHERE name = %s",
        (name,)
    )
    exists = cur.fetchone() is not None

    conn.close()
    return exists


# ---------------- ADD CUSTOMER ----------------
def add_customer(name, phone, address):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO customers (name, phone, address)
        VALUES (%s, %s, %s)
        ON CONFLICT (name) DO NOTHING
        """,
        (name, phone, address)
    )

    conn.commit()
    conn.close()


# ---------------- GET ALL CUSTOMERS ----------------
def get_all_customers():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, phone, address
        FROM customers
        ORDER BY name
    """)

    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    conn.close()
    return [dict(zip(columns, row)) for row in rows]


# ---------------- GET CUSTOMER ID ----------------
def get_customer_id(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM customers WHERE name = %s",
        (name,)
    )
    row = cur.fetchone()

    conn.close()
    return row[0] if row else None


# ---------------- GET CUSTOMER BY ID ----------------
def get_customer_by_id(customer_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, phone, address
        FROM customers
        WHERE id = %s
    """, (customer_id,))

    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]

    conn.close()
    return dict(zip(columns, row)) if row else None


# ---------------- UPDATE CUSTOMER ----------------
def update_customer(customer_id, name, phone, address):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE customers SET
            name = %s,
            phone = %s,
            address = %s
        WHERE id = %s
    """, (name, phone, address, customer_id))

    conn.commit()
    conn.close()


# ---------------- DELETE CUSTOMER ----------------
def delete_customer(customer_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM customers WHERE id = %s",
        (customer_id,)
    )

    conn.commit()
    conn.close()
