import frappe

def execute():
    # Check all columns related to our fields
    cols = frappe.db.sql("show columns from `tabItem`", as_dict=True)
    custom_cols = [c.Field for c in cols if c.Field.startswith('custom_')]
    nutrition_cols = [c.Field for c in cols if c.Field in ('calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium', 'serving_size', 'allergens', 'is_vegetarian', 'is_vegan', 'is_combo_meal')]
    print(f"Native nutrition/combo columns: {nutrition_cols}")
    print(f"Custom columns count: {len(custom_cols)}")
    print(f"Custom columns: {custom_cols}")
