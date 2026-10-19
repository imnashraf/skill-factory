# Reference Guide: Invoice Reconciliation

## Expected Fields

### Invoices CSV

- `invoice_number`: Unique invoice identifier from vendor.
- `po_number`: Referenced purchase order number.
- `vendor`: Vendor or supplier name.
- `amount`: Invoiced subtotal or total in dollars.

### Purchase Orders CSV

- `po_number`: Approved purchase order code.
- `vendor`: Vendor name.
- `amount`: Approved line item or PO budget amount.
