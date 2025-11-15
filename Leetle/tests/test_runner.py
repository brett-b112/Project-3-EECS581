#!/usr/bin/env python3
"""
Leetle Testing Suite Runner

This script runs comprehensive tests for all reference solutions
in Python, JavaScript, and Java across all problems.

Usage:
    python tests/test_runner.py              # Run all tests
    python tests/test_runner.py --problem fizzbuzz  # Test specific problem
    python tests/test_runner.py --language python   # Test specific language
    python tests/test_runner.py --verbose           # Verbose output
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path
import json
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, db, Problem


class TestRunner:
    """Run comprehensive tests for all reference solutions."""

    SUPPORTED_LANGUAGES = ['python', 'javascript', 'java']
    PROBLEM_NAMES = ['two_sum', 'palindrome_number', 'reverse_string', 'fizzbuzz', 'binary_search']

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}

    def get_problem_file(self, problem_name: str, language: str) -> Path:
        """Get the path to a problem solution file."""
        if language == 'java':
            base_name = f"{problem_name.replace('_', '').title()}.java"
        else:
            lang_ext = {'python': 'py', 'javascript': 'js'}
            base_name = f"{problem_name}.{lang_ext[language]}"

        file_path = Path(__file__).parent / 'reference_solutions' / language / base_name
        return file_path

    def run_code(self, language: str, code_path: Path, input_data: str) -> Tuple[str, float, bool]:
        """Run code in the specified language and return output, execution time, and success."""
        start_time = time.time()
        success = True

        try:
            if language == 'python':
                result = subprocess.run(
                    ['python3', str(code_path)],
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=30
                )
            elif language == 'javascript':
                result = subprocess.run(
                    ['node', str(code_path)],
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=30
                )
            elif language == 'java':
                # Compile first
                compile_result = subprocess.run(
                    ['javac', str(code_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if compile_result.returncode != 0:
                    return f"Compilation Error: {compile_result.stderr.strip()}", time.time() - start_time, False

                # Run if compilation successful
                result = subprocess.run(
                    ['java', '-cp', str(code_path.parent), 'Main'],
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=30
                )

            execution_time = time.time() - start_time
            output = result.stdout.strip()
            if result.returncode != 0:
                success = False
                output += f"\nSTDERR: {result.stderr.strip()}"

            return output, execution_time, success

        except subprocess.TimeoutExpired:
            return "TIMEOUT: Code execution exceeded 30 seconds", time.time() - start_time, False
        except FileNotFoundError:
            return f"ERROR: {language.capitalize()} interpreter not found", time.time() - start_time, False
        except Exception as e:
            return f"ERROR: {str(e)}", time.time() - start_time, False

    def run_all_tests(self, problem_filter: str = None, language_filter: str = None) -> Dict[str, Dict]:
        """Run all tests and return results."""
        # Initialize database
        with app.app_context():
            db.create_all()
            # Seed problems if they don't exist
            if Problem.query.count() == 0:
                self.seed_problems()
                self.print_message("Seeded test problems in database.")

            problems = Problem.query.all()
            problem_map = {p.title.lower().replace(' ', '_'): p for p in problems}

            for problem_name in self.PROBLEM_NAMES:
                if problem_filter and problem_name != problem_filter:
                    continue

                if problem_name not in problem_map:
                    self.print_message(f"WARNING: Problem '{problem_name}' not found in database, skipping...")
                    continue

                problem = problem_map[problem_name]
                self.results[problem_name] = {}

                for language in self.SUPPORTED_LANGUAGES:
                    if language_filter and language != language_filter:
                        continue

                    self.print_message(f"\nTesting {problem_name} in {language}...")
                    self.results[problem_name][language] = self.test_problem_language(problem_name, language, problem)

        return self.results

    def test_problem_language(self, problem_name: str, language: str, problem: Problem) -> Dict:
        """Test a single problem in a single language."""
        solution_file = self.get_problem_file(problem_name, language)
        if not solution_file.exists():
            self.print_message(f"  ❌ Solution file {solution_file} not found")
            return {'status': 'FILE_NOT_FOUND', 'tests': []}

        test_cases = json.loads(problem.test_cases)
        results = []
        all_passed = True

        for i, test_case in enumerate(test_cases):
            input_data = test_case['input']
            expected_output = test_case['output']

            output, exec_time, success = self.run_code(language, solution_file, input_data)

            passed = success and output == expected_output
            if not passed:
                all_passed = False

            test_result = {
                'test_case': i + 1,
                'input': input_data.replace('\n', '\\n'),
                'expected': expected_output,
                'actual': output,
                'exec_time': f"{exec_time:.4f}s",
                'passed': passed
            }
            results.append(test_result)

            status = "✅ PASS" if passed else "❌ FAIL"
            if self.verbose:
                self.print_message(f"  Test {i+1}: {status} ({exec_time:.4f}s)")
                if not passed:
                    self.print_message(f"    Expected: {expected_output}")
                    self.print_message(f"    Got:      {output}")

        status = "ALL_PASS" if all_passed else "SOME_FAIL"
        self.print_message(f"  Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

        return {'status': status, 'tests': results}

    def seed_problems(self):
        """Seed test problems in database."""
        problems_data = [
            {
                'title': 'Two Sum',
                'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                'difficulty': 'Easy',
                'input_example': 'nums = [2, 7, 11, 15], target = 9',
                'output_example': '[0, 1]',
                'hint_text': 'Consider using a hash map to store numbers you\'ve seen and their indices.',
                'full_solution': 'Use a dictionary to store each number and its index. For each number, check if target - number exists in the dictionary.',
                'test_cases': json.dumps([
                    {'input': '[2,7,11,15]\n9', 'output': '[0,1]'},
                    {'input': '[3,3]\n6', 'output': '[0,1]'}
                ])
            },
            {
                'title': 'Palindrome Number',
                'description': 'Given an integer x, return true if x is palindrome integer.',
                'difficulty': 'Easy',
                'input_example': 'x = 121',
                'output_example': 'true',
                'hint_text': 'Convert the number to a string and check if it reads the same forwards and backwards.',
                'full_solution': 'Convert x to string, then compare it with its reverse using string slicing.',
                'test_cases': json.dumps([
                    {'input': '121', 'output': 'true'},
                    {'input': '-121', 'output': 'false'},
                    {'input': '10', 'output': 'false'}
                ])
            },
            {
                'title': 'Reverse String',
                'description': 'Write a function that reverses a string. The input string is given as an array of characters s. You must do this by modifying the input array in-place.',
                'difficulty': 'Easy',
                'input_example': 's = ["h","e","l","l","o"]',
                'output_example': '["o","l","l","e","h"]',
                'hint_text': 'Use two pointers, one at the start and one at the end, swapping characters.',
                'full_solution': 'Initialize left = 0, right = len(s)-1. While left < right, swap s[left] and s[right], increment left, decrement right.',
                'test_cases': json.dumps([
                    {'input': '["h","e","l","l","o"]', 'output': '["o","l","l","e","h"]'},
                    {'input': '["H","a","n","n","a","h"]', 'output': '["h","a","n","n","a","H"]'}
                ])
            },
            {
                'title': 'FizzBuzz',
                'description': 'Given an integer n, return a string array answer (1-indexed) where: answer[i] == "FizzBuzz" if i is divisible by 3 and 5. answer[i] == "Fizz" if i is divisible by 3. answer[i] == "Buzz" if i is divisible by 5. answer[i] == i (as a string) otherwise.',
                'difficulty': 'Easy',
                'input_example': 'n = 3',
                'output_example': '["1","2","Fizz"]',
                'hint_text': 'Loop from 1 to n, check divisibility conditions for each number.',
                'full_solution': 'Initialize empty list. For i in range(1, n+1): if i%15==0 append "FizzBuzz", elif i%3==0 append "Fizz", elif i%5==0 append "Buzz", else append str(i).',
                'test_cases': json.dumps([
                    {'input': '3', 'output': '["1","2","Fizz"]'},
                    {'input': '5', 'output': '["1","2","Fizz","4","Buzz"]'}
                ])
            },
            {
                'title': 'Binary Search',
                'description': 'Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.',
                'difficulty': 'Easy',
                'input_example': 'nums = [-1,0,3,5,9,12], target = 9',
                'output_example': '4',
                'hint_text': 'Use left and right pointers to narrow down the search space.',
                'full_solution': 'Set left=0, right=len(nums)-1. While left <= right, mid = (left+right)//2. If nums[mid] == target return mid, elif nums[mid] < target left=mid+1, else right=mid-1. Return -1.',
                'test_cases': json.dumps([
                    {'input': '[-1,0,3,5,9,12]\n9', 'output': '4'},
                    {'input': '[-1,0,3,5,9,12]\n2', 'output': '-1'}
                ])
            }
        ]

        for problem_data in problems_data:
            problem = Problem(**problem_data)
            db.session.add(problem)
        db.session.commit()

    def print_summary(self):
        """Print test summary."""
        if not self.results:
            return

        total_tests = 0
        passed_tests = 0
        total_problems = len(self.results)
        passed_problems = 0

        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        for problem_name, languages in self.results.items():
            problem_passed = True
            print(f"\n{problem_name.upper()}:")
            for language, result in languages.items():
                if result['status'] == 'ALL_PASS':
                    status = "✅ PASS"
                    passed_tests += len(result['tests'])
                    all_test_passed = all(test['passed'] for test in result['tests'])
                    if all_test_passed:
                        total_tests += len(result['tests'])
                    else:
                        problem_passed = False
                else:
                    status = "❌ FAIL"
                    problem_passed = False
                    total_tests += len(result['tests'])

                print(f"  {language}: {status} ({len(result['tests'])} tests)")

            if problem_passed:
                passed_problems += 1

        print("\n" + "-"*80)
        print("OVERALL RESULTS:")
        print(f"Problems tested: {total_problems}")
        print(f"Problems passed: {passed_problems}")
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")

        if passed_problems == total_problems:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some tests failed. Check individual test results above.")

    def print_message(self, message: str):
        """Print a message."""
        print(message)

    def run_with_pytest(self) -> int:
        """Run tests using pytest and return exit code."""
        cmd = [sys.executable, '-m', 'pytest', str(Path(__file__).parent / 'test_problems.py'), '-v']

        if self.verbose:
            cmd.append('--capture=no')
        else:
            cmd.append('--tb=short')

        result = subprocess.run(cmd)
        return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run Leetle testing suite')
    parser.add_argument('--problem', choices=TestRunner.PROBLEM_NAMES,
                       help='Test only specific problem')
    parser.add_argument('--language', choices=TestRunner.SUPPORTED_LANGUAGES,
                       help='Test only specific language')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--pytest', action='store_true',
                       help='Run using pytest (default is custom runner)')

    args = parser.parse_args()

    runner = TestRunner(verbose=args.verbose)

    if args.pytest:
        print("Running tests with pytest...")
        exit_code = runner.run_with_pytest()
        sys.exit(exit_code)
    else:
        print("Running tests with custom runner...")
        print("="*80)
        print("LEETLE TESTING SUITE")
        print("="*80)

        runner.run_all_tests(problem_filter=args.problem, language_filter=args.language)
        runner.print_summary()

        # Exit with proper code
        all_passed = all(
            all(lang_result['status'] == 'ALL_PASS'
                for lang_result in problem_results.values())
            for problem_results in runner.results.values()
        )
        sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
