"""
Create mock restaurant data for testing.
Run with: bench --site test.local execute pos_next.api.create_mock_restaurant_data.execute
"""

import frappe


def execute():
	frappe.only_for("System Manager")

	floors_data = [
		{"floor_name": "Main Hall", "floor_width": 1200, "floor_height": 800},
		{"floor_name": "Patio", "floor_width": 1000, "floor_height": 600},
	]

	floors = {}
	for fd in floors_data:
		if frappe.db.exists("Restaurant Floor", {"floor_name": fd["floor_name"]}):
			floors[fd["floor_name"]] = frappe.db.get_value(
				"Restaurant Floor", {"floor_name": fd["floor_name"]}, "name"
			)
			continue
		doc = frappe.new_doc("Restaurant Floor")
		doc.update(fd)
		doc.insert(ignore_permissions=True)
		floors[fd["floor_name"]] = doc.name
		print(f"  Created floor: {doc.name} ({fd['floor_name']})")

	tables_data = [
		{"table_name": "T1", "table_number": "1", "capacity": 2, "section": "Window", "shape": "Square", "floor": "Main Hall", "x_position": 50, "y_position": 50, "width": 80, "height": 80, "status": "Available"},
		{"table_name": "T2", "table_number": "2", "capacity": 2, "section": "Window", "shape": "Square", "floor": "Main Hall", "x_position": 180, "y_position": 50, "width": 80, "height": 80, "status": "Occupied"},
		{"table_name": "T3", "table_number": "3", "capacity": 4, "section": "Center", "shape": "Square", "floor": "Main Hall", "x_position": 50, "y_position": 200, "width": 100, "height": 100, "status": "Available"},
		{"table_name": "T4", "table_number": "4", "capacity": 4, "section": "Center", "shape": "Rectangle", "floor": "Main Hall", "x_position": 200, "y_position": 200, "width": 140, "height": 100, "status": "Occupied"},
		{"table_name": "T5", "table_number": "5", "capacity": 6, "section": "Center", "shape": "Rectangle", "floor": "Main Hall", "x_position": 400, "y_position": 200, "width": 180, "height": 100, "status": "Reserved"},
		{"table_name": "T6", "table_number": "6", "capacity": 4, "section": "Center", "shape": "Square", "floor": "Main Hall", "x_position": 50, "y_position": 400, "width": 100, "height": 100, "status": "Available"},
		{"table_name": "T7", "table_number": "7", "capacity": 4, "section": "Center", "shape": "Square", "floor": "Main Hall", "x_position": 200, "y_position": 400, "width": 100, "height": 100, "status": "Available"},
		{"table_name": "T8", "table_number": "8", "capacity": 8, "section": "Back", "shape": "Round", "floor": "Main Hall", "x_position": 400, "y_position": 400, "width": 120, "height": 120, "status": "Available"},
		{"table_name": "T9", "table_number": "9", "capacity": 4, "section": "Back", "shape": "Rectangle", "floor": "Main Hall", "x_position": 600, "y_position": 50, "width": 140, "height": 90, "status": "Maintenance"},
		{"table_name": "T10", "table_number": "10", "capacity": 4, "section": "Back", "shape": "Rectangle", "floor": "Main Hall", "x_position": 600, "y_position": 200, "width": 140, "height": 90, "status": "Available"},

		{"table_name": "P1", "table_number": "11", "capacity": 2, "section": "Garden", "shape": "Round", "floor": "Patio", "x_position": 50, "y_position": 50, "width": 80, "height": 80, "status": "Available"},
		{"table_name": "P2", "table_number": "12", "capacity": 4, "section": "Garden", "shape": "Square", "floor": "Patio", "x_position": 200, "y_position": 50, "width": 100, "height": 100, "status": "Occupied"},
		{"table_name": "P3", "table_number": "13", "capacity": 6, "section": "Garden", "shape": "Rectangle", "floor": "Patio", "x_position": 50, "y_position": 250, "width": 160, "height": 100, "status": "Available"},
		{"table_name": "P4", "table_number": "14", "capacity": 4, "section": "Bar", "shape": "Square", "floor": "Patio", "x_position": 350, "y_position": 50, "width": 100, "height": 100, "status": "Available"},
	]

	table_count = 0
	for td in tables_data:
		existing = frappe.db.exists("Restaurant Table", {"table_name": td["table_name"]})
		if existing:
			continue
		doc = frappe.new_doc("Restaurant Table")
		doc.update(td)
		doc.insert(ignore_permissions=True)
		table_count += 1

	print(f"  Created {table_count} tables")

	stations_data = [
		{"station_name": "Grill Station", "sound_alert": 1, "auto_bump": 0},
		{"station_name": "Cold Station", "sound_alert": 1, "auto_bump": 0},
		{"station_name": "Pastry Station", "sound_alert": 0, "auto_bump": 1},
	]

	station_count = 0
	for sd in stations_data:
		if frappe.db.exists("Kitchen Station", {"station_name": sd["station_name"]}):
			continue
		doc = frappe.new_doc("Kitchen Station")
		doc.update(sd)
		doc.insert(ignore_permissions=True)
		station_count += 1

	print(f"  Created {station_count} kitchen stations")

	courses_data = [
		{"course_name": "Starters", "course_order": 1, "auto_send": 0, "delay_minutes": 0},
		{"course_name": "Main Course", "course_order": 2, "auto_send": 1, "delay_minutes": 5},
		{"course_name": "Desserts", "course_order": 3, "auto_send": 1, "delay_minutes": 10},
	]

	course_count = 0
	for cd in courses_data:
		if frappe.db.exists("Restaurant Course", {"course_name": cd["course_name"]}):
			continue
		doc = frappe.new_doc("Restaurant Course")
		doc.update(cd)
		doc.insert(ignore_permissions=True)
		course_count += 1

	print(f"  Created {course_count} courses")

	combo_data = [
		{"combo_name": "Lunch Deal", "combo_price": 25.00, "is_active": 1},
		{"combo_name": "Family Meal", "combo_price": 60.00, "is_active": 1},
	]

	combo_count = 0
	for ccd in combo_data:
		if frappe.db.exists("Combo Meal", {"combo_name": ccd["combo_name"]}):
			continue
		doc = frappe.new_doc("Combo Meal")
		doc.update(ccd)
		doc.insert(ignore_permissions=True)
		combo_count += 1

	print(f"  Created {combo_count} combo meals")

	pos_profiles = frappe.get_all("POS Profile", filters={"disabled": 0}, limit=1)
	if pos_profiles:
		profile = pos_profiles[0].name
		existing = frappe.db.exists("POS Settings", {"pos_profile": profile})
		if existing:
			doc = frappe.get_doc("POS Settings", existing)
			doc.restaurant_mode = 1
			doc.enable_table_service = 1
			doc.enable_kitchen_display = 1
			doc.enable_courses = 1
			doc.enable_combos = 1
			doc.enable_modifiers = 1
			doc.default_service_time_target = 15
			doc.kitchen_alert_threshold = 30
			doc.save(ignore_permissions=True)
			print(f"  Enabled restaurant mode on POS Settings for: {profile}")
		else:
			doc = frappe.new_doc("POS Settings")
			doc.pos_profile = profile
			doc.enabled = 1
			doc.restaurant_mode = 1
			doc.enable_table_service = 1
			doc.enable_kitchen_display = 1
			doc.enable_courses = 1
			doc.enable_combos = 1
			doc.enable_modifiers = 1
			doc.default_service_time_target = 15
			doc.kitchen_alert_threshold = 30
			doc.insert(ignore_permissions=True)
			print(f"  Created POS Settings with restaurant mode for: {profile}")
	else:
		print("  No active POS Profile found. Please create one first.")

	frappe.db.commit()
	print("\nDone! Restaurant mock data created successfully.")
	print("Reload the POS page to see the restaurant view mode toggle.")
