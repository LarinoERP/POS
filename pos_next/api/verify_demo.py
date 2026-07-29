import frappe

def execute():
    """Final verification of all restaurant data on demo.site"""
    # Floors & tables
    floors = frappe.db.sql("select name, floor_name from `tabRestaurant Floor`", as_dict=True)
    print(f"Floors: {len(floors)}")
    for f in floors:
        tables = frappe.db.sql("select table_number, status from `tabRestaurant Table` where floor=%s", f.name, as_dict=True)
        print(f"  {f.floor_name}: {len(tables)} tables")

    # POS Settings
    s = frappe.db.sql("select enable_table_service, enable_combos, enable_reservations from `tabPOS Settings` limit 1", as_dict=True)
    if s:
        s = s[0]
        print(f"\nPOS Settings: table_service={s.enable_table_service}, combos={s.enable_combos}, reservations={s.enable_reservations}")

    # Combo Meals
    combos = frappe.db.sql("select name, combo_name from `tabCombo Meal`", as_dict=True)
    print(f"\nCombo Meals: {len(combos)}")
    for c in combos:
        items = frappe.db.sql("select item_group from `tabCombo Meal Item Group` where parent=%s", c.name, as_dict=True)
        print(f"  {c.combo_name}: {[i.item_group for i in items]}")

    # Combo meal items
    combo_items = frappe.db.sql("select name, item_name from `tabItem` where custom_is_combo_meal=1", as_dict=True)
    print(f"\nItems with is_combo_meal=1: {len(combo_items)}")
    for i in combo_items:
        print(f"  {i.item_name}")

    # Food items with nutrition
    food = frappe.db.sql("select item_name, custom_calories, custom_protein, custom_is_vegetarian, custom_is_vegan from `tabItem` where ifnull(custom_calories,0) > 0 order by item_name", as_dict=True)
    print(f"\nFood items with nutrition: {len(food)}")
    for i in food:
        flags = []
        if i.custom_is_vegetarian: flags.append("V")
        if i.custom_is_vegan: flags.append("VG")
        print(f"  {i.item_name}: {i.custom_calories}cal {i.custom_protein}g protein {' '.join(flags)}")

    # Kitchen Stations
    stations = frappe.db.sql("select name, station_name from `tabKitchen Station`", as_dict=True)
    print(f"\nKitchen Stations: {len(stations)}")
    for s in stations:
        print(f"  {s.station_name}")

    # User roles
    roles = frappe.db.sql("select role from `tabHas Role` where parent='Administrator'", as_dict=True)
    print(f"\nAdministrator roles: {[r.role for r in roles]}")

    print("\n--- ALL DONE ---")
