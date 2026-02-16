# Test Suite for ISO Manager Ansible Role

This directory contains comprehensive test suites for the ISO Manager Ansible role.

## Test Structure

### Unit Tests (tests/)

Located in the `tests/` directory:

1. **test_workflows.py** - GitHub Actions workflow validation
   - Validates workflow YAML structure
   - Checks job definitions and dependencies
   - Verifies security best practices (SHA pinning, no hardcoded secrets)
   - Tests reusable workflow patterns
   - 19 test functions

2. **test_metadata.py** - Ansible role metadata validation
   - Validates meta/main.yml structure and Galaxy requirements
   - Tests defaults/main.yml variable definitions
   - Checks vars/main.yml ISO catalog structure
   - Verifies cross-file consistency
   - Tests security practices (no sensitive data, safe paths)
   - 27 test functions

3. **test_lint_configs.py** - Linting and configuration file validation
   - Validates .ansible-lint configuration
   - Tests .yamllint rules
   - Checks .releaserc.yml semantic-release configuration
   - Validates .gitignore patterns
   - Tests sonar-project.properties
   - Checks version consistency across configs
   - 22 test functions

### Integration Tests (molecule/default/tests/)

Located in `molecule/default/tests/`:

1. **test_default.py** - Testinfra integration tests
   - Tests directory creation and permissions
   - Validates ISO file downloads
   - Checks mount point configuration
   - Verifies ISO mounting with correct options
   - Tests security (no world-writable files, no setuid/setgid)
   - Validates Ansible variables and facts
   - Tests idempotency and regression scenarios
   - Tests edge cases
   - 22 test functions

## Running Tests

### Unit Tests

Run all unit tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_metadata.py -v
```

Run tests with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Integration Tests

Run Molecule tests:
```bash
molecule test
```

Run specific scenario:
```bash
molecule test --scenario-name default
```

Run without destroying containers (for debugging):
```bash
molecule converge
molecule verify
```

## Test Categories

### Security Tests
- No hardcoded secrets in workflows
- No world-writable files or directories
- No setuid/setgid files
- Proper file permissions (0644 for files, 0755 for directories)
- Safe default paths (not /tmp, not /)

### Structure Tests
- Required files exist (meta/main.yml, defaults/main.yml, etc.)
- Valid YAML syntax
- Required fields present
- Proper data types

### Best Practices Tests
- GitHub Actions pinned to commit SHAs
- Ubuntu 24.04 runners
- Explicit version specifications
- Proper job dependencies
- Timeout configurations

### Functional Tests
- Directory creation
- ISO downloads
- ISO mounting with correct options (loop, ro, iso9660)
- Variable resolution
- Catalog validation

### Regression Tests
- ISO catalog contains expected entries
- Mount point naming matches ISO names
- Variables are properly defined
- Cross-file consistency

### Edge Cases
- Storage paths not set to dangerous locations
- Empty configurations handled
- Invalid catalog keys rejected
- Large ISO files handled correctly

## Dependencies

Unit tests require:
```bash
pip install pytest pyyaml
```

Integration tests require:
```bash
pip install -r requirements-dev.txt
ansible-galaxy collection install ansible.posix community.docker
```

## Test Coverage

- **68 unit tests** covering configuration files, metadata, and workflows
- **22 integration tests** covering role functionality and security
- **Total: 90 test functions**

## CI/CD Integration

Tests are automatically run in GitHub Actions:
- Unit tests run on all PRs and pushes
- Integration tests run via Molecule workflow
- Coverage reports sent to SonarCloud

## Adding New Tests

When adding new tests:

1. Follow existing naming conventions: `test_<what>_<condition>()`
2. Add clear docstrings describing what is tested
3. Group related tests with section comments
4. Use pytest markers for categorization
5. Keep tests independent and idempotent

## Test Best Practices

- ✅ Tests are independent and can run in any order
- ✅ Tests clean up after themselves (handled by Molecule)
- ✅ Clear assertion messages for failures
- ✅ Tests verify one thing at a time
- ✅ Tests use fixtures for common setup
- ✅ Tests document expected behavior