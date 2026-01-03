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
def get_item(name):
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        """
        SELECT
            name,
            description,
            unit,
            rate,
            hamali_rate
        FROM items
        WHERE name = ?
        """,
        (name,)
    ).fetchone()

    conn.close()

    if not row:
        return None

    return {
        "name": row["name"],
        "description": row["description"] or "",
        "unit": row["unit"] or "",
        "rate": float(row["rate"] or 0),
        "hamali_rate": float(row["hamali_rate"] or 0)
    }


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

def add_or_update_item(name, description, unit, rate, hamali_rate):
    conn = get_connection()
    cur = conn.cursor()

    existing = cur.execute(
        "SELECT id FROM items WHERE name = ?",
        (name,)
    ).fetchone()

    if existing:
        cur.execute("""
            UPDATE items
            SET description=?, unit=?, rate=?, hamali_rate=?
            WHERE name=?
        """, (description, unit, rate, hamali_rate, name))
    else:
        cur.execute("""
            INSERT INTO items (name, description, unit, rate, hamali_rate)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, unit, rate, hamali_rate))

    conn.commit()
    conn.close()
