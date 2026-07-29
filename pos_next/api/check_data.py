import frappe

def execute():
    # Check native is_combo_meal
    count_native = frappe.db.sql("select count(*) from `tabItem` where is_combo_meal=1")[0][0]
    print(f"Native is_combo_meal=1: {count_native}")

    # Check native calories
    count_calories = frappe.db.sql("select count(*) from `tabItem` where calories > 0")[0][0]
    print(f"Native calories > 0: {count_calories}")

    # Check custom_is_combo_meal
    count_custom = frappe.db.sql("select count(*) from `tabItem` where custom_is_combo_meal=1")[0][0]
    print(f"Custom custom_is_combo_meal=1: {count_custom}")

    # Check custom_calories
    count_custom_cal = frappe.db.sql("select count(*) from `tabItem` where custom_calories > 0")[0][0]
    print(f"Custom custom_calories > 0: {count_custom_cal}")

    # Sample native data
    sample = frappe.db.sql("select item_name, calories, is_combo_meal from `tabItem` where calories > 0 limit 5", as_dict=True)
    print(f"\nSample native data:")
    for s in sample:
        print(f"  {s.item_name}: {s.calories}cal, combo={s.is_combo_meal}")
