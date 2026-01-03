import streamlit as st
import os
from datetime import date
from db.estimate_db import (
    get_filtered_estimates,
    delete_estimate
)
from db.customer_db import get_customer_names


def show():
    st.header("📄 View Estimates")

    # ---------------- FILTERS ----------------
    with st.expander("🔍 Filters", expanded=True):
        f1, f2, f3, f4 = st.columns([2, 3, 2, 2])

        with f1:
            search_est = st.text_input(
                "Estimate No",
                placeholder="SRS001"
            )

        with f2:
            customers = ["All"] + get_customer_names()
            selected_customer = st.selectbox(
                "Customer",
                customers
            )

        with f3:
            start_date = st.date_input(
                "From Date",
                value=None
            )

        with f4:
            end_date = st.date_input(
                "To Date",
                value=None
            )

    customer_filter = None if selected_customer == "All" else selected_customer

    # ---------------- FETCH DATA ----------------
    estimates = get_filtered_estimates(
        estimate_no=search_est or None,
        customer_name=customer_filter,
        start_date=start_date,
        end_date=end_date
    )

    if not estimates:
        st.info("No estimates found for the selected filters.")
        return

    # ---------------- TABLE HEADER ----------------
    h1, h2, h3, h4, h5 = st.columns([2, 2, 3, 2, 3])
    h1.markdown("**Estimate No**")
    h2.markdown("**Date**")
    h3.markdown("**Customer**")
    h4.markdown("**Total (₹)**")
    h5.markdown("**Actions**")

    st.divider()

    # ---------------- ROWS ----------------
    for est in estimates:
        c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 2, 3])

        c1.write(est["estimate_no"])
        c2.write(est["date"])
        c3.write(est["customer_name"] or "—")
        c4.write(f"{est['grand_total']:.2f}")

        a1, a2, a3 = c5.columns(3)

        # 🖨 Reprint PDF
        if est["pdf_path"] and os.path.exists(est["pdf_path"]):
            with open(est["pdf_path"], "rb") as f:
                a1.download_button(
                    "🖨",
                    f,
                    file_name=os.path.basename(est["pdf_path"]),
                    mime="application/pdf",
                    key=f"print_{est['id']}"
                )
        else:
            a1.write("—")

        # ✏️ Edit
        if a2.button("✏️", key=f"edit_{est['id']}"):
            st.session_state.edit_estimate_id = est["id"]
            st.session_state.page = "Create Estimate"
            st.rerun()

        # ❌ Delete
        if a3.button("❌", key=f"del_{est['id']}"):
            st.session_state.delete_estimate_id = est["id"]

    # ---------------- DELETE CONFIRMATION ----------------
    if "delete_estimate_id" in st.session_state:
        st.warning("Are you sure you want to delete this estimate?")

        col_yes, col_no = st.columns(2)

        if col_yes.button("Yes, Delete", key="confirm_delete"):
            delete_estimate(st.session_state.delete_estimate_id)
            st.success("Estimate deleted successfully")
            del st.session_state.delete_estimate_id
            st.rerun()

        if col_no.button("Cancel", key="cancel_delete"):
            del st.session_state.delete_estimate_id
