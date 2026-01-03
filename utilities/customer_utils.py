# utilities/customer_utils.py

# Temporary in-memory store (replace with DB later)
CUSTOMERS = {
    "Ramesh": {"phone": "9876543210", "address": "Hyderabad"},
    "Suresh": {"phone": "9123456789", "address": "Warangal"},
    "Mahesh": {"phone": "9988776655", "address": "Karimnagar"},
}

def get_customer_names():
    return list(CUSTOMERS.keys())

def get_customer(name):
    return CUSTOMERS.get(name)
