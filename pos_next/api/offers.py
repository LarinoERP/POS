# Copyright (c) 2025, POS Next and contributors
# For license information, please see license.txt

"""
Offers API - Fetches and manages promotional offers and pricing rules for POS

This module provides a clean API for retrieving promotional offers from both
Promotional Schemes and standalone Pricing Rules.
"""

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

# ============================================================================
# Constants
# ============================================================================


class DiscountType:
	"""Discount type constants"""

	PRICE = "Price"
	PRODUCT = "Product"


class ApplyOn:
	"""Apply on constants"""

	ITEM_CODE = "Item Code"
	ITEM_GROUP = "Item Group"
	BRAND = "Brand"
	TRANSACTION = "Transaction"


class OfferSource:
	"""Offer source constants"""

	PROMOTIONAL_SCHEME = "Promotional Scheme"
	PRICING_RULE = "Pricing Rule"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class OfferEligibility:
	"""Eligibility criteria for an offer"""

	items: list[str]
	item_groups: list[str]
	brands: list[str]


@dataclass
class Offer:
	"""Structured offer data"""

	name: str
	title: str
	description: str
	apply_on: str
	offer: str
	auto: int
	coupon_based: int
	min_qty: float
	max_qty: float
	min_amt: float
	max_amt: float
	discount_type: str | None
	rate: float
	discount_amount: float
	discount_percentage: float
	valid_from: str | None
	valid_upto: str | None
	source: str
	promotional_scheme: str | None
	promotional_scheme_id: str | None
	eligible_items: list[str]
	eligible_item_groups: list[str]
	eligible_brands: list[str]
	# Free item fields for product discounts
	free_item: str | None = None
	free_qty: float = 0
	free_item_uom: str | None = None
	same_item: int = 0  # 1 if free item should be same as purchased item
	is_recursive: int = 0  # 1 if offer applies recursively (e.g., buy 2 get 1 free for every 2)
	recurse_for: float = 0  # Give free item for every N quantity (used when is_recursive=1)
	apply_recursion_over: float = 0  # Qty for which recursion isn't applicable
	one_time_per_customer: int = 0  # 1 if each customer may redeem this offer only once
	free_item_mode: str | None = None  # "Cheapest Item" / "Next Item Added": mixed items count together

	def to_dict(self) -> dict:
		"""Convert to dictionary for API response"""
		return asdict(self)


# ============================================================================
# Database Query Helpers
# ============================================================================


