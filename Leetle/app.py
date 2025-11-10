from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
import tempfile
import subprocess
import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'leetlenew-secret-key-change-in-production'
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leetle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRE_MINUTES'] = 15
app.config['JWT_REFRESH_TOKEN_EXPIRE_DAYS'] = 7
db = SQLAlchemy(app)

# Database Models
class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(10), nullable=False, default='Medium')  # Easy, Medium, Hard
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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

# JWT Helper Functions
def generate_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=app.config['JWT_ACCESS_TOKEN_EXPIRE_MINUTES']),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def generate_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=app.config['JWT_REFRESH_TOKEN_EXPIRE_DAYS']),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload or payload.get('type') != 'access':
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Add user_id to request context
        request.user_id = payload['user_id']
        return f(*args, **kwargs)
    return decorated_function

# Authentication Routes
@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].lower().strip()
    password = data['password']

    # Validate email format (basic)
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email format'}), 400

    # Check password strength
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409

    # Create new user
    password_hash = generate_password_hash(password)
    new_user = User(email=email, password_hash=password_hash)

    try:
        db.session.add(new_user)
        db.session.commit()

        # Generate tokens
        access_token = generate_access_token(new_user.id)
        refresh_token = generate_refresh_token(new_user.id)

        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': new_user.id,
                'email': new_user.email
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create user'}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].lower().strip()
    password = data['password']

    # Find user
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Generate tokens
    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'email': user.email
        }
    }), 200

@app.route('/auth/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()

    if not data or not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token is required'}), 400

    refresh_token = data['refresh_token']
    payload = verify_token(refresh_token)

    if not payload or payload.get('type') != 'refresh':
        return jsonify({'error': 'Invalid refresh token'}), 401

    user_id = payload['user_id']

    # Verify user still exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 401

    # Generate new access token
    new_access_token = generate_access_token(user_id)

    return jsonify({
        'access_token': new_access_token
    }), 200

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/problem')
def problem():
    try:
        problem = get_today_problem()
        if not problem:
            return jsonify({'error': 'No problem found'}), 404
            
        return jsonify({
            'title': problem.title,
            'description': problem.description,
            'difficulty': getattr(problem, 'difficulty', 'Medium'),
            'input_example': problem.input_example,
            'output_example': problem.output_example
        }), 200
    except Exception as e:
        print(f"Error in /problem route: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/submit', methods=['POST'])
@token_required
def submit():
    data = request.get_json()

    if not data or not data.get('language') or not data.get('code'):
        return jsonify({'error': 'Language and code are required'}), 400

    language = data['language']
    code = data['code']

    # Get user info from token
    user_id = request.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 401

    problem = get_today_problem()
    if not problem:
        return jsonify({'error': 'No problem available today'}), 404

    is_correct, exec_time = validate_submission(problem, language, code)

    if not is_correct:
        return jsonify({'error': 'Incorrect solution'}), 400

    # Save submission
    submission = Submission(name=user.email, problem_id=problem.id,
                          language=language, exec_time=exec_time)
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'message': 'Submission successful!',
        'execution_time': exec_time,
        'problem_id': problem.id
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed problems if not exist
        if Problem.query.count() == 0:
            problems_data = [
                {
                    'title': 'Two Sum',
                    'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                    'difficulty': 'Easy',
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
                    'difficulty': 'Easy',
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
                    'difficulty': 'Easy',
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
                    'difficulty': 'Easy',
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
                    'difficulty': 'Easy',
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
