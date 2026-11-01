import json
import os
from datetime import datetime

DATA_FILE = "salon_data.json"

DEFAULT_DATA = {
    "products": [
        {"id": 1, "name": "Shampoo", "price": 12.00, "stock": 20},
        {"id": 2, "name": "Conditioner", "price": 14.00, "stock": 15},
        {"id": 3, "name": "Hair Oil", "price": 10.00, "stock": 12}
    ],
    "services": [
        {"id": 1, "name": "Haircut", "price": 25.00},
        {"id": 2, "name": "Hair Coloring", "price": 65.00},
        {"id": 3, "name": "Manicure", "price": 30.00}
    ],
    "sales": []
}


def load_data():
    """Load salon data, creating a starter dataset on first launch."""
    if not os.path.exists(DATA_FILE):
        return DEFAULT_DATA.copy()
    try:
        with open(DATA_FILE, "r") as data_file:
            data = json.load(data_file)
        data.setdefault("products", [])
        data.setdefault("services", [])
        data.setdefault("sales", [])
        return data
    except (IOError, ValueError):
        print("Could not read the saved data. Starting with the sample data.")
        return DEFAULT_DATA.copy()


def save_data(data):
    with open(DATA_FILE, "w") as data_file:
        json.dump(data, data_file, indent=2)


def money(amount):
    return "₱{:.2f}".format(amount)


def read_number(message, minimum=0):
    while True:
        try:
            value = int(input(message))
            if value < minimum:
                print("Please enter a value of at least {}.".format(minimum))
                continue
            return value
        except ValueError:
            print("Please enter a whole number.")


def list_products(data):
    print("\nPRODUCT INVENTORY")
    if not data["products"]:
        print("No products have been added.")
        return
    print("{:<5} {:<24} {:>10} {:>8}".format("ID", "Product", "Price", "Stock"))
    for product in data["products"]:
        print("{:<5} {:<24} {:>10} {:>8}".format(
            product["id"], product["name"], money(product["price"]), product["stock"]
        ))


def list_services(data):
    print("\nSALON SERVICES")
    if not data["services"]:
        print("No services have been added.")
        return
    print("{:<5} {:<28} {:>10}".format("ID", "Service", "Price"))
    for service in data["services"]:
        print("{:<5} {:<28} {:>10}".format(
            service["id"], service["name"], money(service["price"])
        ))


def find_by_id(items, item_id):
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def checkout(data):
    """Create one sale containing any combination of services and products."""
    cart = []
    product_quantities = {}

    while True:
        print("\n1. Add a service  2. Add a product  3. Finish sale  0. Cancel")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Sale cancelled.")
            return
        if choice == "1":
            list_services(data)
            service_id = read_number("Service ID (0 to go back): ")
            if service_id == 0:
                continue
            service = find_by_id(data["services"], service_id)
            if service is None:
                print("Service not found.")
                continue
            cart.append({"type": "service", "name": service["name"],
                         "quantity": 1, "unit_price": service["price"]})
            print("Added {}.".format(service["name"]))
        elif choice == "2":
            list_products(data)
            product_id = read_number("Product ID (0 to go back): ")
            if product_id == 0:
                continue
            product = find_by_id(data["products"], product_id)
            if product is None:
                print("Product not found.")
                continue
            quantity = read_number("Quantity: ", 1)
            already_in_cart = product_quantities.get(product_id, 0)
            if already_in_cart + quantity > product["stock"]:
                print("Not enough stock. Available: {}.".format(
                    product["stock"] - already_in_cart
                ))
                continue
            product_quantities[product_id] = already_in_cart + quantity
            cart.append({"type": "product", "product_id": product_id,
                         "name": product["name"], "quantity": quantity,
                         "unit_price": product["price"]})
            print("Added {} x {}.".format(quantity, product["name"]))
        elif choice == "3":
            if not cart:
                print("The sale is empty.")
                return
            subtotal = sum(item["quantity"] * item["unit_price"] for item in cart)
            print("\nSALE SUMMARY")
            for item in cart:
                line_total = item["quantity"] * item["unit_price"]
                print("{} x {}  {}".format(
                    item["quantity"], item["name"], money(line_total)
                ))
            print("Total: {}".format(money(subtotal)))
            confirm = input("Complete this sale? (y/n): ").strip().lower()
            if confirm != "y":
                print("Sale not completed.")
                return

            # Deduct product stock only after the sale is confirmed.
            for product_id, quantity in product_quantities.items():
                find_by_id(data["products"], product_id)["stock"] -= quantity
            sale = {
                "id": len(data["sales"]) + 1,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": cart,
                "total": round(subtotal, 2)
            }
            data["sales"].append(sale)
            save_data(data)
            print("Sale #{} completed. Total: {}".format(sale["id"], money(subtotal)))
            return
        else:
            print("Choose 0, 1, 2, or 3.")


def add_stock(data):
    list_products(data)
    product_id = read_number("Product ID (0 to go back): ")
    if product_id == 0:
        return
    product = find_by_id(data["products"], product_id)
    if product is None:
        print("Product not found.")
        return
    quantity = read_number("Quantity to add: ", 1)
    product["stock"] += quantity
    save_data(data)
    print("Updated {} stock: {} units.".format(product["name"], product["stock"]))


def sales_report(data):
    print("\nSALES REPORT")
    if not data["sales"]:
        print("No sales recorded yet.")
        return
    total_revenue = sum(sale["total"] for sale in data["sales"])
    for sale in data["sales"]:
        print("Sale #{} | {} | {}".format(
            sale["id"], sale["date"], money(sale["total"])
        ))
    print("{} sale(s) | Total revenue: {}".format(
        len(data["sales"]), money(total_revenue)
    ))


def main():
    data = load_data()
    while True:
        print("\n=== SALON POS & INVENTORY ===")
        print("1. New sale")
        print("2. View inventory")
        print("3. Add stock")
        print("4. View services")
        print("5. Sales report")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            checkout(data)
        elif choice == "2":
            list_products(data)
        elif choice == "3":
            add_stock(data)
        elif choice == "4":
            list_services(data)
        elif choice == "5":
            sales_report(data)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Please choose one of the listed options.")


if __name__ == "__main__":
    main()