class EligibilityFetcher:
	"""Fetches eligibility criteria for pricing rules/schemes in bulk"""

	@staticmethod
	def fetch_all(parent_names: list[str]) -> dict[str, OfferEligibility]:
		"""
		Fetch all eligibility criteria for given parent names

		Args:
			parent_names: List of pricing rule or scheme names

		Returns:
			Dict mapping parent name to OfferEligibility
		"""
		if not parent_names:
			return {}

		items_map = EligibilityFetcher._fetch_items(parent_names)
		item_groups_map = EligibilityFetcher._fetch_item_groups(parent_names)
		brands_map = EligibilityFetcher._fetch_brands(parent_names)

		# Combine all maps into OfferEligibility objects
		eligibility = {}
		for parent in parent_names:
			eligibility[parent] = OfferEligibility(
				items=items_map.get(parent, []),
				item_groups=item_groups_map.get(parent, []),
				brands=brands_map.get(parent, []),
			)

		return eligibility

	@staticmethod
	def _fetch_items(parent_names: list[str]) -> dict[str, list[str]]:
		"""
		Fetch item codes for given parents, expanding template items to include variants.

		When a pricing rule is created for a template item (has_variants=1), this method
		automatically includes all its variant items in the eligible items list.
		This ensures offers work correctly when variants are added to cart.
		"""
		results = frappe.db.sql(
			"""
			SELECT parent, item_code
			FROM `tabPricing Rule Item Code`
			WHERE parent IN %s
		""",
			[parent_names],
			as_dict=1,
		)

		if not results:
			return {}

		# Collect all unique item codes
		all_item_codes = list({row["item_code"] for row in results})

		# Find which items are templates (have variants)
		template_items = frappe.get_all(
			"Item", filters={"name": ["in", all_item_codes], "has_variants": 1}, pluck="name"
		)

		# Fetch variants for all template items in one query
		variants_map = {}
		if template_items:
			variants = frappe.get_all(
				"Item",
				filters={"variant_of": ["in", template_items], "disabled": 0},
				fields=["name", "variant_of"],
			)
			for variant in variants:
				variants_map.setdefault(variant["variant_of"], []).append(variant["name"])

		# Build items map, expanding templates to include their variants
		items_map = {}
		for row in results:
			parent = row["parent"]
			item_code = row["item_code"]

			items_map.setdefault(parent, []).append(item_code)

			# If this item is a template, also add all its variants
			if item_code in variants_map:
				items_map[parent].extend(variants_map[item_code])

		return items_map

	@staticmethod
	def _fetch_item_groups(parent_names: list[str]) -> dict[str, list[str]]:
		"""Fetch item groups for given parents"""
		results = frappe.db.sql(
			"""
			SELECT parent, item_group
			FROM `tabPricing Rule Item Group`
			WHERE parent IN %s
		""",
			[parent_names],
			as_dict=1,
		)

		groups_map = {}
		for row in results:
			groups_map.setdefault(row["parent"], []).append(row["item_group"])
		return groups_map

	@staticmethod
	def _fetch_brands(parent_names: list[str]) -> dict[str, list[str]]:
		"""Fetch brands for given parents"""
		results = frappe.db.sql(
			"""
			SELECT parent, brand
			FROM `tabPricing Rule Brand`
			WHERE parent IN %s
		""",
			[parent_names],
			as_dict=1,
		)

		brands_map = {}
		for row in results:
			brands_map.setdefault(row["parent"], []).append(row["brand"])
		return brands_map


class SlabFetcher:
	"""Fetches discount slabs for promotional schemes"""

	@staticmethod
	def fetch_price_slabs(scheme_names: list[str]) -> dict[str, dict]:
		"""Fetch first price discount slab for each scheme"""
		if not scheme_names:
			return {}

		results = frappe.db.sql(
			"""
			SELECT
				parent, min_qty, max_qty, min_amount, max_amount,
				rate_or_discount, rate, discount_amount, discount_percentage,
				apply_multiple_pricing_rules
			FROM `tabPromotional Scheme Price Discount`
			WHERE parent IN %s AND disable = 0
			ORDER BY parent, min_amount ASC, min_qty ASC
		""",
			[scheme_names],
			as_dict=1,
		)

		# Take first slab for each parent
		slabs_map = {}
		for slab in results:
			if slab["parent"] not in slabs_map:
				slabs_map[slab["parent"]] = slab

		return slabs_map

	@staticmethod
	def fetch_product_slabs(scheme_names: list[str]) -> dict[str, dict]:
		"""Fetch first product discount slab for each scheme"""
		if not scheme_names:
			return {}

		results = frappe.db.sql(
			"""
			SELECT
				parent, min_qty, max_qty, min_amount, max_amount,
				apply_multiple_pricing_rules,
				free_item, free_qty, free_item_uom, same_item, is_recursive,
				recurse_for, apply_recursion_over
			FROM `tabPromotional Scheme Product Discount`
			WHERE parent IN %s AND disable = 0
			ORDER BY parent, min_amount ASC, min_qty ASC
		""",
			[scheme_names],
			as_dict=1,
		)

		# Take first slab for each parent
		slabs_map = {}
		for slab in results:
			if slab["parent"] not in slabs_map:
				slabs_map[slab["parent"]] = slab

		return slabs_map


# ============================================================================
# Offer Builders
# ============================================================================


