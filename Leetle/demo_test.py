#!/usr/bin/env python3
"""
Simple demo script showing how the testing suite works.
This demonstrates testing a reference solution directly.
"""

import subprocess
import sys
from pathlib import Path

def test_solution(language, problem_name, input_data, expected_output):
    """Test a single solution with given input."""
    base_path = Path(__file__).parent / 'tests' / 'reference_solutions'

    if language == 'python':
        ext, cmd = '.py', ['python3']
    elif language == 'javascript':
        ext, cmd = '.js', ['node']
    elif language == 'java':
        # For Java, we need to handle class name
        class_name = problem_name.replace('_', '').title()
        ext, cmd = f'{class_name}.java', ['java', '-cp', str(base_path / language), 'Main']
        # Compile first if needed
        source_file = base_path / language / f'{class_name}.java'
        if source_file.exists():
            compile_result = subprocess.run(['javac', str(source_file)], capture_output=True)
            if compile_result.returncode != 0:
                print(f"❌ Java compilation failed: {compile_result.stderr.decode()}")
                return False, "COMPILE_ERROR"
    else:
        print(f"❌ Unsupported language: {language}")
        return False, "UNSUPPORTED_LANGUAGE"

    solution_file = base_path / language / f'{problem_name}{ext}'

    if not solution_file.exists():
        print(f"❌ Solution file not found: {solution_file}")
        return False, "FILE_NOT_FOUND"

    try:
        cmd = cmd + [str(solution_file)]
        result = subprocess.run(
            cmd,
            input=input_data,
            text=True,
            capture_output=True,
            timeout=10
        )

        output = result.stdout.strip()
        success = result.returncode == 0 and output == expected_output

        return success, output

    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, f"ERROR: {str(e)}"

def main():
    """Demonstrate the testing suite."""

    # Test problems with sample inputs
    test_cases = [
        {
            'problem': 'two_sum',
            'input': '[2,7,11,15]\n9',
            'expected': '[0,1]'
        },
        {
            'problem': 'palindrome_number',
            'input': '121',
            'expected': 'true'
        },
        {
            'problem': 'fizzbuzz',
            'input': '3',
            'expected': '["1","2","Fizz"]'
        },
        {
            'problem': 'binary_search',
            'input': '[-1,0,3,5,9,12]\n9',
            'expected': '4'
        }
    ]

    languages = ['python', 'javascript', 'java']

    print("🚀 Leetle Testing Suite Demo")
    print("=" * 50)

    total_tests = 0
    passed_tests = 0

    for test_case in test_cases:
        problem = test_case['problem']
        print(f"\n📝 Testing {problem.upper()}")
        print("-" * 30)

        for language in languages:
            total_tests += 1
            success, output = test_solution(
                language,
                problem,
                test_case['input'],
                test_case['expected']
            )

            if success:
                passed_tests += 1
                print(f"  ✅ {language}: PASS")
            else:
                print(f"  ❌ {language}: FAIL (got: {output})")

    print("\n" + "=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    print(f"Tests run: {total_tests}")
    print(f"Tests passed: {passed_tests}")
    print(".1f")

    if passed_tests == total_tests:
        print("🎉 ALL DEMO TESTS PASSED!")
    else:
        print("⚠️ Some demo tests failed.")

    print("\n" + "=" * 50)
    print("To run the full testing suite:")
    print("python tests/test_runner.py")
    print("python tests/test_runner.py --verbose")
    print("python tests/test_runner.py --problem two_sum --language python")
    print("=" * 50)

if __name__ == '__main__':
    main()
