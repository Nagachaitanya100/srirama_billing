from db.connection import get_connection


# ---------------- NEXT ESTIMATE NUMBER ----------------
def get_next_estimate_no():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT estimate_no
        FROM estimates
        ORDER BY id DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()

    if not row:
        return "SRS001"

    last_no = row[0]  # e.g. SRS007
    num = int(last_no.replace("SRS", ""))
    return f"SRS{num + 1:03d}"


# ---------------- SAVE ESTIMATE HEADER ----------------
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

    cur.execute("""
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
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        RETURNING id
    """, (
        estimate_no,
        date,
        customer_id,
        items_total,
        hamali_total,
        auto_charge,
        discount,
        grand_total,
        pdf_path
    ))

    estimate_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return estimate_id


# ---------------- SAVE ESTIMATE ITEMS ----------------
def save_estimate_items(estimate_id, items):
    conn = get_connection()
    cur = conn.cursor()

    for item in items:
        if not item.get("item_name"):
            continue  # skip empty rows

        cur.execute("""
            INSERT INTO estimate_items (
                estimate_id,
                item_name,
                description,
                qty,
                unit,
                rate,
                hamali_rate
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            estimate_id,
            item["item_name"],
            item.get("desc", ""),
            item["qty"],
            item.get("unit", ""),
            item["rate"],
            item.get("hamali_rate", 0)
        ))

    conn.commit()
    conn.close()



# ---------------- UPDATE ESTIMATE HEADER ----------------
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
            date = %s,
            customer_id = %s,
            items_total = %s,
            hamali_total = %s,
            auto_charge = %s,
            discount = %s,
            grand_total = %s,
            pdf_path = %s
        WHERE id = %s
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


# ---------------- DELETE ESTIMATE ITEMS ----------------
def delete_estimate_items(estimate_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM estimate_items WHERE estimate_id = %s", (estimate_id,))

    conn.commit()
    conn.close()


# ---------------- CHECK ESTIMATE EXISTS ----------------
def estimate_exists(estimate_no):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM estimates WHERE estimate_no = %s",
        (estimate_no,)
    )
    exists = cur.fetchone() is not None
    conn.close()
    return exists


# ---------------- ESTIMATE SUMMARY (DASHBOARD) ----------------
def get_estimate_summary():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) AS total_count,
            COALESCE(SUM(grand_total), 0) AS total_amount,
            COUNT(CASE WHEN date = CURRENT_DATE THEN 1 END) AS today_count,
            COALESCE(SUM(CASE WHEN date = CURRENT_DATE THEN grand_total END), 0) AS today_amount
        FROM estimates
    """)

    row = cur.fetchone()
    conn.close()

    return {
        "total_count": int(row[0]),
        "total_amount": float(row[1]),
        "today_count": int(row[2]),
        "today_amount": float(row[3]),
    }


# ---------------- FILTERED ESTIMATES (VIEW PAGE) ----------------
def get_filtered_estimates(
    estimate_no=None,
    customer_name=None,
    start_date=None,
    end_date=None
):
    conn = get_connection()
    cur = conn.cursor()

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
        query += " AND e.estimate_no ILIKE %s"
        params.append(f"%{estimate_no}%")

    if customer_name:
        query += " AND c.name = %s"
        params.append(customer_name)

    if start_date:
        query += " AND e.date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND e.date <= %s"
        params.append(end_date)

    query += " ORDER BY e.id DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    conn.close()
    return [dict(zip(columns, row)) for row in rows]


# ---------------- GET ESTIMATE BY ID (EDIT) ----------------
def get_estimate_by_id(estimate_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT e.*, c.name AS customer_name, c.phone, c.address
        FROM estimates e
        LEFT JOIN customers c ON e.customer_id = c.id
        WHERE e.id = %s
    """, (estimate_id,))
    header_row = cur.fetchone()
    header_cols = [d[0] for d in cur.description]

    cur.execute("""
        SELECT
            item_name,
            description AS desc,
            qty,
            unit,
            rate,
            hamali_rate
        FROM estimate_items
        WHERE estimate_id = %s
    """, (estimate_id,))
    item_rows = cur.fetchall()
    item_cols = [d[0] for d in cur.description]

    conn.close()

    header = dict(zip(header_cols, header_row)) if header_row else None
    items = [dict(zip(item_cols, r)) for r in item_rows]

    return header, items


# ---------------- DELETE ESTIMATE ----------------
def delete_estimate(estimate_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM estimate_items WHERE estimate_id = %s", (estimate_id,))
    cur.execute("DELETE FROM estimates WHERE id = %s", (estimate_id,))

    conn.commit()
    conn.close()


# ---------------- MONTHLY SUMMARY ----------------
def get_monthly_estimate_summary(year, month):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) AS count,
            COALESCE(SUM(grand_total), 0) AS amount
        FROM estimates
        WHERE EXTRACT(YEAR FROM date) = %s
          AND EXTRACT(MONTH FROM date) = %s
    """, (year, month))

    row = cur.fetchone()
    conn.close()

    return {
        "count": int(row[0]),
        "amount": float(row[1]),
    }


# ---------------- DAY-WISE SUMMARY ----------------
def get_daywise_estimates(year, month):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            date,
            COUNT(*) AS count,
            COALESCE(SUM(grand_total), 0) AS amount
        FROM estimates
        WHERE EXTRACT(YEAR FROM date) = %s
          AND EXTRACT(MONTH FROM date) = %s
        GROUP BY date
        ORDER BY date
    """, (year, month))

    rows = cur.fetchall()
    conn.close()

    return [
        {"date": r[0], "count": int(r[1]), "amount": float(r[2])}
        for r in rows
    ]