class OfferBuilder:
	"""Builds Offer objects from pricing rules and schemes"""

	@staticmethod
	def build_from_scheme_rule(rule: dict, slab: dict, eligibility: OfferEligibility) -> Offer:
		"""Build offer from promotional scheme pricing rule"""

		# Determine if auto-apply
		is_auto = 0
		if not rule.get("coupon_code_based"):
			if not slab.get("apply_multiple_pricing_rules"):
				is_auto = 1

		# Extract eligibility based on apply_on
		eligible_items = []
		eligible_item_groups = []
		eligible_brands = []

		if rule["apply_on"] == ApplyOn.ITEM_CODE:
			eligible_items = eligibility.items
		elif rule["apply_on"] == ApplyOn.ITEM_GROUP:
			eligible_item_groups = eligibility.item_groups
		elif rule["apply_on"] == ApplyOn.BRAND:
			eligible_brands = eligibility.brands

		# Determine offer type
		is_price_discount = rule.get("price_or_product_discount") == DiscountType.PRICE
		free_item_mode = None if is_price_discount else rule.get("free_item_mode")
		min_qty = flt(slab.get("min_qty", 0))
		if free_item_mode:
			# Mixed-item offers need Min Qty paid + Free Qty free items in the cart
			min_qty += flt(slab.get("free_qty", 0))

		return Offer(
			name=rule["name"],
			title=rule.get("title") or rule.get("promotional_scheme") or rule["name"],
			description=rule.get("title") or rule.get("promotional_scheme") or "",
			apply_on=rule["apply_on"],
			offer="Item Price" if is_price_discount else "Give Product",
			auto=is_auto,
			coupon_based=1 if rule.get("coupon_code_based") else 0,
			min_qty=min_qty,
			max_qty=flt(slab.get("max_qty", 0)),
			min_amt=flt(slab.get("min_amount", 0)),
			max_amt=flt(slab.get("max_amount", 0)),
			discount_type=slab.get("rate_or_discount") if is_price_discount else None,
			rate=flt(slab.get("rate", 0)) if is_price_discount else 0,
			discount_amount=flt(slab.get("discount_amount", 0)) if is_price_discount else 0,
			discount_percentage=flt(slab.get("discount_percentage", 0)) if is_price_discount else 0,
			valid_from=rule.get("valid_from"),
			valid_upto=rule.get("valid_upto"),
			source=OfferSource.PROMOTIONAL_SCHEME,
			promotional_scheme=rule.get("promotional_scheme"),
			promotional_scheme_id=rule.get("promotional_scheme_id"),
			eligible_items=eligible_items,
			eligible_item_groups=eligible_item_groups,
			eligible_brands=eligible_brands,
			# Free item fields for product discounts
			free_item=slab.get("free_item") if not is_price_discount else None,
			free_qty=flt(slab.get("free_qty", 0)) if not is_price_discount else 0,
			free_item_uom=slab.get("free_item_uom") if not is_price_discount else None,
			same_item=1 if slab.get("same_item") and not is_price_discount else 0,
			is_recursive=1 if slab.get("is_recursive") and not is_price_discount else 0,
			recurse_for=flt(slab.get("recurse_for", 0)) if not is_price_discount else 0,
			apply_recursion_over=flt(slab.get("apply_recursion_over", 0)) if not is_price_discount else 0,
			one_time_per_customer=1 if rule.get("one_time_per_customer") else 0,
			free_item_mode=free_item_mode,
		)

	@staticmethod
	def build_from_standalone_rule(rule: dict, eligibility: OfferEligibility) -> Offer:
		"""Build offer from standalone pricing rule"""

		# Standalone rules auto-apply unless coupon-based
		is_auto = 0 if rule.get("coupon_code_based") else 1

		# Extract eligibility based on apply_on
		eligible_items = []
		eligible_item_groups = []
		eligible_brands = []

		if rule["apply_on"] == ApplyOn.ITEM_CODE:
			eligible_items = eligibility.items
		elif rule["apply_on"] == ApplyOn.ITEM_GROUP:
			eligible_item_groups = eligibility.item_groups
		elif rule["apply_on"] == ApplyOn.BRAND:
			eligible_brands = eligibility.brands

		return Offer(
			name=rule["name"],
			title=rule.get("title") or rule["name"],
			description=rule.get("title") or f"Pricing Rule: {rule['name']}",
			apply_on=rule["apply_on"],
			offer="Item Price",
			auto=is_auto,
			coupon_based=1 if rule.get("coupon_code_based") else 0,
			min_qty=flt(rule.get("min_qty", 0)),
			max_qty=flt(rule.get("max_qty", 0)),
			min_amt=flt(rule.get("min_amt", 0)),
			max_amt=flt(rule.get("max_amt", 0)),
			discount_type=rule.get("rate_or_discount"),
			rate=flt(rule.get("rate", 0)),
			discount_amount=flt(rule.get("discount_amount", 0)),
			discount_percentage=flt(rule.get("discount_percentage", 0)),
			valid_from=rule.get("valid_from"),
			valid_upto=rule.get("valid_upto"),
			source=OfferSource.PRICING_RULE,
			promotional_scheme=None,
			promotional_scheme_id=None,
			eligible_items=eligible_items,
			eligible_item_groups=eligible_item_groups,
			eligible_brands=eligible_brands,
			one_time_per_customer=1 if rule.get("one_time_per_customer") else 0,
		)


