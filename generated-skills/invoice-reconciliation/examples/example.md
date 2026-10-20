# Example Reconciliation Run

## Command

```bash
python3 scripts/main.py examples/invoices.csv examples/purchase_orders.csv
```

## Sample Output

The tool parses both files, matches items, and prints a markdown report detailing full matches, variances, and missing POs.
