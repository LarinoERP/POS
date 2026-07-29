import frappe

def execute():
    # Check ALL custom fields on Item related to combo
    cfs = frappe.db.sql("""
        SELECT name, fieldname, fieldtype, label, dt, module, idx
        FROM `tabCustom Field`
        WHERE dt = 'Item' AND fieldname LIKE '%combo%'
        ORDER BY idx
    """, as_dict=True)
    print(f"Custom Fields on Item with 'combo': {len(cfs)}")
    for c in cfs:
        print(f"  {c.name}: fieldname={c.fieldname}, module={c.module}")

    # Also check if there are multiple is_combo_meal fields
    dups = frappe.db.sql("""
        SELECT name, fieldname, dt
        FROM `tabCustom Field`
        WHERE dt = 'Item' AND fieldname = 'is_combo_meal'
    """, as_dict=True)
    print(f"\nDuplicate is_combo_meal fields: {len(dups)}")
    for d in dups:
        print(f"  {d.name}")

    # Direct SQL count with the exact query the Desk list view would use
    count1 = frappe.db.sql("SELECT count(*) FROM `tabItem` WHERE `is_combo_meal` = 1")[0][0]
    count2 = frappe.db.sql("SELECT count(*) FROM `tabItem` WHERE `custom_is_combo_meal` = 1")[0][0]
    print(f"\nDirect SQL:")
    print(f"  WHERE is_combo_meal = 1: {count1}")
    print(f"  WHERE custom_is_combo_meal = 1: {count2}")

    # Check the native is_combo_meal column - is it part of Item DocType JSON?
    item_meta = frappe.get_meta("Item")
    native_field = None
    for f in item_meta.fields:
        if f.fieldname == "is_combo_meal":
            native_field = f
            break
    if native_field:
        print(f"\nNative is_combo_meal field on Item DocType: fieldtype={native_field.fieldtype}, label={native_field.label}")
    else:
        print(f"\nNo native is_combo_meal field in Item DocType meta (only custom field)")