# ============================================================================
# Main API Functions
# ============================================================================


@frappe.whitelist()
def get_offers(pos_profile: str) -> list[dict]:
	"""
	Fetch all auto-applicable offers for the POS profile

	Args:
		pos_profile: POS Profile name

	Returns:
		List of offer dictionaries
	"""
	try:
		profile = frappe.get_doc("POS Profile", pos_profile)

		# Respect POS Profile's ignore_pricing_rule setting
		if profile.ignore_pricing_rule:
			return []

		date = nowdate()

		offers = []

		# Get offers from promotional schemes
		scheme_offers = _get_promotional_scheme_offers(profile.company, date)
		offers.extend(scheme_offers)

		# Get standalone pricing rule offers
		standalone_offers = _get_standalone_pricing_rule_offers(profile.company, date)
		offers.extend(standalone_offers)

		return [offer.to_dict() for offer in offers]

	except Exception as e:
		frappe.log_error(f"Error fetching offers: {e!s}", "Offers API")
		return []


@frappe.whitelist()
def get_customer_one_time_redemptions(customer: str) -> list[str]:
	"""Return the Pricing Rule names a customer has already redeemed once.

	Used by the POS frontend to enforce one-time-per-customer offers OFFLINE:
	the cart caches this list when a customer is selected (while online) so the
	offline offer engine can mirror the server-side gate in ``apply_offers``.
	"""
	if not customer or not frappe.db.table_exists("One Time Customer Offer Usage"):
		return []

	return frappe.get_all(
		"One Time Customer Offer Usage",
		filters={"customer": customer},
		pluck="pricing_rule",
	)


def _get_promotional_scheme_offers(company: str, date: str) -> list[Offer]:
	"""Fetch offers from promotional schemes"""

	# Fetch pricing rules linked to promotional schemes
	pricing_rules = frappe.db.sql(
		"""
		SELECT
			name, title, apply_on, selling, promotional_scheme,
			promotional_scheme_id, coupon_code_based, one_time_per_customer,
			price_or_product_discount, priority, valid_from, valid_upto
		FROM `tabPricing Rule`
		WHERE
			disable = 0
			AND selling = 1
			AND promotional_scheme IS NOT NULL
			AND company = %(company)s
			AND (valid_from IS NULL OR valid_from <= %(date)s)
			AND (valid_upto IS NULL OR valid_upto >= %(date)s)
		ORDER BY priority DESC, name
	""",
		{"company": company, "date": date},
		as_dict=1,
	)

	if not pricing_rules:
		return []

	free_item_modes = get_free_item_mode_schemes()
	for rule in pricing_rules:
		rule["free_item_mode"] = free_item_modes.get(rule["promotional_scheme"])

	# Get unique scheme names
	scheme_names = list({rule["promotional_scheme"] for rule in pricing_rules})

	# Fetch all slabs and eligibility in batch
	price_slabs = SlabFetcher.fetch_price_slabs(scheme_names)
	product_slabs = SlabFetcher.fetch_product_slabs(scheme_names)
	eligibility_map = EligibilityFetcher.fetch_all(scheme_names)

	# Build offers
	offers = []
	for rule in pricing_rules:
		scheme_name = rule["promotional_scheme"]

		# Get appropriate slab
		if rule.get("price_or_product_discount") == DiscountType.PRICE:
			slab = price_slabs.get(scheme_name)
		else:
			slab = product_slabs.get(scheme_name)

		if not slab:
			continue

		eligibility = eligibility_map.get(scheme_name, OfferEligibility([], [], []))
		offer = OfferBuilder.build_from_scheme_rule(rule, slab, eligibility)
		offers.append(offer)

	return offers


