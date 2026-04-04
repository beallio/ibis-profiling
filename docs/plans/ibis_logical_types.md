# Ibis Logical Type Inference System

## Problem Definition
The current `ibis-profiling` tool relies on physical types provided by the Ibis schema. This misses valuable semantic information (e.g., a String column containing UUIDs or URLs). We need a system to infer logical types from physical data using Ibis-native expressions.

## Architecture Overview
The system will follow a graph-based approach similar to `visions` but optimized for Ibis's lazy evaluation.

### Core Components
1. **`LogicalType`**: An abstraction for a semantic type (e.g., `Email`, `URL`, `Integer`).
2. **`TypeGraph`**: A directed graph where nodes are `LogicalType`s and edges represent potential inferences.
3. **`InferenceEngine`**: Executes the inference process by building and running Ibis expressions.

## Core Data Structures
```python
class LogicalType:
    name: str
    physical_type: ibis.DataType
    
    @classmethod
    def contains(cls, expr: ibis.Value) -> ibis.BooleanValue:
        """Returns an Ibis expression that evaluates to True if the column matches this type."""
        ...

class TypeRelation:
    from_type: Type[LogicalType]
    to_type: Type[LogicalType]
    condition: Callable[[ibis.Value], ibis.BooleanValue]
```

## Public Interfaces
```python
class IbisTypeInference:
    def infer_column_type(self, table: ibis.Table, column: str) -> LogicalType:
        ...
```

## Dependency Requirements
- `ibis-framework`
- `networkx` (for graph traversal, if complex)

## Testing Strategy
- **Unit Tests**: Verify `contains` expressions for various types (Email, UUID, etc.).
- **Integration Tests**: Verify full table inference on sample datasets.
- **Performance Tests**: Ensure inference doesn't trigger excessive full-table scans.
