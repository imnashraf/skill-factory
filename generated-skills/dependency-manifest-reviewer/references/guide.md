# Reference Guide: Dependency Manifest Reviewer

## Security Rules Evaluated

- `DEP-01` (CRITICAL): Insecure `http://` download endpoint.
- `DEP-02` (HIGH): Mutable VCS repository link missing a specific commit SHA hash.
- `DEP-03` (MEDIUM): Duplicate dependency declaration.
- `DEP-04` (MEDIUM): Completely unpinned package.
- `DEP-05` (LOW): Unbounded version operator (`>=` without `<`) or wildcard (`*`).
