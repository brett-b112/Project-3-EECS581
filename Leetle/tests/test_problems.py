import pytest
import os
import json
import subprocess
import tempfile
import time
from pathlib import Path


class TestProblems:
    """Test reference solutions for all problems in all languages."""

    SUPPORTED_LANGUAGES = ['python', 'javascript', 'java']
    PROBLEM_NAMES = ['two_sum', 'palindrome_number', 'reverse_string', 'fizzbuzz', 'binary_search']

    def get_problem_file(self, problem_name: str, language: str) -> Path:
        """Get the path to a problem solution file."""
        lang_ext = {'python': 'py', 'javascript': 'js', 'java': f'{problem_name.replace("_", "").title()}.java'}
        base_name = f"{problem_name}.{lang_ext[language]}" if language != 'java' else f"{problem_name.replace('_', '').title()}.java"

        file_path = Path(__file__).parent / 'reference_solutions' / language / base_name
        return file_path

    def run_code(self, language: str, code_path: Path, input_data: str) -> tuple[str, float]:
        """Run code in the specified language and return output and execution time."""
        start_time = time.time()

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
                return f"Compilation Error: {compile_result.stderr.strip()}", time.time() - start_time

            # Run if compilation successful
            main_class_file = str(code_path).replace('.java', '')
            result = subprocess.run(
                ['java', '-cp', str(code_path.parent), 'Main'],
                input=input_data,
                text=True,
                capture_output=True,
                timeout=30
            )

        execution_time = time.time() - start_time
        output = result.stdout.strip()
        if result.stderr:
            output += f"\nSTDERR: {result.stderr.strip()}"

        return output, execution_time

    @pytest.mark.parametrize("problem_name", PROBLEM_NAMES)
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    def test_problem_solution(self, test_db, problems_data, problem_name, language):
        """Test that reference solutions produce correct output for all test cases."""
        # Get the problem from database
        problem = problems_data.get(problem_name)
        assert problem is not None, f"Problem {problem_name} not found in database"

        # Get the solution file
        solution_file = self.get_problem_file(problem_name, language)
        assert solution_file.exists(), f"Solution file {solution_file} does not exist"

        # Test all test cases
        test_cases = json.loads(problem.test_cases)
        for i, test_case in enumerate(test_cases):
            input_data = test_case['input']
            expected_output = test_case['output']

            # Run the solution
            output, exec_time = self.run_code(language, solution_file, input_data)

            assert output == expected_output, (
                f"Problem: {problem_name}, Language: {language}, Test case {i+1}\n"
                f"Input: {input_data}\n"
                f"Expected: {expected_output}\n"
                f"Got: {output}\n"
                f"Execution time: {exec_time:.4f}s"
            )

            # Assert execution time is reasonable (under 1 second for these simple problems)
            assert exec_time < 1.0, f"Execution time too slow: {exec_time:.4f}s for {problem_name} in {language}"
