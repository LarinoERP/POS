"""Remove the legacy POS Offer doctype.

POS Offer (inherited from POS Awesome) is never read by POS Next: the POS only
applies ERPNext Promotional Schemes / Pricing Rules and POS Coupons. Offers saved
as POS Offer therefore silently never applied.

Before dropping the doctypes, active offers are converted to their working
equivalent and every POS Offer record is backed up as a private JSON file.
"""

import json
import re

import frappe
from frappe.utils import cint, flt

LEGACY_DOCTYPES = ("POS Coupon Detail", "POS Offer Detail", "POS Offer")


def execute():
	if not frappe.db.exists("DocType", "POS Offer"):
		_delete_legacy_doctypes()
		return

	offers = frappe.get_all("POS Offer", fields=["*"], order_by="creation")
	if offers:
		_backup(offers)

	for offer in offers:
		if cint(offer.disable):
			continue
		try:
			_convert(offer)
		except Exception:
			frappe.log_error(
				title=f"POS Offer migration failed: {offer.name}", message=frappe.get_traceback()
			)

	_delete_legacy_doctypes()


def _backup(offers):
	frappe.get_doc(
		{
			"doctype": "File",
			"file_name": "pos_offer_backup.json",
			"is_private": 1,
			"content": json.dumps(offers, indent=1, default=str, ensure_ascii=False),
		}
	).insert(ignore_permissions=True)


def _convert(offer):
	if offer.offer == "Grand Total":
		_convert_to_coupon(offer)
	elif offer.offer in ("Item Price", "Give Product"):
		_convert_to_promotional_scheme(offer)
	else:
		_skip(offer, f"offer type '{offer.offer}' has no POS Next equivalent")


def _convert_to_coupon(offer):
	"""Manual invoice-level discounts become promotional POS Coupons."""
	if frappe.db.exists("POS Coupon", offer.name):
		return

	discount_type = {"Discount Percentage": "Percentage", "Discount Amount": "Amount"}.get(
		offer.discount_type
	)
	if not discount_type:
		_skip(offer, f"discount type '{offer.discount_type}' is not supported by POS Coupon")
		return

	coupon_code = re.sub(r"[^A-Z0-9]", "", offer.name.upper()) or None
	if coupon_code and frappe.db.exists("POS Coupon", {"coupon_code": coupon_code}):
		coupon_code = None

	frappe.get_doc(
		{
			"doctype": "POS Coupon",
			"coupon_name": offer.name,
			"coupon_code": coupon_code,
			"coupon_type": "Promotional",
			"company": offer.company,
			"discount_type": discount_type,
			"discount_percentage": flt(offer.discount_percentage) if discount_type == "Percentage" else None,
			"discount_amount": flt(offer.discount_amount) if discount_type == "Amount" else None,
			"min_amount": flt(offer.min_amt) or None,
			"apply_on": "Grand Total",
			"valid_from": offer.valid_from,
			"valid_upto": offer.valid_upto,
			"description": offer.description,
		}
	).insert(ignore_permissions=True)


def _convert_to_promotional_scheme(offer):
	if frappe.db.exists("Promotional Scheme", offer.name):
		return

	if cint(offer.coupon_based):
		_skip(offer, "coupon-based item offers must be recreated as a coupon-based Promotional Scheme")
		return
	if not cint(offer.auto):
		_skip(offer, "manual item offers would become automatic as a Promotional Scheme")
		return

	scheme = frappe.new_doc("Promotional Scheme")
	scheme.update(
		{
			"__newname": offer.name,
			"apply_on": offer.apply_on,
			"selling": 1,
			"company": offer.company,
			"currency": frappe.get_cached_value("Company", offer.company, "default_currency"),
			"valid_from": offer.valid_from,
			"valid_upto": offer.valid_upto,
			"pos_only": 1,
		}
	)

	criteria = {
		"Item Code": ("items", "item_code", offer.item),
		"Item Group": ("item_groups", "item_group", offer.item_group),
		"Brand": ("brands", "brand", offer.brand),
	}.get(offer.apply_on)
	if criteria:
		table, field, value = criteria
		if not value:
			_skip(offer, f"no {field} set for apply on '{offer.apply_on}'")
			return
		scheme.append(table, {field: value})
	elif offer.apply_on != "Transaction":
		_skip(offer, f"apply on '{offer.apply_on}' is not supported")
		return

	slab = {
		"rule_description": offer.description or offer.title or offer.name,
		"min_qty": flt(offer.min_qty),
		"max_qty": flt(offer.max_qty),
		"min_amount": flt(offer.min_amt),
		"max_amount": flt(offer.max_amt),
		"warehouse": _get_warehouse(offer),
	}

	if offer.offer == "Item Price":
		slab.update(
			{
				"rate_or_discount": offer.discount_type,
				"rate": flt(offer.rate),
				"discount_percentage": flt(offer.discount_percentage),
				"discount_amount": flt(offer.discount_amount),
			}
		)
		scheme.append("price_discount_slabs", slab)
	else:
		if offer.discount_type != "Discount Percentage" or flt(offer.discount_percentage) != 100:
			_skip(offer, "only fully free (100%) give-product offers can be converted")
			return
		if offer.apply_type == "Item Code" and offer.apply_item_code:
			slab["free_item"] = offer.apply_item_code
		else:
			slab["same_item"] = 1
		# "Buy N get M free" repeats for every N bought
		buy_qty = flt(offer.min_qty) or 1
		slab.update(
			{
				"min_qty": buy_qty,
				"free_qty": flt(offer.given_qty) or 1,
				"is_recursive": 1,
				"recurse_for": buy_qty,
			}
		)
		scheme.append("product_discount_slabs", slab)

	scheme.insert(ignore_permissions=True)


def _get_warehouse(offer):
	if offer.warehouse:
		return offer.warehouse
	if offer.pos_profile:
		return frappe.db.get_value("POS Profile", offer.pos_profile, "warehouse")


def _skip(offer, reason):
	frappe.log_error(
		title=f"POS Offer not migrated: {offer.name}",
		message=f"{reason}. Recreate it manually; the original is in pos_offer_backup.json.",
	)


def _delete_legacy_doctypes():
	for doctype in ("Workspace Link", "Workspace Shortcut"):
		frappe.db.delete(doctype, {"link_to": "POS Offer"})
	frappe.db.delete("Property Setter", {"doc_type": ["in", LEGACY_DOCTYPES]})

	for doctype in LEGACY_DOCTYPES:
		if frappe.db.exists("DocType", doctype):
			frappe.delete_doc("DocType", doctype, force=True, ignore_permissions=True)
		frappe.db.sql_ddl(f"drop table if exists `tab{doctype}`")
