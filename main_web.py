import streamlit as st
from modules import (
    dashboard,
    invoice,
    invoice_view,
    estimate,
    estimate_view,
    customers,
    items , 
    monthly_report
)


st.set_page_config(page_title="Inv Web", layout="wide")

# ---------- Session State ----------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------- Custom Sidebar ----------
with st.sidebar:
    st.title("Inv Web")

    if st.button("Dashboard"):
        st.session_state.page = "Dashboard"

    st.markdown("---")

    if st.button("Create Estimate"):
        st.session_state.page = "Create Estimate"

    if st.button("View Estimates"):
        st.session_state.page = "View Estimates"

    st.markdown("---")

    if st.button("Customers"):
        st.session_state.page = "Customers"

    if st.button("Items"):
        st.session_state.page = "Items"

    st.markdown("---")

    if st.button("📊 Monthly Report"):
        st.session_state.page = "Monthly Report"

# ---------- Routing ----------
if st.session_state.page == "Dashboard":
    dashboard.show()

elif st.session_state.page == "Create Estimate":
    estimate.show()

elif st.session_state.page == "View Estimates":
    estimate_view.show()

elif st.session_state.page == "Customers":
    customers.show()

elif st.session_state.page == "Items":
    items.show()

elif st.session_state.page == "Monthly Report":
    monthly_report.show()

