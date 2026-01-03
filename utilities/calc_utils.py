def calculate_line_amount(qty, rate, gst):
    line = qty * rate
    tax = line * (gst / 100)
    return line, tax, line + tax


def calculate_totals(items):
    subtotal = 0.0
    total_tax = 0.0

    for item in items:
        line = item["qty"] * item["rate"]
        tax = line * (item["gst"] / 100)
        subtotal += line
        total_tax += tax

    return subtotal, total_tax, subtotal + total_tax
