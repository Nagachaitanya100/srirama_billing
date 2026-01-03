import sqlite3
from db.connection import get_connection


# ---------------- ADD ITEM ----------------
def add_item(name, description, unit, rate, hamali_rate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO items (name, description, unit, rate, hamali_rate)
        VALUES (?, ?, ?, ?, ?)
    """, (name, description, unit, rate, hamali_rate))

    conn.commit()
    conn.close()


# ---------------- GET ALL ITEMS ----------------
def get_all_items():
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT id, name, description, unit, rate, hamali_rate
        FROM items
        ORDER BY name
    """).fetchall()

    conn.close()
    return [dict(row) for row in rows]


# ---------------- GET ITEM BY ID ----------------
def get_item_by_id(item_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    row = conn.execute("""
        SELECT id, name, description, unit, rate, hamali_rate
        FROM items
        WHERE id = ?
    """, (item_id,)).fetchone()

    conn.close()
    return dict(row) if row else None

# ---------------- GET ITEM NAMES (FOR COMBO BOX) ----------------
def get_item_names():
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT name FROM items ORDER BY name"
    ).fetchall()

    conn.close()
    return [row[0] for row in rows]


# ---------------- GET ITEM BY NAME (FOR AUTO-FILL) ----------------
def get_item(item_name):
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        """
        SELECT
            name,
            description AS desc,
            unit,
            rate AS price,
            hamali_rate AS hamali
        FROM items
        WHERE name = ?
        """,
        (item_name,)
    ).fetchone()

    conn.close()
    return dict(row) if row else None

# ---------------- UPDATE ITEM ----------------
def update_item(item_id, name, description, unit, rate, hamali_rate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE items SET
            name = ?,
            description = ?,
            unit = ?,
            rate = ?,
            hamali_rate = ?
        WHERE id = ?
    """, (name, description, unit, rate, hamali_rate, item_id))

    conn.commit()
    conn.close()


# ---------------- DELETE ITEM ----------------
def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