def _get_standalone_pricing_rule_offers(company: str, date: str) -> list[Offer]:
	"""Fetch offers from standalone pricing rules"""

	# Fetch standalone pricing rules (not linked to schemes)
	pricing_rules = frappe.db.sql(
		"""
		SELECT
			name, title, apply_on, selling,
			coupon_code_based, one_time_per_customer, price_or_product_discount,
			rate_or_discount, rate, discount_amount, discount_percentage,
			min_qty, max_qty, min_amt, max_amt,
			priority, valid_from, valid_upto
		FROM `tabPricing Rule`
		WHERE
			disable = 0
			AND selling = 1
			AND promotional_scheme IS NULL
			AND company = %(company)s
			AND (valid_from IS NULL OR valid_from <= %(date)s)
			AND (valid_upto IS NULL OR valid_upto >= %(date)s)
			AND price_or_product_discount = %(discount_type)s
		ORDER BY priority DESC, name
	""",
		{"company": company, "date": date, "discount_type": DiscountType.PRICE},
		as_dict=1,
	)

	if not pricing_rules:
		return []

	# Get rule names
	rule_names = [rule["name"] for rule in pricing_rules]

	# Fetch eligibility in batch
	eligibility_map = EligibilityFetcher.fetch_all(rule_names)

	# Build offers
	offers = []
	for rule in pricing_rules:
		eligibility = eligibility_map.get(rule["name"], OfferEligibility([], [], []))
		offer = OfferBuilder.build_from_standalone_rule(rule, eligibility)
		offers.append(offer)

	return offers


# ============================================================================
# Mixed-Item Free Offers
# ============================================================================
#
# ERPNext product discounts count each item separately, and with mixed
# conditions they need a fixed free item, so "buy any 2 pizzas, get the 3rd
# free" across different pizzas cannot be expressed. Promotional Schemes with
# pos_free_item_mode are therefore kept out of the ERPNext engine and
# evaluated here: for every Min Qty + Free Qty eligible units in the cart,
# Free Qty units get a 100% discount.


class FreeItemMode:
	"""pos_free_item_mode options"""

	CHEAPEST = "Cheapest Item"
	NEXT_ADDED = "Next Item Added"


def get_free_item_mode_schemes() -> dict[str, str]:
	"""Map active Promotional Schemes using a mixed-item free mode to that mode."""
	if not frappe.db.has_column("Promotional Scheme", "pos_free_item_mode"):
		return {}
	return dict(
		frappe.get_all(
			"Promotional Scheme",
			filters={"pos_free_item_mode": ["is", "set"], "disable": 0},
			fields=["name", "pos_free_item_mode"],
			as_list=True,
		)
	)


