# Reference Guide: Test Inventory Analyzer

## Analysis Rules

- Matches all Python files ending in `test_*.py` or `*_test.py`.
- Catalogs all functions starting with `test_`.
- Inspects decorators for `@unittest.skip` or `@pytest.mark.skip`.
- Counts explicit `assert` statements and `self.assert*` calls.
