import streamlit as st
from db.customer_db import (
    add_customer,
    get_all_customers,
    customer_exists,
    get_customer_by_id,
    update_customer,
    delete_customer
)


def show():
    st.header("Customers")

    tab_add, tab_list = st.tabs(["➕ Add / Edit Customer", "📋 Customer List"])

    # ---------- ADD / EDIT CUSTOMER ----------
    with tab_add:

        editing = "edit_customer_id" in st.session_state

        if editing:
            customer = get_customer_by_id(st.session_state.edit_customer_id)
            st.subheader("✏️ Edit Customer")
        else:
            customer = {}

        name = st.text_input(
            "Customer Name",
            value=customer.get("name", "")
        )

        phone = st.text_input(
            "Phone",
            value=customer.get("phone", "")
        )

        address = st.text_input(
            "Address",
            value=customer.get("address", "")
        )

        if st.button("💾 Save Customer"):
            if not name.strip():
                st.error("Customer name is required")
                return

            if editing:
                update_customer(
                    customer_id=st.session_state.edit_customer_id,
                    name=name.strip(),
                    phone=phone.strip(),
                    address=address.strip()
                )
                del st.session_state.edit_customer_id
                st.success("Customer updated successfully")
            else:
                if customer_exists(name.strip()):
                    st.warning("Customer already exists")
                    return

                add_customer(
                    name=name.strip(),
                    phone=phone.strip(),
                    address=address.strip()
                )
                st.success("Customer added successfully")

            st.rerun()

    # ---------- CUSTOMER LIST ----------
    with tab_list:
        st.subheader("Customer List")

        customers = get_all_customers()

        if not customers:
            st.info("No customers found")
            return

        search = st.text_input("🔍 Search (name / phone / address)")

        if search:
            s = search.lower()
            customers = [
                c for c in customers
                if s in c["name"].lower()
                or s in (c["phone"] or "").lower()
                or s in (c["address"] or "").lower()
            ]

        if not customers:
            st.warning("No matching customers")
            return

        h1, h2, h3, h4 = st.columns([3, 2, 3, 2])
        h1.markdown("**Name**")
        h2.markdown("**Phone**")
        h3.markdown("**Address**")
        h4.markdown("**Actions**")

        st.divider()

        for cust in customers:
            c1, c2, c3, c4 = st.columns([3, 2, 3, 2])

            c1.write(cust["name"])
            c2.write(cust["phone"])
            c3.write(cust["address"])

            e1, e2 = c4.columns(2)

            if e1.button("✏️", key=f"edit_cust_{cust['id']}"):
                st.session_state.edit_customer_id = cust["id"]
                st.session_state.page = "Customers"
                st.rerun()

            if e2.button("❌", key=f"del_cust_{cust['id']}"):
                st.session_state.delete_customer_id = cust["id"]

        # ---------- DELETE CONFIRMATION ----------
        if "delete_customer_id" in st.session_state:
            st.warning("Are you sure you want to delete this customer?")

            col_yes, col_no = st.columns(2)

            if col_yes.button("Yes, Delete", key="confirm_delete_customer"):
                delete_customer(st.session_state.delete_customer_id)
                del st.session_state.delete_customer_id
                st.success("Customer deleted successfully")
                st.rerun()

            if col_no.button("Cancel", key="cancel_delete_customer"):
                del st.session_state.delete_customer_id