def apply_mixed_free_item_offers(invoice: dict, result: dict, selected_offer_names: set[str]) -> dict:
	"""Discount the free units of each mixed-item free rule.

	Args:
		invoice: Invoice payload sent by the POS
		result: Response from the ERPNext pricing engine pass (modified in place)
		selected_offer_names: Pricing Rule names selected in the POS (empty = all)

	Returns:
		The updated result
	"""
	items = result.get("items") or []
	if not items or not invoice.get("pos_profile"):
		return result

	modes = get_free_item_mode_schemes()
	if not modes:
		return result

	profile = frappe.get_cached_doc("POS Profile", invoice.get("pos_profile"))
	if profile.ignore_pricing_rule:
		return result

	date = getdate(invoice.get("posting_date") or nowdate())
	rules = [
		rule
		for rule in frappe.get_all(
			"Pricing Rule",
			filters={
				"promotional_scheme": ["in", list(modes)],
				"price_or_product_discount": DiscountType.PRODUCT,
				"disable": 0,
				"selling": 1,
				"coupon_code_based": 0,
				"company": profile.company,
			},
			fields=[
				"name",
				"promotional_scheme",
				"apply_on",
				"min_qty",
				"free_qty",
				"warehouse",
				"valid_from",
				"valid_upto",
				"applicable_for",
				"customer",
				"customer_group",
				"territory",
			],
			order_by="priority desc, name",
		)
		if (not selected_offer_names or rule.name in selected_offer_names)
		and (not rule.valid_from or getdate(rule.valid_from) <= date)
		and (not rule.valid_upto or getdate(rule.valid_upto) >= date)
		and _matches_party(rule, invoice)
	]
	if not rules:
		return result

	item_codes = list({item.get("item_code") for item in items if item.get("item_code")})
	item_details = {
		row.name: row
		for row in frappe.get_all(
			"Item", filters={"name": ["in", item_codes]}, fields=["name", "item_group", "brand"]
		)
	}

	# Prices from the ERPNext pass were reset; anything sent by the POS is stale
	reset_discounts = "applied_pricing_rules" not in result
	applied_rules = set(result.get("applied_pricing_rules") or [])

	for rule in rules:
		buy_qty = int(flt(rule.min_qty))
		free_qty = int(flt(rule.free_qty))
		if buy_qty <= 0 or free_qty <= 0:
			continue

		matches = _get_rule_matcher(rule)
		warehouses = _get_rule_warehouses(rule)
		eligible = [
			item
			for item in items
			if not item.get("is_free_item")
			and flt(item.get("qty")) > 0
			and flt(item.get("price_list_rate") or item.get("rate")) > 0
			and matches(item_details.get(item.get("item_code")))
			and (not warehouses or (item.get("warehouse") or profile.warehouse) in warehouses)
		]

		free_by_item = _get_free_units(eligible, buy_qty, free_qty, modes[rule.promotional_scheme])
		if not free_by_item:
			continue

		for index, item in enumerate(eligible):
			rate = flt(item.get("price_list_rate") or item.get("rate"))
			qty = flt(item.get("qty"))
			discount = 0 if reset_discounts else flt(item.get("discount_amount"))
			discount = min(discount + free_by_item.get(index, 0) * rate, rate * qty)

			item["price_list_rate"] = rate
			item["discount_amount"] = discount
			item["discount_percentage"] = discount / (rate * qty) * 100
			# Tag every eligible line so the POS clears stale discounts on lines
			# that are no longer free
			rule_names = [r for r in str(item.get("pricing_rules") or "").split(",") if r]
			item["pricing_rules"] = ",".join([*rule_names, rule.name])

		applied_rules.add(rule.name)

	result["applied_pricing_rules"] = sorted(applied_rules)
	return result


def _get_free_units(eligible: list[dict], buy_qty: int, free_qty: int, mode: str) -> dict[int, int]:
	"""Return {index in eligible: free units} for "buy buy_qty, get free_qty free"."""
	# One entry per unit, in cart order
	units = [
		(flt(item.get("price_list_rate") or item.get("rate")), index)
		for index, item in enumerate(eligible)
		for _ in range(int(flt(item.get("qty"))))
	]
	group_size = buy_qty + free_qty
	groups = len(units) // group_size

	if mode == FreeItemMode.NEXT_ADDED:
		# The last free_qty units of every complete group
		free_units = [
			units[group * group_size + offset]
			for group in range(groups)
			for offset in range(buy_qty, group_size)
		]
	else:
		free_units = sorted(units)[: groups * free_qty]

	free_by_item = {}
	for _rate, index in free_units:
		free_by_item[index] = free_by_item.get(index, 0) + 1
	return free_by_item


