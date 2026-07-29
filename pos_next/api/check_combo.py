import frappe

def execute():
    """Check native is_combo_meal on Item"""
    items = frappe.db.sql("""
        SELECT name, item_name, is_combo_meal
        FROM `tabItem`
        WHERE is_combo_meal = 1
        ORDER BY item_name
    """, as_dict=True)
    print(f"Items with native is_combo_meal=1: {len(items)}")
    for i in items:
        print(f"  {i.name}: {i.item_name}")

    # Also check custom_is_combo_meal
    items2 = frappe.db.sql("""
        SELECT name, item_name, custom_is_combo_meal
        FROM `tabItem`
        WHERE custom_is_combo_meal = 1
        LIMIT 5
    """, as_dict=True)
    print(f"\nItems with custom_is_combo_meal=1 (sample): {len(items2)}")
    for i in items2:
        print(f"  {i.name}: {i.item_name}")
