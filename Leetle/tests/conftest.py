import pytest
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, db, Problem

@pytest.fixture(scope='session')
def flask_app():
    """Create and configure a test app instance."""
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.config['SECRET_KEY'] = 'test-secret-key'
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with test_app.app_context():
        db.init_app(test_app)
        db.create_all()
        yield test_app

@pytest.fixture(scope='function')
def test_db(flask_app):
    """Create a fresh database for each test."""
    with flask_app.app_context():
        db.create_all()
        # Seed test problems
        seed_test_problems()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def problems_data(test_db):
    """Get the test problems data."""
    with test_db.session.begin():
        problems = Problem.query.all()
        return {problem.title.lower().replace(' ', '_'): problem for problem in problems}

def seed_test_problems():
    """Seed the database with test problems."""
    import json

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
