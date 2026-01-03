import streamlit as st
from datetime import date

def show():
    st.header("Create Invoice")

    # ---------------- Invoice Details ----------------
    st.markdown("### Invoice Details")
    col1, col2 = st.columns(2)
    with col1:
        invoice_no = st.text_input("Invoice Number", placeholder="INV-001")
    with col2:
        invoice_date = st.date_input("Invoice Date", value=date.today())

    # ---------------- Customer Details ----------------
    st.markdown("### Customer Details")

    # Simple customer mode for now (DB-ready later)
    customer_mode = st.radio(
        "Customer Type",
        ["New Customer", "Existing Customer"],
        horizontal=True
    )

    if customer_mode == "Existing Customer":
        # Placeholder list (replace with DB later)
        customer_name = st.selectbox(
            "Select Customer",
            ["— Select —", "Ramesh", "Suresh", "Mahesh"]
        )
        customer_phone = st.text_input("Customer Phone", disabled=True)
        customer_address = st.text_area("Customer Address", disabled=True)
    else:
        customer_name = st.text_input("Customer Name")
        customer_phone = st.text_input("Customer Phone")
        customer_address = st.text_area("Customer Address")

    st.divider()

    # ---------------- Items Section ----------------
    st.markdown("### Items")

    # Initialize items in session state
    if "items" not in st.session_state:
        st.session_state.items = [
            {"name": "", "qty": 1, "rate": 0.0, "gst": 0.0}
        ]

    # Add / Remove item controls
    col_add, col_space, col_remove = st.columns([2, 8, 2])
    with col_add:
        if st.button("➕ Add Item"):
            st.session_state.items.append(
                {"name": "", "qty": 1, "rate": 0.0, "gst": 0.0}
            )
    with col_remove:
        if st.button("➖ Remove Last") and len(st.session_state.items) > 1:
            st.session_state.items.pop()

    # Table header
    h1, h2, h3, h4, h5 = st.columns([4, 2, 2, 2, 2])
    h1.markdown("**Item**")
    h2.markdown("**Qty**")
    h3.markdown("**Rate**")
    h4.markdown("**GST %**")
    h5.markdown("**Amount**")

    subtotal = 0.0
    total_tax = 0.0

    # Render rows
    for i, item in enumerate(st.session_state.items):
        c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 2])

        item["name"] = c1.text_input(
            f"item_name_{i}", value=item["name"], label_visibility="collapsed"
        )
        item["qty"] = c2.number_input(
            f"item_qty_{i}", min_value=1, value=item["qty"], label_visibility="collapsed"
        )
        item["rate"] = c3.number_input(
            f"item_rate_{i}", min_value=0.0, value=item["rate"], step=0.5,
            label_visibility="collapsed"
        )
        item["gst"] = c4.number_input(
            f"item_gst_{i}", min_value=0.0, max_value=100.0,
            value=item["gst"], step=1.0, label_visibility="collapsed"
        )

        line_amount = item["qty"] * item["rate"]
        tax_amount = line_amount * (item["gst"] / 100)

        subtotal += line_amount
        total_tax += tax_amount

        c5.write(f"{line_amount + tax_amount:.2f}")

    st.divider()

    # ---------------- Totals ----------------
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("**Subtotal:**")
        st.write("**Total GST:**")
        st.write("**Grand Total:**")
    with col_t2:
        st.write(f"{subtotal:.2f}")
        st.write(f"{total_tax:.2f}")
        st.write(f"**{(subtotal + total_tax):.2f}**")

    st.divider()

    # ---------------- Actions ----------------
    col_s1, col_s2 = st.columns([3, 2])
    with col_s1:
        if st.button("💾 Save Invoice"):
            st.success("Invoice captured in UI (DB save will be added next).")
    with col_s2:
        st.button("🧾 Generate PDF (later)")
