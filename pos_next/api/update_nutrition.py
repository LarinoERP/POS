import frappe

def execute():
    """Update existing food items with nutrition data"""
    items = [
        {"item_code": "STARTER001", "item_name": "Spring Rolls", "calories": 195, "protein": 6, "carbohydrates": 22, "fat": 9, "fiber": 3, "sugar": 4, "sodium": 480, "serving_size": "4 pieces", "allergens": "Gluten, Soy", "is_vegetarian": 0},
        {"item_code": "STARTER002", "item_name": "Bruschetta", "calories": 165, "protein": 5, "carbohydrates": 20, "fat": 7, "fiber": 2, "sugar": 3, "sodium": 320, "serving_size": "3 pieces", "allergens": "Gluten", "is_vegetarian": 1},
        {"item_code": "STARTER003", "item_name": "Soup of the Day", "calories": 120, "protein": 4, "carbohydrates": 15, "fat": 5, "fiber": 3, "sugar": 5, "sodium": 590, "serving_size": "1 bowl (350ml)", "allergens": "Dairy", "is_vegetarian": 1},
        {"item_code": "STARTER004", "item_name": "Garlic Bread", "calories": 210, "protein": 5, "carbohydrates": 25, "fat": 10, "fiber": 1, "sugar": 2, "sodium": 410, "serving_size": "2 slices", "allergens": "Gluten, Dairy", "is_vegetarian": 1},
        {"item_code": "STARTER005", "item_name": "Caesar Salad", "calories": 180, "protein": 8, "carbohydrates": 12, "fat": 12, "fiber": 4, "sugar": 3, "sodium": 350, "serving_size": "1 plate", "allergens": "Dairy, Eggs, Fish", "is_vegetarian": 0},
        {"item_code": "MAIN001", "item_name": "Grilled Chicken", "calories": 420, "protein": 42, "carbohydrates": 8, "fat": 24, "fiber": 2, "sugar": 2, "sodium": 520, "serving_size": "1 plate (250g)", "allergens": "", "is_vegetarian": 0},
        {"item_code": "MAIN002", "item_name": "Beef Steak", "calories": 520, "protein": 48, "carbohydrates": 2, "fat": 35, "fiber": 0, "sugar": 1, "sodium": 380, "serving_size": "1 steak (300g)", "allergens": "", "is_vegetarian": 0},
        {"item_code": "MAIN003", "item_name": "Fish & Chips", "calories": 580, "protein": 28, "carbohydrates": 48, "fat": 30, "fiber": 3, "sugar": 3, "sodium": 620, "serving_size": "1 plate", "allergens": "Gluten, Fish", "is_vegetarian": 0},
        {"item_code": "MAIN004", "item_name": "Pasta Carbonara", "calories": 620, "protein": 22, "carbohydrates": 58, "fat": 32, "fiber": 3, "sugar": 4, "sodium": 680, "serving_size": "1 plate", "allergens": "Gluten, Dairy, Eggs", "is_vegetarian": 0},
        {"item_code": "MAIN005", "item_name": "Margherita Pizza", "calories": 540, "protein": 20, "carbohydrates": 55, "fat": 26, "fiber": 4, "sugar": 6, "sodium": 720, "serving_size": "1 pizza (10\")", "allergens": "Gluten, Dairy", "is_vegetarian": 1},
        {"item_code": "MAIN006", "item_name": "Vegetable Curry", "calories": 350, "protein": 10, "carbohydrates": 42, "fat": 16, "fiber": 8, "sugar": 8, "sodium": 540, "serving_size": "1 plate with rice", "allergens": "Nuts", "is_vegetarian": 1},
        {"item_code": "MAIN007", "item_name": "Lamb Chops", "calories": 480, "protein": 40, "carbohydrates": 4, "fat": 32, "fiber": 1, "sugar": 1, "sodium": 350, "serving_size": "4 chops", "allergens": "", "is_vegetarian": 0},
        {"item_code": "DESSERT001", "item_name": "Chocolate Cake", "calories": 420, "protein": 5, "carbohydrates": 52, "fat": 22, "fiber": 3, "sugar": 38, "sodium": 280, "serving_size": "1 slice", "allergens": "Gluten, Dairy, Eggs", "is_vegetarian": 1},
        {"item_code": "DESSERT002", "item_name": "Ice Cream Sundae", "calories": 340, "protein": 5, "carbohydrates": 42, "fat": 18, "fiber": 1, "sugar": 35, "sodium": 120, "serving_size": "1 sundae", "allergens": "Dairy, Nuts", "is_vegetarian": 1},
        {"item_code": "DESSERT003", "item_name": "Cheesecake", "calories": 460, "protein": 7, "carbohydrates": 38, "fat": 32, "fiber": 1, "sugar": 28, "sodium": 310, "serving_size": "1 slice", "allergens": "Gluten, Dairy, Eggs", "is_vegetarian": 1},
        {"item_code": "DESSERT004", "item_name": "Tiramisu", "calories": 380, "protein": 6, "carbohydrates": 30, "fat": 26, "fiber": 0, "sugar": 24, "sodium": 90, "serving_size": "1 portion", "allergens": "Gluten, Dairy, Eggs", "is_vegetarian": 1},
        {"item_code": "DRINK001", "item_name": "Fresh Orange Juice", "calories": 110, "protein": 2, "carbohydrates": 26, "fat": 0, "fiber": 1, "sugar": 22, "sodium": 5, "serving_size": "330ml", "allergens": "", "is_vegetarian": 1},
        {"item_code": "DRINK002", "item_name": "Iced Coffee", "calories": 140, "protein": 3, "carbohydrates": 20, "fat": 5, "fiber": 0, "sugar": 18, "sodium": 60, "serving_size": "350ml", "allergens": "Dairy", "is_vegetarian": 1},
        {"item_code": "DRINK003", "item_name": "Lemonade", "calories": 120, "protein": 0, "carbohydrates": 30, "fat": 0, "fiber": 0, "sugar": 28, "sodium": 15, "serving_size": "330ml", "allergens": "", "is_vegetarian": 1},
        {"item_code": "DRINK004", "item_name": "Mineral Water", "calories": 0, "protein": 0, "carbohydrates": 0, "fat": 0, "fiber": 0, "sugar": 0, "sodium": 10, "serving_size": "500ml", "allergens": "", "is_vegetarian": 1},
    ]

    updated = 0
    for item_data in items:
        if not frappe.db.exists("Item", item_data["item_code"]):
            print(f"  Item not found: {item_data['item_code']}")
            continue

        frappe.db.set_value("Item", item_data["item_code"], {
            "custom_calories": item_data["calories"],
            "custom_protein": item_data["protein"],
            "custom_carbohydrates": item_data["carbohydrates"],
            "custom_fat": item_data["fat"],
            "custom_fiber": item_data["fiber"],
            "custom_sugar": item_data["sugar"],
            "custom_sodium": item_data["sodium"],
            "custom_serving_size": item_data["serving_size"],
            "custom_allergens": item_data.get("allergens", ""),
            "custom_is_vegetarian": item_data.get("is_vegetarian", 0),
            "custom_is_vegan": item_data.get("is_vegan", 0),
        }, update_modified=False)
        updated += 1
        print(f"  Updated nutrition: {item_data['item_name']} ({item_data['calories']}cal)")

    frappe.db.commit()
    print(f"\nUpdated {updated} items with nutrition data")
