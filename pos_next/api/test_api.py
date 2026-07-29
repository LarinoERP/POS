import frappe

def execute():
    """Test the actual get_items API to see what is_combo_meal values come back"""
    profiles = frappe.get_all("POS Profile", filters={"disabled": 0}, limit=1, pluck="name")
    if not profiles:
        print("No POS Profile found")
        return

    profile = profiles[0]
    print(f"Using POS Profile: {profile}")

    # Test get_items
    from pos_next.api.items import get_items
    items = get_items(profile, search_term=None, item_group=None, start=0, limit=50)
    print(f"\nget_items returned: {len(items)} items")

    combo_count = sum(1 for i in items if i.get("is_combo_meal"))
    print(f"Items with is_combo_meal=1: {combo_count}")

    for i in items[:5]:
        print(f"  {i.get('item_code')}: combo={i.get('is_combo_meal')}, cal={i.get('calories')}")
