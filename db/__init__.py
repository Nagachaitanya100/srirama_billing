from db.connection import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # ---------- COMPANY ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS company (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        address TEXT
    )
    """)

    # ---------- CUSTOMERS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------- ITEMS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        unit TEXT,
        rate REAL,
        hamali_rate REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------- ESTIMATES ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS estimates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estimate_no TEXT UNIQUE,
        date TEXT,
        customer_id INTEGER,
        items_total REAL,
        hamali_total REAL,
        auto_charge REAL,
        discount REAL,
        grand_total REAL,
        pdf_path TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------- ESTIMATE ITEMS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS estimate_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estimate_id INTEGER,
        item_name TEXT,
        description TEXT,
        qty INTEGER,
        unit TEXT,
        rate REAL,
        row_total REAL,
        hamali_rate REAL,
        hamali_total REAL
    )
    """)

    conn.commit()
    conn.close()
