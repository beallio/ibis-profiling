# Plan: Ibis Logical Types Expansion

## Problem Definition
The current logical type system supports a limited set of semantic types (Email, UUID, Categorical). To provide a comprehensive profiling experience, we need to expand this to include common data patterns found in real-world datasets, leveraging Ibis's lazy evaluation for performance.

## Architecture Overview
We will continue using the `LogicalType` abstraction and the `IbisLogicalTypeSystem` batch inference engine. Each new type will define its own Ibis aggregate expressions.

## Phased Approach

### Phase 1: String-Based Pattern Types
- **URL**: Regex-based detection of web addresses.
- **IPAddress**: Regex-based detection of IPv4/IPv6.
- **PhoneNumber**: Regex-based detection of E.164 and common formats.

### Phase 2: Inferred Semantic Types
- **Boolean (Logical)**: Detecting string/integer columns representing truth values (e.g., "yes/no", "1/0").
- **DateTime (Inferred)**: Detecting string columns that follow date/time patterns.

### Phase 3: Numeric Semantic Types
- **Integer (Inferred)**: String columns castable to integers.
- **Decimal (Inferred)**: String columns castable to decimals.
- **Count**: Non-negative integer columns.

### Phase 4: Structural Types
- **Ordinal**: Categorical types with inherent ordering.

### Phase 5: Integration & UI
- CLI parameter exposure (if needed, though inference is generally automatic).
- HTML template updates to display new logical types.
- Documentation updates (README.md, specs).

## Git Strategy
- **Branch**: `feat/logical-type-inference` (Active)
- **Commit Frequency**: Atomic commit per logical type implementation.
- **Prefix**: `feat:`

## Task Decomposition (Type Execution Loop)

For each type $T \in \{URL, IPAddress, Boolean, DateTime, PhoneNumber, Integer, Decimal, Ordinal, Count\}$:
1. **Red**: Write a failing test in `tests/test_logical_types.py`.
2. **Green**: Implement `T(LogicalType)` in `src/ibis_profiling/logical_types.py` and register it in `IbisLogicalTypeSystem`.
3. **Refactor/Validate**: Run lint, type checks, and the specific test.
4. **Commit**: Atomic commit for type $T$.

## Testing Strategy
- Use `ibis.memtable` for fast, reproducible tests.
- Cover positive cases (all values match), negative cases (mixed data), and null handling.

## Phase 6: Stabilization & Scale (Complete)
- **Chunked Inference**: Processed in 5-column batches. Verified stability on 100-column datasets.
- **Physical-Type Fallback**: Implemented `from_native` for all logical types.
- **Performance Benchmarks (100M Rows)**:
    - **100k Threshold**: 39.4s (Baseline)
    - **No Threshold**: 66.6s (+69% latency spike)
    - **Conclusion**: Heuristic-based unique counts are mandatory for large-scale dataset stability.

## Phase 7: Dynamic Threshold Optimization
- **Goal**: Implement a smarter `n_unique_threshold` that balances semantic precision with performance.
- **Logic**: `max(1,000,000, 0.1 * total_rows)`.
- **Rationale**: For smaller datasets, we can afford higher precision. For very large datasets, we scale the threshold to allow meaningful sampling/sketching if implemented later.

## Git Strategy
- **Branch**: `feat/logical-type-inference` (Active)
- **Commit Frequency**: Atomic commit per stabilization fix.
