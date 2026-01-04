from db.connection import get_connection


# ---------------- ADD ITEM ----------------
def add_item(name, description, unit, rate, hamali_rate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO items (name, description, unit, rate, hamali_rate)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (name) DO NOTHING
    """, (name, description, unit, rate, hamali_rate))

    conn.commit()
    conn.close()


# ---------------- GET ALL ITEMS ----------------
def get_all_items():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, description, unit, rate, hamali_rate
        FROM items
        ORDER BY name
    """)

    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    conn.close()
    return [dict(zip(columns, row)) for row in rows]


# ---------------- GET ITEM BY ID ----------------
def get_item_by_id(item_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, description, unit, rate, hamali_rate
        FROM items
        WHERE id = %s
    """, (item_id,))

    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]

    conn.close()
    return dict(zip(columns, row)) if row else None


# ---------------- GET ITEM NAMES (FOR COMBO BOX) ----------------
def get_item_names():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM items ORDER BY name")
    rows = cur.fetchall()

    conn.close()
    return [r[0] for r in rows]


# ---------------- GET ITEM BY NAME (FOR AUTO-FILL IN ESTIMATE) ----------------
def get_item(item_name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, description, unit, rate, hamali_rate
        FROM items
        WHERE name = %s
    """, (item_name,))

    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]

    conn.close()

    if not row:
        return None

    data = dict(zip(columns, row))

    return {
        "name": data["name"],
        "description": data.get("description") or "",
        "unit": data.get("unit") or "",
        "rate": float(data.get("rate") or 0),
        "hamali_rate": float(data.get("hamali_rate") or 0),
    }


# ---------------- UPDATE ITEM ----------------
def update_item(item_id, name, description, unit, rate, hamali_rate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE items
        SET name = %s,
            description = %s,
            unit = %s,
            rate = %s,
            hamali_rate = %s
        WHERE id = %s
    """, (name, description, unit, rate, hamali_rate, item_id))

    conn.commit()
    conn.close()


# ---------------- DELETE ITEM ----------------
def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM items WHERE id = %s", (item_id,))

    conn.commit()
    conn.close()


# ---------------- ADD / UPDATE ITEM (FOR EXCEL IMPORT) ----------------
def add_or_update_item(name, description, unit, rate, hamali_rate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO items (name, description, unit, rate, hamali_rate)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (name) DO UPDATE SET
            description = EXCLUDED.description,
            unit = EXCLUDED.unit,
            rate = EXCLUDED.rate,
            hamali_rate = EXCLUDED.hamali_rate
    """, (name, description, unit, rate, hamali_rate))

    conn.commit()
    conn.close()