def _matches_party(rule, invoice: dict) -> bool:
	"""Check the rule's Applicable For condition (Customer / Customer Group / Territory)."""
	if not rule.applicable_for:
		return True

	field = frappe.scrub(rule.applicable_for)
	if field not in ("customer", "customer_group", "territory"):
		return False

	value = invoice.get(field)
	if not value and invoice.get("customer"):
		value = frappe.get_cached_value("Customer", invoice.get("customer"), field)
	return value == rule.get(field)


def _get_rule_matcher(rule):
	"""Return a function telling whether an Item (name, item_group, brand) is eligible."""
	if rule.apply_on == ApplyOn.ITEM_CODE:
		item_codes = set(
			frappe.get_all("Pricing Rule Item Code", filters={"parent": rule.name}, pluck="item_code")
		)
		return lambda item: bool(item) and item.name in item_codes

	if rule.apply_on == ApplyOn.ITEM_GROUP:
		groups = set()
		for group in frappe.get_all(
			"Pricing Rule Item Group", filters={"parent": rule.name}, pluck="item_group"
		):
			groups.add(group)
			groups.update(frappe.db.get_descendants("Item Group", group) or [])
		return lambda item: bool(item) and item.item_group in groups

	if rule.apply_on == ApplyOn.BRAND:
		brands = set(frappe.get_all("Pricing Rule Brand", filters={"parent": rule.name}, pluck="brand"))
		return lambda item: bool(item) and item.brand in brands

	return lambda item: bool(item)


def _get_rule_warehouses(rule) -> set[str]:
	"""The rule's warehouse and its children (empty = any warehouse)."""
	if not rule.warehouse:
		return set()
	return {rule.warehouse, *(frappe.db.get_descendants("Warehouse", rule.warehouse) or [])}


# ============================================================================
# Coupon Functions
# ============================================================================


@frappe.whitelist()
def get_active_coupons(customer: str, company: str) -> list[dict]:
	"""Get active gift card coupons for a customer"""
	if not frappe.db.table_exists("POS Coupon"):
		return []

	coupons = frappe.get_all(
		"POS Coupon",
		filters={
			"company": company,
			"coupon_type": "Gift Card",
			"customer": customer,
			"used": 0,
		},
		fields=["name", "coupon_code", "coupon_name", "valid_from", "valid_upto"],
	)

	return coupons


@frappe.whitelist()
def validate_coupon(coupon_code: str, customer: str, company: str) -> dict:
	"""Validate a coupon code and return its details"""
	if not frappe.db.table_exists("POS Coupon"):
		return {"valid": False, "message": _("Coupons are not enabled")}

	date = getdate()

	# Fetch coupon with case-insensitive code matching
	# Note: coupon_code field is unique, so we can fetch directly
	coupon = frappe.db.get_value(
		"POS Coupon", {"coupon_code": coupon_code, "company": company}, ["*"], as_dict=1
	)

	if not coupon:
		return {"valid": False, "message": _("Invalid coupon code")}

	if coupon.disabled:
		return {"valid": False, "message": _("This coupon is disabled")}

	# Check usage limits
	if coupon.coupon_type == "Gift Card":
		if coupon.used:
			return {"valid": False, "message": _("This gift card has already been used")}
	else:
		# Promotional coupons
		if coupon.maximum_use > 0 and coupon.used >= coupon.maximum_use:
			return {"valid": False, "message": _("This coupon has reached its usage limit")}

	# Check validity dates
	if coupon.valid_from and coupon.valid_from > date:
		return {"valid": False, "message": _("This coupon is not yet valid")}

	if coupon.valid_upto and coupon.valid_upto < date:
		return {"valid": False, "message": _("This coupon has expired")}

	# Check customer restriction
	if coupon.customer and coupon.customer != customer:
		return {"valid": False, "message": _("This coupon is not valid for this customer")}

	return {"valid": True, "coupon": coupon}
