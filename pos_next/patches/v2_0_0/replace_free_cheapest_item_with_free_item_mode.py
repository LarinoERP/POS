"""Replace the "Free Cheapest Items (POS)" checkbox with "Mixed Items Free Item (POS)".

The checkbox counted Min Qty as paid + free items; the new field counts Min Qty
as paid items only (buy Min Qty, get Free Qty free), so existing slabs are
reduced by their Free Qty.
"""

import frappe
from frappe.modules.utils import sync_customizations
from frappe.utils import flt

OLD_FIELD = "pos_free_cheapest_item"


def execute():
	if not frappe.db.has_column("Promotional Scheme", OLD_FIELD):
		return

	sync_customizations("pos_next")

	for name in frappe.get_all("Promotional Scheme", filters={OLD_FIELD: 1}, pluck="name"):
		scheme = frappe.get_doc("Promotional Scheme", name)
		if not scheme.get("pos_free_item_mode"):
			scheme.pos_free_item_mode = "Cheapest Item"
			for slab in scheme.product_discount_slabs:
				slab.min_qty = max(flt(slab.min_qty) - flt(slab.free_qty), 1)
			scheme.save(ignore_permissions=True)

	for name in frappe.get_all(
		"Custom Field", filters={"dt": "Promotional Scheme", "fieldname": OLD_FIELD}, pluck="name"
	):
		frappe.delete_doc("Custom Field", name, force=True, ignore_permissions=True)
	frappe.db.sql_ddl(f"alter table `tabPromotional Scheme` drop column `{OLD_FIELD}`")
