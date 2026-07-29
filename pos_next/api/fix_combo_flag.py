import frappe

def execute():
    # Mark items that belong to combo meal item groups
    combos = frappe.get_all("Combo Meal", filters={"is_active": 1}, fields=["name", "combo_name"])
    marked = 0
    for combo in combos:
        item_groups = frappe.get_all(
            "Combo Meal Item Group",
            filters={"parent": combo.name},
            fields=["item_group"],
        )
        for ig in item_groups:
            items = frappe.get_all("Item", filters={"item_group": ig.item_group}, pluck="name")
            for item_name in items:
                frappe.db.set_value("Item", item_name, "is_combo_meal", 1, update_modified=False)
                frappe.db.set_value("Item", item_name, "custom_is_combo_meal", 1, update_modified=False)
                marked += 1

    frappe.db.commit()
    print(f"Marked {marked} items as is_combo_meal=1")

    # Verify
    count = frappe.db.sql("select count(*) from `tabItem` where is_combo_meal=1")[0][0]
    print(f"Total items with is_combo_meal=1: {count}")
