import streamlit as st
from datetime import date
from db.estimate_db import (
    get_monthly_estimate_summary,
    get_daywise_estimates
)


def show():
    st.header("📊 Monthly Estimate Report")

    today = date.today()

    col1, col2 = st.columns(2)

    with col1:
        year = st.selectbox(
            "Year",
            list(range(today.year - 5, today.year + 1)),
            index=5
        )

    with col2:
        month = st.selectbox(
            "Month",
            list(range(1, 13)),
            index=today.month - 1,
            format_func=lambda x: date(1900, x, 1).strftime("%B")
        )

    st.divider()

    # ---------- SUMMARY ----------
    summary = get_monthly_estimate_summary(year, month)

    c1, c2 = st.columns(2)

    c1.metric(
        "📄 Total Estimates",
        summary["count"]
    )

    c2.metric(
        "💰 Total Amount",
        f"₹ {summary['amount']:.2f}"
    )

    st.divider()

    # ---------- DAY-WISE TABLE ----------
    st.subheader("📅 Day-wise Breakdown")

    rows = get_daywise_estimates(year, month)

    if not rows:
        st.info("No estimates found for this month.")
        return

    st.dataframe(
        rows,
        use_container_width=True
    )

