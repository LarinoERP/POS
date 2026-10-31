"""Switch POS Offers that used "Replace Cheapest Item" to the cheapest-item-free mode.

remove_pos_offer converted them to same-item free product schemes, which only
count one item at a time. With pos_free_cheapest_item, different eligible items
count together and the cheapest ones become free, as the POS Offer intended:
for every Min Qty + Given Qty items, the cheapest Given Qty are free.
"""

import json

import frappe
from frappe.modules.utils import sync_customizations
from frappe.utils import cint, flt


def execute():
	# Custom fields are synced after patches; the field is needed now
	sync_customizations("pos_next")

	for name in frappe.get_all(
		"File", filters={"file_name": ["like", "pos_offer_backup%.json"]}, pluck="name"
	):
		for offer in json.loads(frappe.get_doc("File", name).get_content()):
			if cint(offer.get("disable")) or offer.get("offer") != "Give Product":
				continue
			if not cint(offer.get("replace_cheapest_item")):
				continue
			if frappe.db.exists("Promotional Scheme", offer["name"]):
				_convert(offer)


def _convert(offer):
	scheme = frappe.get_doc("Promotional Scheme", offer["name"])
	if scheme.get("pos_free_cheapest_item") or len(scheme.product_discount_slabs) != 1:
		return

	free_qty = flt(offer.get("given_qty")) or 1
	scheme.pos_free_cheapest_item = 1
	scheme.mixed_conditions = 0
	scheme.product_discount_slabs[0].update(
		{
			"min_qty": flt(offer.get("min_qty")) + free_qty,
			"free_qty": free_qty,
			"same_item": 1,
			"is_recursive": 0,
			"recurse_for": 0,
		}
	)
	scheme.save(ignore_permissions=True)
