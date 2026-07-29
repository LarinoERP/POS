import frappe

def execute():
    """Check and fix custom fields on Item"""
    # Check what custom fields exist
    fields = frappe.db.sql(
        "select fieldname, fieldtype, label from `tabCustom Field` where dt='Item' and module='POS Next' order by idx",
        as_dict=True
    )
    print(f"Custom Fields on Item (module=POS Next): {len(fields)}")
    for f in fields:
        print(f"  - {f.fieldname} ({f.fieldtype}): {f.label}")

    # Check which columns actually exist
    columns = frappe.db.sql("show columns from `tabItem` like 'custom_%'", as_dict=True)
    existing_cols = {c.Field for c in columns}
    print(f"\nExisting custom_ columns on Item: {len(existing_cols)}")

    # Find missing columns
    missing = []
    for f in fields:
        col_name = f"custom_{f['fieldname']}"
        if f['fieldtype'] in ('Section Break', 'Column Break', 'Tab Break'):
            continue
        if col_name not in existing_cols:
            missing.append(f)

    if missing:
        print(f"\nMissing columns ({len(missing)}):")
        for f in missing:
            print(f"  - custom_{f['fieldname']} ({f['fieldtype']})")

        # Add missing columns
        type_map = {
            'Data': 'varchar(140)',
            'Int': 'int(11)',
            'Float': 'decimal(21,9)',
            'Check': 'int(11)',
            'Small Text': 'text',
            'Text': 'text',
            'Select': 'varchar(140)',
            'Link': 'varchar(140)',
        }
        for f in missing:
            col_name = f"custom_{f['fieldname']}"
            mysql_type = type_map.get(f['fieldtype'], 'varchar(140)')
            try:
                default_val = '0' if f['fieldtype'] in ('Int', 'Float', 'Check') else "''"
                frappe.db.sql(f"ALTER TABLE `tabItem` ADD COLUMN `{col_name}` {mysql_type} DEFAULT {default_val}")
                print(f"  + Added column: {col_name}")
            except Exception as e:
                print(f"  ! Error adding {col_name}: {e}")

        frappe.db.commit()
    else:
        print("\nAll columns present!")

    # Clear cache to rebuild schema
    frappe.clear_cache()
    print("\nCache cleared!")
