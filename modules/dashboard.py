import streamlit as st
from db.estimate_db import get_estimate_summary


def show():
    st.header("📊 Dashboard")

    summary = get_estimate_summary()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        label="📄 Total Estimates",
        value=summary["total_count"]
    )

    c2.metric(
        label="💰 Total Amount",
        value=f"₹ {summary['total_amount']:.2f}"
    )

    c3.metric(
        label="📆 Today Estimates",
        value=summary["today_count"]
    )

    c4.metric(
        label="💵 Today Amount",
        value=f"₹ {summary['today_amount']:.2f}"
    )

    st.divider()

    
