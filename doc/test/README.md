# Testing Documentation

## Overview

NormPic follows a strict TDD (Test-Driven Development) approach as outlined in [CONTRIBUTE.md](../CONTRIBUTE.md).

## Testing Strategy

### Integration Tests First
- **E2E/Integration tests** surface larger missing or broken pieces
- **Prioritized first** to discover requirements  
- Use complete workflow scenarios to reveal missing implementations

### Unit Tests Second  
- **Unit tests** written when integration tests reveal specific missing pieces
- Focus on individual functions and components
- Use same fixtures as integration tests for consistency

### RED-GREEN-REFACTOR Cycle
1. **RED**: Write failing test
2. **GREEN**: Implement minimal code to pass test
3. **REFACTOR**: Improve implementation if needed

## File Organization

```
test/
├── fixtures.py           # Shared fixtures for all tests
├── integration/          # End-to-end workflow tests
│   └── test_*.py
├── unit/                # Component-specific tests  
│   └── test_*.py
└── conftest.py          # pytest configuration
```

## Documentation

- [Integration Tests](integration-tests.md) - Complex end-to-end test scenarios and workflows
- [Fixtures](fixtures.md) - Available fixtures and usage patterns
- [Patterns](patterns.md) - Integration vs unit test patterns

## Key Principles

### Mocked Filesystem
- **All file interactions** use ephemeral in-memory files
- **No real files** created during testing
- Use `create_photo_with_exif` fixture for synthetic photos

### Fixture Reuse
- **Same fixtures** used by both integration and unit tests
- **Consistent test data** across all test types  
- **Easy to maintain** - update fixture once, affects all tests

### Requirements Discovery
- **Integration tests** define what we actually need
- **Failing tests** guide implementation priorities
- **No over-engineering** - only build what tests require