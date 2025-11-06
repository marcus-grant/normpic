# Data Models Architecture

## Overview

NormPic uses a clean separation between data models and serialization logic, following dataclass patterns for type safety and JSON Schema validation for interoperability.

## Architecture Decisions

### Dataclass-First Design
- **Models**: Pure dataclasses in `lib/model/` with no serialization logic
- **Serializers**: Separate layer in `lib/serializer/` handles JSON operations
- **Benefits**: Clean separation of concerns, easy testing, type safety

### TDD Implementation Approach
1. **RED**: Write failing unit tests first
2. **GREEN**: Implement minimal code to pass tests  
3. **REFACTOR**: Clean up implementation
4. **Result**: 20 comprehensive unit tests covering all scenarios

### Model Structure

#### Pic Dataclass
```python
@dataclass
class Pic:
    # Required fields
    source_path: str
    dest_path: str  
    hash: str
    size_bytes: int
    
    # Optional fields
    timestamp: Optional[datetime] = None
    timestamp_source: Optional[str] = None
    camera: Optional[str] = None
    gps: Optional[Dict[str, float]] = None
    errors: List[str] = field(default_factory=list)
```

#### Manifest Dataclass
```python
@dataclass
class Manifest:
    # Required fields
    version: str
    collection_name: str
    generated_at: datetime
    pics: List[Pic]
    
    # Optional fields
    collection_description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
```

#### Config Dataclass
```python
@dataclass
class Config:
    collection_name: str
    collection_description: Optional[str] = None
    timestamp_offset_hours: int = 0
    force_reprocess: bool = False
```

## Serialization Layer

### ManifestSerializer
- **Location**: `lib/serializer/manifest.py`
- **Methods**: `serialize()`, `deserialize()`, `validate()`
- **Features**: JSON Schema validation, round-trip serialization, error handling

### Key Features
- **Schema Validation**: Automatic validation during deserialization
- **Type Conversion**: Handles datetime ↔ ISO string conversion
- **Error Handling**: Clear validation errors with schema violations
- **Round-trip Safety**: serialize → deserialize preserves all data

## Testing Strategy

### Unit Test Coverage
- **Schema Tests**: 7 tests validating JSON Schema definitions
- **Model Tests**: 7 tests covering dataclass creation and serialization
- **Serializer Tests**: 6 tests for JSON operations and validation

### Test Structure
```
test/unit/
├── test_schema.py      # Schema validation tests
├── test_models.py      # Dataclass behavior tests
└── test_serializer.py  # JSON serialization tests
```

## Design Benefits

1. **Type Safety**: Dataclasses provide IDE support and runtime type checking
2. **Separation of Concerns**: Models focus on data, serializers handle format
3. **Testability**: Each layer tested independently
4. **Extensibility**: Easy to add new serialization formats (YAML, TOML)
5. **Schema Evolution**: Versioned schemas enable backward compatibility

## Integration Points

- **Schema Validation**: Models validated against `schema_v0.py` definitions
- **JSON Conversion**: `to_dict()` methods prepare data for serialization
- **Error Handling**: Schema violations caught at serialization boundaries
- **Future Migration**: Schema versioning enables manifest format evolution