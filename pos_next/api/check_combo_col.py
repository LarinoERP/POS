import frappe

def execute():
    # Check if is_combo_meal or custom_is_combo_meal exists
    cols = frappe.db.sql("show columns from `tabItem` like '%combo%'", as_dict=True)
    print(f"Combo columns on Item: {[c.Field for c in cols]}")

    # Check what custom_field exists
    cf = frappe.db.sql("select fieldname from `tabCustom Field` where dt='Item' and fieldname like '%combo%'", as_dict=True)
    print(f"Custom Fields with combo: {[c.fieldname for c in cf]}")

    # Check is_combo_meal column type
    try:
        col_info = frappe.db.sql("describe `tabItem` `is_combo_meal`", as_dict=True)
        print(f"is_combo_meal column: {col_info}")
    except:
        print("No is_combo_meal column")

    try:
        col_info = frappe.db.sql("describe `tabItem` `custom_is_combo_meal`", as_dict=True)
        print(f"custom_is_combo_meal column: {col_info}")
    except:
        print("No custom_is_combo_meal column")
