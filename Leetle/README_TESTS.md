# Leetle Testing Suite

This document describes the comprehensive testing suite for Leetle's reference solutions.

## Overview

The testing suite validates that reference implementations for all problems produce correct outputs across all supported languages (Python, JavaScript, and Java).

## Structure

```
tests/
├── reference_solutions/          # Reference implementations
│   ├── python/                   # Python solutions
│   ├── javascript/               # JavaScript solutions
│   └── java/                     # Java solutions
├── conftest.py                   # pytest fixtures and database setup
├── test_problems.py              # pytest test cases
├── test_runner.py                # Standalone test runner
└── __init__.py                   # Python package marker
```

## Running Tests

### Method 1: Custom Test Runner (Recommended)

```bash
# Run all tests
python tests/test_runner.py

# Run specific problem
python tests/test_runner.py --problem two_sum

# Run specific language
python tests/test_runner.py --language python

# Verbose output
python tests/test_runner.py --verbose

# Test one problem in one language
python tests/test_runner.py --problem fizzbuzz --language javascript --verbose
```

### Method 2: pytest

```bash
# Install test dependencies
pip install -r requirements.txt

# Run pytest (requires database setup)
python tests/test_runner.py --pytest
```

## Test Coverage

The testing suite covers:

- **5 Problems**: Two Sum, Palindrome Number, Reverse String, FizzBuzz, Binary Search
- **3 Languages**: Python, JavaScript, Java
- **Multiple Test Cases**: Each problem has 2-3 test cases from the database
- **Execution Validation**: Code execution time and correctness
- **Output Verification**: Exact output matching against expected results

## Reference Solutions

Each problem has reference implementations that demonstrate correct approaches:

### Two Sum (Easy)
- **Input**: Array and target value
- **Output**: Indices of two numbers that sum to target
- **Python**: Hash map approach
- **JavaScript**: Map-based solution
- **Java**: HashMap implementation

### Palindrome Number (Easy)
- **Input**: Integer
- **Output**: "true" if palindrome, "false" otherwise
- **Approach**: String conversion and reversal

### Reverse String (Easy)
- **Input**: Character array
- **Output**: Reversed character array
- **Approach**: Two-pointer in-place reversal

### FizzBuzz (Easy)
- **Input**: Integer n
- **Output**: Array of FizzBuzz strings
- **Approach**: Loop with conditional logic

### Binary Search (Easy)
- **Input**: Sorted array and target
- **Output**: Index of target or -1
- **Approach**: Binary search algorithm

## Adding New Tests

### Adding a New Problem

1. Create problem entry in database or `seed_problems()` in `test_runner.py`
2. Implement reference solutions in all 3 languages in `tests/reference_solutions/`
3. Add problem name to `PROBLEM_NAMES` in both test files
4. Solutions must read from stdin and write to stdout

### Language-Specific Requirements

#### Python Solutions
- Use `sys.stdin.read()` and `print()` for I/O
- Include necessary imports
- Handle different input formats appropriately

#### JavaScript Solutions
- Use `fs.readFileSync(0)` and `console.log()` for I/O
- Require 'fs' module for stdin reading
- Handle JSON parsing for complex inputs

#### Java Solutions
- Class must be named `Main`
- Use `Scanner` for input, `System.out.println()` for output
- Handle array parsing manually (comma-separated values in brackets)

## Expected Output Formats

Solutions must produce output that exactly matches the test case expectations:

- Arrays: `[1,2,3]` or `["a","b","c"]`
- Booleans: `"true"` or `"false"` (lowercase string)
- Numbers: String representation
- No extra whitespace or newlines (except where specified)

## Troubleshooting

### Common Issues

1. **File Not Found**: Ensure all reference solution files exist and are executable
2. **Language Not Installed**: Ensure Python 3, Node.js, and Java are installed
3. **Compilation Errors**: Check Java class names and syntax
4. **Output Format Mismatch**: Verify output exactly matches expected format
5. **Execution Timeout**: Solutions should complete within 30 seconds

### Debug Mode

Use `--verbose` flag with the test runner to see detailed output:

```bash
python tests/test_runner.py --problem two_sum --verbose
```

This will show:
- Individual test case results
- Execution times
- Input/expected/actual output comparisons

## Integration with CI/CD

The test runner returns appropriate exit codes:
- `0`: All tests passed
- `1`: Some tests failed

Use in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: python tests/test_runner.py
  continue-on-error: false
```

## Performance Benchmarks

Typical execution times for reference solutions:
- Simple problems: < 0.1 seconds
- All tests combined: < 5 seconds
- Timeout limit: 30 seconds per test case

## Contributing

When adding new features:
1. Update this documentation
2. Add comprehensive test cases
3. Ensure all language implementations
4. Validate with `--verbose` flag
5. Update CI/CD configurations if needed
