import sqlite3 
from db.connection import get_connection

def get_next_estimate_no():
    conn = get_connection()
    row = conn.execute(
        """
        SELECT estimate_no
        FROM estimates
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    conn.close()

    if not row:
        return "SRS001"

    last_no = row["estimate_no"]  # e.g. SRS007
    num = int(last_no.replace("SRS", ""))
    return f"SRS{num + 1:03d}"


def save_estimate_header(
    estimate_no,
    date,
    customer_id,
    items_total,
    hamali_total,
    auto_charge,
    discount,
    grand_total,
    pdf_path
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO estimates (
            estimate_no,
            date,
            customer_id,
            items_total,
            hamali_total,
            auto_charge,
            discount,
            grand_total,
            pdf_path,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """,
        (
            estimate_no,
            date,
            customer_id,
            items_total,
            hamali_total,
            auto_charge,
            discount,
            grand_total,
            pdf_path
        )
    )

    estimate_id = cur.lastrowid
    conn.commit()
    conn.close()
    return estimate_id


def save_estimate_items(estimate_id, items):
    conn = get_connection()
    cur = conn.cursor()

    for item in items:
        qty = item.get("qty", 0)
        rate = item.get("rate", 0.0)
        hamali_rate = item.get("hamali_rate", 0.0)

        cur.execute(
            """
            INSERT INTO estimate_items (
                estimate_id,
                item_name,
                description,
                qty,
                unit,
                rate,
                row_total,
                hamali_rate,
                hamali_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                estimate_id,
                item.get("item_name", ""),
                item.get("desc", ""),
                qty,
                item.get("unit", ""),
                rate,
                qty * rate,
                hamali_rate,
                qty * hamali_rate
            )
        )

    conn.commit()
    conn.close()

def update_estimate_header(
    estimate_id,
    date,
    customer_id,
    items_total,
    hamali_total,
    auto_charge,
    discount,
    grand_total,
    pdf_path
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE estimates SET
            date = ?,
            customer_id = ?,
            items_total = ?,
            hamali_total = ?,
            auto_charge = ?,
            discount = ?,
            grand_total = ?,
            pdf_path = ?
        WHERE id = ?
    """, (
        date,
        customer_id,
        items_total,
        hamali_total,
        auto_charge,
        discount,
        grand_total,
        pdf_path,
        estimate_id
    ))

    conn.commit()
    conn.close()

def delete_estimate_items(estimate_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM estimate_items WHERE estimate_id = ?", (estimate_id,))
    conn.commit()
    conn.close()

def get_estimate_summary():
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    total = conn.execute("""
        SELECT
            COUNT(*) AS count,
            COALESCE(SUM(grand_total), 0) AS amount
        FROM estimates
    """).fetchone()

    today = conn.execute("""
        SELECT
            COUNT(*) AS count,
            COALESCE(SUM(grand_total), 0) AS amount
        FROM estimates
        WHERE date = DATE('now')
    """).fetchone()

    conn.close()

    return {
        "total_count": total["count"],
        "total_amount": total["amount"],
        "today_count": today["count"],
        "today_amount": today["amount"]
    }

def estimate_exists(estimate_no):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM estimates WHERE estimate_no = ?",
        (estimate_no,)
    ).fetchone()
    conn.close()
    return row is not None

def get_filtered_estimates(
    estimate_no=None,
    customer_name=None,
    start_date=None,
    end_date=None
):
    conn = get_connection()

    query = """
        SELECT 
            e.id,
            e.estimate_no,
            e.date,
            c.name AS customer_name,
            e.grand_total,
            e.pdf_path
        FROM estimates e
        LEFT JOIN customers c ON e.customer_id = c.id
        WHERE 1=1
    """
    params = []

    if estimate_no:
        query += " AND e.estimate_no LIKE ?"
        params.append(f"%{estimate_no}%")

    if customer_name:
        query += " AND c.name = ?"
        params.append(customer_name)

    if start_date:
        query += " AND e.date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND e.date <= ?"
        params.append(end_date)

    query += " ORDER BY e.id DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows

def get_estimate_by_id(estimate_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    header = conn.execute(
        """
        SELECT e.*, c.name AS customer_name, c.phone, c.address
        FROM estimates e
        LEFT JOIN customers c ON e.customer_id = c.id
        WHERE e.id = ?
        """,
        (estimate_id,)
    ).fetchone()

    items = conn.execute(
        """
        SELECT item_name, description AS desc, qty, unit, rate, hamali_rate
        FROM estimate_items
        WHERE estimate_id = ?
        """,
        (estimate_id,)
    ).fetchall()

    conn.close()

    return dict(header), [dict(item) for item in items]


def delete_estimate(estimate_id):
    conn = get_connection()
    conn.execute("DELETE FROM estimate_items WHERE estimate_id = ?", (estimate_id,))
    conn.execute("DELETE FROM estimates WHERE id = ?", (estimate_id,))
    conn.commit()
    conn.close()

def get_all_estimates():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT 
            e.id,
            e.estimate_no,
            e.date,
            c.name AS customer_name,
            e.grand_total,
            e.pdf_path
        FROM estimates e
        LEFT JOIN customers c ON e.customer_id = c.id
        ORDER BY e.id DESC
        """
    ).fetchall()
    conn.close()
    return rows

def get_monthly_estimate_summary(year, month):
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    summary = conn.execute("""
        SELECT
            COUNT(*) AS count,
            COALESCE(SUM(grand_total), 0) AS amount
        FROM estimates
        WHERE strftime('%Y', date) = ?
          AND strftime('%m', date) = ?
    """, (str(year), f"{month:02d}")).fetchone()

    conn.close()
    return dict(summary)


def get_daywise_estimates(year, month):
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            date,
            COUNT(*) AS count,
            SUM(grand_total) AS amount
        FROM estimates
        WHERE strftime('%Y', date) = ?
          AND strftime('%m', date) = ?
        GROUP BY date
        ORDER BY date
    """, (str(year), f"{month:02d}")).fetchall()

    conn.close()
    return [dict(row) for row in rows]