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

## Performance Benchmarking
- Benchmark the full inference suite against a 10M row dataset to ensure batching prevents linear scaling of latency with the number of types.
