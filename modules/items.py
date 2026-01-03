import streamlit as st
import pandas as pd
from io import BytesIO

from db.item_db import add_item , get_all_items , get_item_by_id, update_item, delete_item , add_or_update_item

def show():
    st.header("Items")

    tab_add, tab_list, tab_ie = st.tabs(
        ["➕ Add Item", "📋 Item List", "📥 Import / 📤 Export"]
    )

    # ---------- ADD / EDIT ITEM ----------
    with tab_add:

        editing = "edit_item_id" in st.session_state

        if editing:
            item = get_item_by_id(st.session_state.edit_item_id)
            st.subheader("✏️ Edit Item")
        else:
            item = {}

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Item Name",
                value=item.get("name", "")
            )

            unit_list = ["pcs", "Kg", "Box", "Bag", "Dozen", "feet", "litre", "Meter"]
            unit = st.selectbox(
                "Unit",
                unit_list,
                index=unit_list.index(item.get("unit", "pcs"))
            )

        with col2:
            rate = st.number_input(
                "Rate",
                min_value=0.0,
                step=0.5,
                value=float(item.get("rate", 0.0))
            )

            hamali = st.number_input(
                "Hamali Rate (per unit)",
                min_value=0.0,
                step=1.0,
                value=float(item.get("hamali_rate", 0.0))
            )

        desc = st.text_area(
            "Description",
            value=item.get("description", ""),
            height=80
        )

        # ---------- SAVE ----------
        if st.button("💾 Save Item"):
            if not name.strip():
                st.error("Item name is required")
                return

            if editing:
                update_item(
                    item_id=st.session_state.edit_item_id,
                    name=name.strip(),
                    description=desc.strip(),
                    unit=unit,
                    rate=rate,
                    hamali_rate=hamali
                )
                del st.session_state.edit_item_id
                st.success("Item updated successfully")
            else:
                add_item(
                    name=name.strip(),
                    description=desc.strip(),
                    unit=unit,
                    rate=rate,
                    hamali_rate=hamali
                )
                st.success("Item added successfully")

            st.rerun()
 

        editing = "edit_item_id" in st.session_state

        if editing:
            item = get_item_by_id(st.session_state.edit_item_id)
            st.subheader("✏️ Edit Item")
        else:
            item = {}

    # ---------- ITEM LIST ----------
    with tab_list:
        st.subheader("Item List")

        items = get_all_items()

        if not items:
            st.warning("No items found")
            return

        search = st.text_input("🔍 Search (name / unit / rate / hamali / description)")

        if search:
            s = search.lower()

            def match(item):
                return (
                    s in item["name"].lower()
                    or s in (item["description"] or "").lower()
                    or s in item["unit"].lower()
                    or s in str(item["rate"])
                    or s in str(item["hamali_rate"])
                )

            items = [item for item in items if match(item)]

        if not items:
            st.info("No matching items")
            return

        h1, h2, h3, h4, h5, h6 = st.columns([3, 3, 1.5, 2, 2, 2])
        h1.markdown("**Item**")
        h2.markdown("**Description**")
        h3.markdown("**Unit**")
        h4.markdown("**Rate**")
        h5.markdown("**Hamali**")
        h6.markdown("**Actions**")

        st.divider()

        for item in items:
            c1, c2, c3, c4, c5, c6 = st.columns([3, 3, 1.5, 2, 2, 2])

            c1.write(item["name"])
            c2.write(item["description"])
            c3.write(item["unit"])
            c4.write(f"{item['rate']:.2f}")
            c5.write(f"{item['hamali_rate']:.2f}")

            e1, e2 = c6.columns(2)

            if e1.button("✏️", key=f"edit_item_{item['id']}"):
                st.session_state.edit_item_id = item["id"]
                st.session_state.page = "Items"
                st.rerun()

            if e2.button("❌", key=f"del_item_{item['id']}"):
                st.session_state.delete_item_id = item["id"]

        # ---------- DELETE CONFIRMATION ----------
        if "delete_item_id" in st.session_state:

            st.warning("Are you sure you want to delete this item?")

            col_yes, col_no = st.columns(2)

            if col_yes.button("Yes, Delete", key="confirm_delete_item"):
                delete_item(st.session_state.delete_item_id)
                del st.session_state.delete_item_id
                st.success("Item deleted successfully")
                st.rerun()

            if col_no.button("Cancel", key="cancel_delete_item"):
                del st.session_state.delete_item_id

        

    # ---------- IMPORT / EXPORT ----------
    with tab_ie:
        col_imp, col_exp = st.columns(2)

        
        # ---- IMPORT ----
        with col_imp:
            st.subheader("Import Items (Excel)")

            uploaded_file = st.file_uploader(
                "Upload Excel File",
                type=["xlsx"]
            )

            if uploaded_file is not None:
                df = pd.read_excel(uploaded_file)

                required_cols = [
                    "Item Name",
                    "Description",
                    "Unit",
                    "Rate",
                    "Hamali Rate"
                ]

                if not all(col in df.columns for col in required_cols):
                    st.error("Invalid Excel format. Please use correct template.")
                else:
                    imported = 0
                    for _, row in df.iterrows():
                        add_or_update_item(
                            name=str(row["Item Name"]).strip(),
                            description=str(row["Description"]).strip(),
                            unit=str(row["Unit"]).strip(),
                            rate=float(row["Rate"]),
                            hamali_rate=float(row["Hamali Rate"])
                        )
                        imported += 1

                    st.success(f"✅ {imported} items imported successfully")
                    st.rerun()

        # ---- EXPORT ----
        with col_exp:
            st.subheader("Export Items")

            items = get_all_items()

            if not items:
                st.warning("No items to export")
            else:
                export_df = pd.DataFrame([
                    {
                        "Item Name": i["name"],
                        "Description": i["description"],
                        "Unit": i["unit"],
                        "Rate": i["rate"],
                        "Hamali Rate": i["hamali_rate"]
                    }
                    for i in items
                ])

                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    export_df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Items"
                    )

                st.download_button(
                    "📤 Download Items Excel",
                    data=output.getvalue(),
                    file_name="items.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

