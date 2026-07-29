import frappe

def execute():
    """Fix combo meal items and assign roles"""

    # 1. Add child table records to Combo Meals
    combos = frappe.get_all("Combo Meal", fields=["name", "combo_name"])
    for combo in combos:
        existing = frappe.get_all("Combo Meal Item Group", filters={"parent": combo.name}, fields=["item_group"])
        if existing:
            print(f"  {combo.combo_name} already has item groups: {[e.item_group for e in existing]}")
            continue

        doc = frappe.get_doc("Combo Meal", combo.name)
        if combo.combo_name == "Lunch Deal":
            doc.append("item_groups", {"group_name": "Choose a Starter", "item_group": "Starters", "min_qty": 1, "max_qty": 1, "is_required": 1})
            doc.append("item_groups", {"group_name": "Choose a Main", "item_group": "Main Course", "min_qty": 1, "max_qty": 1, "is_required": 1})
        elif combo.combo_name == "Family Meal":
            doc.append("item_groups", {"group_name": "Choose a Starter", "item_group": "Starters", "min_qty": 1, "max_qty": 2, "is_required": 1})
            doc.append("item_groups", {"group_name": "Choose a Main", "item_group": "Main Course", "min_qty": 2, "max_qty": 4, "is_required": 1})
            doc.append("item_groups", {"group_name": "Choose a Dessert", "item_group": "Desserts", "min_qty": 1, "max_qty": 4, "is_required": 0})
        doc.save(ignore_permissions=True)
        groups = [(ig.group_name, ig.item_group) for ig in doc.item_groups]
        print(f"  {combo.combo_name}: added item groups {groups}")

    frappe.db.commit()

    # 2. Mark items that belong to combo meal item groups
    combos = frappe.get_all("Combo Meal", filters={"is_active": 1}, fields=["name", "combo_name"])
    for combo in combos:
        item_groups = frappe.get_all(
            "Combo Meal Item Group",
            filters={"parent": combo.name},
            fields=["item_group"],
        )
        for ig in item_groups:
            items = frappe.get_all("Item", filters={"item_group": ig.item_group}, pluck="name")
            for item_name in items:
                frappe.db.set_value("Item", item_name, "custom_is_combo_meal", 1, update_modified=False)
                print(f"    Marked {item_name} as combo meal item")

    frappe.db.commit()

    # 3. Assign POS Manager + POSNext Cashier roles to Administrator
    admin_roles_to_add = ["POS Manager", "POSNext Cashier"]
    for role_name in admin_roles_to_add:
        exists = frappe.db.exists("Has Role", {"parent": "Administrator", "role": role_name})
        if exists:
            print(f"  Administrator already has role: {role_name}")
        else:
            frappe.get_doc({
                "doctype": "Has Role",
                "parent": "Administrator",
                "parenttype": "User",
                "parentfield": "roles",
                "role": role_name,
            }).insert(ignore_permissions=True)
            print(f"  Added role: {role_name} to Administrator")

    frappe.db.commit()
    print("\nDone! Combos, items, and roles fixed.")
