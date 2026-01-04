import streamlit as st
import os
from datetime import date

from utilities.pdf_generator_utils import generate_estimate_pdf
from db.item_db import get_item_names, get_item
from db.estimate_db import save_estimate_header, update_estimate_header , delete_estimate_items , get_next_estimate_no, estimate_exists, get_estimate_by_id , save_estimate_items
 

from db.customer_db import (
    get_customer_names,
    get_customer_id, 
    get_customer, 
    customer_exists,
    add_customer
) 



def show():
    
    company_info = {
        "name": "Sri Rama Steel & Cement",
        "phone": "8885482288",
        "address": "Warangal Road, Huzurabad"
    }

    if "auto_charge" not in st.session_state:
        st.session_state.auto_charge = 0.0

    if "discount" not in st.session_state:
        st.session_state.discount = 0.0

    if "hamali_adjustment" not in st.session_state:
        st.session_state.hamali_adjustment = 0.0

    if "edit_estimate_id" in st.session_state:
        header, items = get_estimate_by_id(st.session_state.edit_estimate_id)

        # Header fields
        st.session_state.current_est_no = header["estimate_no"]
        st.session_state.est_items = [dict(item) for item in items]

        # Customer
        st.session_state.customer_mode = "existing"
        st.session_state.customer_name_input = header["customer_name"]

        # ✅ LOAD CHARGES (THIS FIXES YOUR ISSUE)
        st.session_state.auto_charge = header.get("auto_charge", 0.0)
        st.session_state.discount = header.get("discount", 0.0)

        # Optional (if you store it)
        st.session_state.hamali_adjustment = header.get("hamali_adjustment", 0.0)

    if "estimate_saved" not in st.session_state:
        st.session_state.estimate_saved = False

    # ---------- Session State Initialization ----------
    if "customer_mode" not in st.session_state:
        st.session_state.customer_mode = "existing"

    if "selected_customer" not in st.session_state:
        st.session_state.selected_customer = ""

    if "customer_name_input" not in st.session_state:
        st.session_state.customer_name_input = ""

    if "est_items" not in st.session_state:
        st.session_state.est_items = []

    if "auto_charge" not in st.session_state:
        st.session_state.auto_charge = 0.0

    if "discount" not in st.session_state:
        st.session_state.discount = 0.0

    st.header("Estimate")

    st.markdown(
    """
    <style>
    .amount-box {
        border: 1.5px solid #4F4F4F;
        padding: 6px;
        text-align: right;
        border-radius: 4px;
        font-weight: 600;
        background-color: #FAFAFA;
    }
    </style>
    """,
    unsafe_allow_html=True
    )



    if "current_est_no" not in st.session_state:
        st.session_state.current_est_no = get_next_estimate_no()

    # ---------------- Estimate Details ----------------
    st.markdown("### Estimate Details")
    col1, col2 = st.columns(2)

    with col1:
        est_no = st.text_input(
            "Estimate No",
            value=st.session_state.current_est_no,
            disabled=True
        )

    with col2:
        est_date = st.date_input("Date", value=date.today())

    st.divider()

   # ---------------- Customer Section ----------------
    st.markdown("### Customer")

    # ---- Session state init ----
    if "customer_mode" not in st.session_state:
        st.session_state.customer_mode = "existing"

    if "selected_customer" not in st.session_state:
        st.session_state.selected_customer = "— Search Customer —"

    if "customer_name_input" not in st.session_state:
        st.session_state.customer_name_input = ""

    # ---- Search box (combo box) ----
    customer_names = ["— Search Customer —"] + get_customer_names()

    selected = st.selectbox(
        "Search Customer",
        customer_names,
        index=customer_names.index(st.session_state.selected_customer)
        if st.session_state.selected_customer in customer_names
        else 0,
        key="customer_search"
    )

    customer_data = None

    # ---- Load customer data if selected ----
    if selected != "— Search Customer —":
        st.session_state.selected_customer = selected
        customer_data = get_customer(selected)
        st.session_state.customer_name_input = selected
    
    # ---- Mode selector (ROUND DOT) ----
    st.session_state.customer_mode = st.radio(
        "Customer Mode",
        ["existing", "new"],
        format_func=lambda x: "Existing Customer" if x == "existing" else "New Customer",
        horizontal=True
    )

    # ---- Clear selection if switched to NEW ----
    if st.session_state.customer_mode == "new":
        st.session_state.selected_customer = "— Search Customer —"
        customer_data = None

    # ---- Customer Name ----
    if st.session_state.customer_mode == "existing" and customer_data:
        customer_name = st.text_input(
            "Customer Name",
            value=customer_data["name"],
            disabled=True
        )
    else:
        customer_name = st.text_input(
            "Customer Name",
            value=st.session_state.customer_name_input,
            placeholder="Enter new customer name"
        )
        st.session_state.customer_name_input = customer_name

    # ---- Phone & Address ----
    col3, col4 = st.columns(2)

    with col3:
        phone = st.text_input(
            "Phone",
            value=customer_data["phone"] if customer_data else "",
            disabled=st.session_state.customer_mode == "existing" and customer_data is not None
        )

    with col4:
        address = st.text_input(
            "Address",
            value=customer_data["address"] if customer_data else "",
            disabled=st.session_state.customer_mode == "existing" and customer_data is not None
        )
    

    # ---- Status indicator ----
    if st.session_state.customer_mode == "existing" and customer_data:
        st.success("✔ Existing customer selected")
    elif st.session_state.customer_mode == "new":
        st.info("➕ New customer entry")

    st.divider()


    # ---------------- Items Section ----------------
    st.markdown("### Items")

    if "est_items" not in st.session_state:
        st.session_state.est_items = [
            {
                "item_name": "",
                "desc": "",
                "qty": 1,
                "unit": "",
                "rate": 0.0,
                "hamali_rate": 0.0
            }
        ]

    col_add, _, col_remove = st.columns([2, 8, 2])

    with col_add:
        if st.button("➕ Add Item"):
            st.session_state.est_items.append(
                {
                    "item_name": "",
                    "desc": "",
                    "qty": 1,
                    "unit": "",
                    "rate": 0.0,
                    "hamali_rate": 0.0
                }
            )

    # ---- Header ----
    h1, h2, h3, h4, h5, h6, h7, h8, h9 = st.columns([3, 3, 1, 1.5, 2, 2, 2, 2, 1])
    h1.markdown("**Item**")
    h2.markdown("**Description**")
    h3.markdown("**Qty**")
    h4.markdown("**Unit**")
    h5.markdown("**Rate**")
    h6.markdown("**Row Total**")
    h7.markdown("**Hamali**")
    h8.markdown("**Hamali Total**")
    h9.markdown("**Del**")

    grand_total = 0.0
    hamali_grand_total = 0.0

    item_names = [""] + get_item_names()

    for i, row in enumerate(st.session_state.est_items):
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([3, 3, 1, 1.5, 2, 2, 2, 2, 1])

        selected_item = c1.selectbox(
            f"item_{i}",
            item_names,
            index=item_names.index(row["item_name"])
            if row["item_name"] in item_names else 0,
            label_visibility="collapsed"
        )

        # Fetch from DB if item exists
        if selected_item:
            row["item_name"] = selected_item
            item_data = get_item(selected_item)

            row["desc"] = item_data["description"]
            row["unit"] = item_data["unit"]
            row["rate"] = item_data["rate"]
            row["hamali_rate"] = item_data["hamali_rate"]

        row["desc"] = c2.text_input(
            f"desc_{i}",
            value=row["desc"],
            label_visibility="collapsed"
        )

        row["qty"] = c3.number_input(
            f"qty_{i}",
            min_value=1,
            value=row["qty"],
            label_visibility="collapsed"
        )

        row["unit"] = c4.text_input(
            f"unit_{i}",
            value=row["unit"],
            label_visibility="collapsed"
        )

        row["rate"] = c5.number_input(
            f"rate_{i}",
            min_value=0.0,
            value=row["rate"],
            step=0.5,
            label_visibility="collapsed"
        )
    
        if row["item_name"] == "" or row["rate"] == 0:
            row.pop("_completed", None)

        # ---- ROW TOTAL (Qty × Rate) ----
        row_total = row["qty"] * row["rate"]
        grand_total += row_total

        c6.markdown(
            f"<div class='amount-box'>{row_total:.2f}</div>",
            unsafe_allow_html=True
        )

        # ---- HAMALI ----
        row["hamali_rate"] = c7.number_input(
            f"hamali_{i}",
            min_value=0.0,
            value=row["hamali_rate"],
            step=1.0,
            label_visibility="collapsed"
        )

        hamali_total = row["qty"] * row["hamali_rate"]
        hamali_grand_total += hamali_total

        c8.markdown(
            f"<div class='amount-box'>{hamali_total:.2f}</div>",
            unsafe_allow_html=True
        )

        # ---- DELETE ROW BUTTON ----
        if c9.button("❌", key=f"del_{i}"):
            st.session_state.est_items.pop(i)
            st.session_state._row_deleted = True
            st.rerun()



    st.divider()

    # ---- AUTO ADD ROW WHEN LAST ROW IS COMPLETED ----

    last_row = st.session_state.est_items[-1]

    is_last_row_filled = (
        last_row["item_name"] != "" and
        last_row["qty"] > 0 and
        last_row["rate"] > 0
    )

    # Prevent auto-add immediately after delete
    if is_last_row_filled and not st.session_state.get("_row_deleted", False):
        if not last_row.get("_completed"):
            last_row["_completed"] = True
            st.session_state.est_items.append(
                {
                    "item_name": "",
                    "desc": "",
                    "qty": 1,
                    "unit": "",
                    "rate": 0.0,
                    "hamali_rate": 0.0
                }
            )
            st.session_state._row_deleted = False
            st.rerun()

    # ---------------- Totals ----------------

    # ---- Hamali Final ----
    final_hamali_total = hamali_grand_total + st.session_state.hamali_adjustment

    # ---- Auto Charge ----
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(f"Items Total : ₹ {grand_total:.2f}")
        st.subheader(f"Hamali Charges : ₹ {final_hamali_total:.2f}")

    with col2:
        st.markdown("### Hamali Adjustment")
        st.session_state.hamali_adjustment = st.number_input(
            "Hamali Adjustment",
            value=st.session_state.hamali_adjustment,
            step=10.0,
            label_visibility="collapsed"
        )

    # ---- Auto ----
    st.session_state.auto_charge = st.number_input(
        "Auto Charges",
        value=st.session_state.auto_charge,
        step=50.0
    )

    # ---- Subtotal ----
    subtotal = grand_total + final_hamali_total + st.session_state.auto_charge

    st.subheader(f"Subtotal : ₹ {subtotal:.2f}")


    # ---- Discount ----
    st.session_state.discount = st.number_input(
        "Discount",
        value=st.session_state.discount,
        step=50.0
    )

    # ---- Final Total ----
    final_total = subtotal - st.session_state.discount

    st.divider()
    st.subheader(f"Grand Total : ₹ {final_total:.2f}")

    is_editing = "edit_estimate_id" in st.session_state

    # ---------------- Actions ----------------
    if st.button("💾 Save & Generate PDF", key="save_estimate_btn"):

        is_editing = "edit_estimate_id" in st.session_state

        if st.session_state.customer_mode == "existing" and not customer_data:
            st.error("Please select an existing customer")
            return

        if st.session_state.customer_mode == "new" and not customer_name.strip():
            st.error("Please enter customer name")
            return

        # 🔒 Prevent duplicate ONLY for new estimates
        if estimate_exists(st.session_state.current_est_no) and not is_editing:
            st.warning("Estimate already saved. Opening existing PDF.")
            return

        os.makedirs("bills", exist_ok=True)
        pdf_path = f"bills/{st.session_state.current_est_no}.pdf"

        # 1️⃣ Save customer ONLY on save
        if st.session_state.customer_mode == "new":
            if not customer_exists(customer_name):
                add_customer(
                    name=customer_name.strip(),
                    phone=phone.strip(),
                    address=address.strip()
                )

        # 2️⃣ Generate PDF
        generate_estimate_pdf(
            estimate={
                "estimate_number": st.session_state.current_est_no,
                "date": est_date
            },
            company_info=company_info,
            customer={
                "name": customer_name.strip(),
                "phone": phone.strip(),
                "address": address.strip()
            },
            items=st.session_state.est_items,
            filename=pdf_path,
            notes="",
            totals={
                "items_total": grand_total,
                "hamali_total": final_hamali_total,
                "auto_charge": st.session_state.auto_charge,
                "discount": st.session_state.discount,
                "grand_total": final_total
            }
        )

        # 3️⃣ Save estimate to DB
        customer_id = get_customer_id(customer_name)

        if is_editing:
            estimate_id = st.session_state.edit_estimate_id

            update_estimate_header(
                estimate_id=estimate_id,
                date=est_date,
                customer_id=customer_id,
                items_total=grand_total,
                hamali_total=final_hamali_total,
                auto_charge=st.session_state.auto_charge,
                discount=st.session_state.discount,
                grand_total=final_total,
                pdf_path=pdf_path
            )

            delete_estimate_items(estimate_id)

        else:
            estimate_id = save_estimate_header(
                estimate_no=st.session_state.current_est_no,
                date=est_date,
                customer_id=customer_id,
                items_total=grand_total,
                hamali_total=final_hamali_total,
                auto_charge=st.session_state.auto_charge,
                discount=st.session_state.discount,
                grand_total=final_total,
                pdf_path=pdf_path
            )

        save_estimate_items(
            estimate_id=estimate_id,
            items=st.session_state.est_items
        )

        st.success("Estimate saved and PDF generated")

        # Exit edit mode
        if is_editing:
            del st.session_state.edit_estimate_id
        else:
            st.session_state.current_est_no = get_next_estimate_no()

        # 4️⃣ Open PDF
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "🖨 Open / Print PDF",
                    f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    key="print_estimate_pdf"
                )

    
