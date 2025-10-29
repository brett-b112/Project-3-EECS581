from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import os
import tempfile
import subprocess
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leetlenew-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leetle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    input_example = db.Column(db.Text, nullable=False)
    output_example = db.Column(db.Text, nullable=False)
    test_cases = db.Column(db.Text, nullable=False)  # JSON string

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    language = db.Column(db.String(10), nullable=False)  # 'python', 'javascript', 'java'
    exec_time = db.Column(db.Float, nullable=False)  # in seconds
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions
def get_today_problem():
    # For simplicity, cycle through problems based on day
    day = datetime.now().day % db.session.query(Problem).count()
    if day == 0:
        day = db.session.query(Problem).count()
    return db.session.get(Problem, day)

def run_code_in_docker(language, code, input_data):
    execution_time = 0.0
    output = ""

    try:
        # Create temporary file for code
        ext = {'python': 'py', 'javascript': 'js', 'java': 'java'}[language]
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{ext}', delete=False) as f:
            f.write(code)
            filename = f.name

        start_time = time.time()

        # Run code based on language
        if language == 'python':
            result = subprocess.run(
                ['python3', filename],
                input=input_data,
                text=True,
                capture_output=True,
                timeout=30
            )
            output = result.stdout.strip()
            if result.stderr:
                output += f"\nSTDERR: {result.stderr.strip()}"

        elif language == 'javascript':
            result = subprocess.run(
                ['node', filename],
                input=input_data,
                text=True,
                capture_output=True,
                timeout=30
            )
            output = result.stdout.strip()
            if result.stderr:
                output += f"\nSTDERR: {result.stderr.strip()}"

        elif language == 'java':
            # For Java, we need to ensure the class is named Main
            if 'public class ' in code:
                # Simple check - assume the class is named Main
                # For robustness, could parse the class name
                pass

            # Compile first
            compile_result = subprocess.run(
                ['javac', filename],
                capture_output=True,
                text=True,
                timeout=30
            )

            if compile_result.returncode != 0:
                output = f"Compilation Error: {compile_result.stderr.strip()}"
            else:
                # Run if compilation successful
                main_class_file = filename.replace('.java', '')
                result = subprocess.run(
                    ['java', '-cp', os.path.dirname(filename), 'Main'],
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=30
                )
                output = result.stdout.strip()
                if result.stderr:
                    output += f"\nSTDERR: {result.stderr.strip()}"

        else:
            raise ValueError("Unsupported language")

        execution_time = time.time() - start_time

    except subprocess.TimeoutExpired:
        output = "Error: Code execution timed out (30 seconds)"
        execution_time = 30.0
    except FileNotFoundError:
        output = f"Error: {language.capitalize()} interpreter not found. Please install it."
        execution_time = 30.0
    except Exception as e:
        output = f"Error: {str(e)}"
        execution_time = 30.0

    finally:
        if 'filename' in locals() and os.path.exists(filename):
            os.unlink(filename)

    return output, execution_time

def validate_submission(problem, language, code):
    # Run code against each test case
    test_cases = json.loads(problem.test_cases)
    total_time = 0.0

    for test in test_cases:
        input_data = test['input']
        expected_output = test['output']

        output, time_taken = run_code_in_docker(language, code, input_data)
        total_time += time_taken

        if output != expected_output:
            return False, total_time

    return True, total_time

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/problem')
def problem():
    problem = get_today_problem()
    if 'start_time' not in session:
        session['start_time'] = datetime.utcnow().isoformat()
    return render_template('problem.html', problem=problem)

@app.route('/leaderboard')
def leaderboard():
    submissions = Submission.query.order_by(Submission.exec_time).all()
    return render_template('leaderboard.html', submissions=submissions)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    language = request.form.get('language')
    code = request.form.get('code')

    if not all([name, language, code]):
        flash('All fields are required')
        return redirect(url_for('problem'))

    problem = get_today_problem()

    is_correct, exec_time = validate_submission(problem, language, code)

    if not is_correct:
        flash('Incorrect solution')
        return redirect(url_for('problem'))

    # Save submission
    submission = Submission(name=name, problem_id=problem.id,
                          language=language, exec_time=exec_time)
    db.session.add(submission)
    db.session.commit()

    flash('Submission successful!')
    return redirect(url_for('leaderboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed problems if not exist
        if Problem.query.count() == 0:
            problems_data = [
                {
                    'title': 'Two Sum',
                    'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                    'input_example': 'nums = [2, 7, 11, 15], target = 9',
                    'output_example': '[0, 1]',
                    'test_cases': json.dumps([
                        {'input': '[2,7,11,15]\n9', 'output': '[0,1]'},
                        {'input': '[3,3]\n6', 'output': '[0,1]'}
                    ])
                },
                {
                    'title': 'Palindrome Number',
                    'description': 'Given an integer x, return true if x is palindrome integer.',
                    'input_example': 'x = 121',
                    'output_example': 'true',
                    'test_cases': json.dumps([
                        {'input': '121', 'output': 'true'},
                        {'input': '-121', 'output': 'false'},
                        {'input': '10', 'output': 'false'}
                    ])
                },
                {
                    'title': 'Reverse String',
                    'description': 'Write a function that reverses a string. The input string is given as an array of characters s. You must do this by modifying the input array in-place.',
                    'input_example': 's = ["h","e","l","l","o"]',
                    'output_example': '["o","l","l","e","h"]',
                    'test_cases': json.dumps([
                        {'input': '["h","e","l","l","o"]', 'output': '["o","l","l","e","h"]'},
                        {'input': '["H","a","n","n","a","h"]', 'output': '["h","a","n","n","a","H"]'}
                    ])
                },
                {
                    'title': 'FizzBuzz',
                    'description': 'Given an integer n, return a string array answer (1-indexed) where: answer[i] == "FizzBuzz" if i is divisible by 3 and 5. answer[i] == "Fizz" if i is divisible by 3. answer[i] == "Buzz" if i is divisible by 5. answer[i] == i (as a string) otherwise.',
                    'input_example': 'n = 3',
                    'output_example': '["1","2","Fizz"]',
                    'test_cases': json.dumps([
                        {'input': '3', 'output': '["1","2","Fizz"]'},
                        {'input': '5', 'output': '["1","2","Fizz","4","Buzz"]'}
                    ])
                },
                {
                    'title': 'Binary Search',
                    'description': 'Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.',
                    'input_example': 'nums = [-1,0,3,5,9,12], target = 9',
                    'output_example': '4',
                    'test_cases': json.dumps([
                        {'input': '[-1,0,3,5,9,12]\n9', 'output': '4'},
                        {'input': '[-1,0,3,5,9,12]\n2', 'output': '-1'}
                    ])
                }
            ]
            for prob in problems_data:
                problem = Problem(**prob)
                db.session.add(problem)
            db.session.commit()
    app.run(debug=True, host='0.0.0.0', port=5001)
