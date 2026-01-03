# utilities/item_utils.py

ITEMS = {
    "Cement": {
        "desc": "UltraTech Cement 50kg",
        "unit": "Bag",
        "price": 420.0,
        "hamali": 20.0
    },
    "TMT Rod": {
        "desc": "TMT Steel Rod",
        "unit": "Kg",
        "price": 62.0,
        "hamali": 5.0
    }
}

def get_item_names():
    return list(ITEMS.keys())

def get_item(name):
    return ITEMS.get(name)
