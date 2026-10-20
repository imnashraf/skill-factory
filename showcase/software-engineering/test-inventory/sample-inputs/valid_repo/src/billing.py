"""Billing processing module."""

def calculate_invoice_total(subtotal: float, tax_rate: float) -> float:
    return subtotal * (1.0 + tax_rate)
