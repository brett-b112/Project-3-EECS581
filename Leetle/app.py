"""
This file serves as the main backend application for the Leetle coding platform, initializing the Flask app, defining database models, handling authentication via JWT, executing user code in Docker containers, and managing API endpoints for problems, leaderboards, and administrative tasks.
Authors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, and Arnav Jain
"""




"""
Initializes the Flask application, configures database connections and JWT settings, and imports necessary libraries for server operation.
Inputs: Environment variables (.env)
Outputs: Configured Flask application instance
Contributors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, Arnav Jain
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_compress import Compress
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import json
import os
import tempfile
import subprocess
import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'leetlenew-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leetle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRE_MINUTES'] = 15
app.config['JWT_REFRESH_TOKEN_EXPIRE_DAYS'] = 7
Compress(app)
db = SQLAlchemy(app)

# Database Models
"""
Database model representing a coding challenge, including its description, test cases, and solution data.
Inputs: title, description, difficulty, examples, test cases
Outputs: Problem database object
Contributors: Daniel Neugent, Jay Patel
"""
class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(10), nullable=False, default='Medium')  # Easy, Medium, Hard
    input_example = db.Column(db.Text, nullable=False)
    output_example = db.Column(db.Text, nullable=False)
    test_cases = db.Column(db.Text, nullable=False)  # JSON string
    hint_text = db.Column(db.Text, nullable=True)  # Partial hint
    full_solution = db.Column(db.Text, nullable=True)  # Full solution
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

"""
Database model recording a user's code attempt for a specific problem, including execution time and correctness.
Inputs: user_id, problem_id, language, code, execution status
Outputs: Submission database object
Contributors: Tej Gumaste, Arnav Jain
"""
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    language = db.Column(db.String(10), nullable=False)  # 'python', 'javascript', 'java'
    code = db.Column(db.Text, nullable=False)  # Store the actual code
    exec_time = db.Column(db.Float, nullable=False)  # in seconds
    is_correct = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='submissions')
    problem = db.relationship('Problem', backref='submissions')

"""
Database model managing user authentication credentials, roles, and aggregate streak information.
Inputs: email, password hash, role
Outputs: User database object
Contributors: Brett Balquist, Daniel Neugent
"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    total_solutions = db.Column(db.Integer, default=0)
    last_submission_date = db.Column(db.Date, nullable=True)

"""
Database model defining the available gamification rewards, including criteria for earning them and point values.
Inputs: name, description, criteria JSON, icon, points
Outputs: Achievement database object
Contributors: Jay Patel, Tej Gumaste
"""
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    criteria = db.Column(db.Text, nullable=False)  # JSON string describing criteria
    icon = db.Column(db.String(50), nullable=False)  # Icon identifier
    points = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

"""
Association model linking users to the specific achievements they have earned and the timestamp of earning.
Inputs: user_id, achievement_id
Outputs: UserAchievement database object
Contributors: Arnav Jain, Brett Balquist
"""
class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='achievements')
    achievement = db.relationship('Achievement', backref='users')

"""
Database model tracking detailed performance metrics for a user, such as total attempts and success rates.
Inputs: user_id, statistical counters
Outputs: UserStats database object
Contributors: Daniel Neugent, Jay Patel, Tej Gumaste
"""
class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_attempts = db.Column(db.Integer, default=0)
    total_correct = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    favorite_language = db.Column(db.String(10), default='python')
    problems_attempted = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='stats')

"""
Database model tracking which hints a user has revealed for specific problems to enforce daily limits.
Inputs: user_id, problem_id, hint_level
Outputs: UserHintUsage database object
Contributors: Brett Balquist, Arnav Jain
"""
class UserHintUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    hint_level = db.Column(db.String(10), nullable=False)  # 'partial', 'full'
    used_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='hint_usage')
    problem = db.relationship('Problem', backref='hint_usage')

"""
Database model storing anonymous or signed user feedback and ratings regarding the platform.
Inputs: user_id (optional), rating, feedback text
Outputs: FeedbackSubmission database object
Contributors: Tej Gumaste, Daniel Neugent
"""
class FeedbackSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional for anonymous
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    feedback_text = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions

"""
Selects a problem based on the current day of the month to ensure all users see the same daily challenge.
Inputs: None
Outputs: Problem object or None
Contributors: Daniel Neugent, Brett Balquist
"""
def get_today_problem():
    # For simplicity, cycle through problems based on day
    day = datetime.now().day % db.session.query(Problem).count()
    if day == 0:
        day = db.session.query(Problem).count()
    return db.session.get(Problem, day)

"""
Executes user-submitted code within a secure isolated environment using temporary files and subprocess calls.
Inputs: language (string), code (string), input_data (string)
Outputs: output (string), execution_time (float)
Contributors: Tej Gumaste, Arnav Jain, Jay Patel
"""
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

"""
Computes the current streak of consecutive days a user has successfully solved a problem.
Inputs: user (User object)
Outputs: streak (integer)
Contributors: Brett Balquist, Daniel Neugent
"""
def calculate_user_streak(user):
    """Calculate current streak based on submission dates"""
    from collections import defaultdict

    # Get all successful submissions ordered by date
    submissions = Submission.query.filter_by(user_id=user.id, is_correct=True)\
                                 .order_by(Submission.submitted_at).all()

    if not submissions:
        return 0

    # Group submissions by date
    daily_success = defaultdict(bool)
    for sub in submissions:
        date = sub.submitted_at.date()
        daily_success[date] = True

    # Count consecutive days from today backwards
    streak = 0
    current_date = datetime.now().date()

    while daily_success.get(current_date, False):
        streak += 1
        current_date -= timedelta(days=1)

    return streak

"""
Updates the user's statistics, including success rate, favorite language, and streak counters, after a submission.
Inputs: user (User object), language (string), is_correct (boolean)
Outputs: None
Contributors: Jay Patel, Arnav Jain
"""
def update_user_stats(user, language, is_correct):
    """Update user statistics and streaks after a submission"""
    # Get or create user stats
    stats = UserStats.query.filter_by(user_id=user.id).first()
    if not stats:
        stats = UserStats(user_id=user.id)
        db.session.add(stats)

    # Update attempts and success rate
    stats.total_attempts += 1
    if is_correct:
        stats.total_correct += 1
    stats.success_rate = (stats.total_correct / stats.total_attempts) * 100 if stats.total_attempts > 0 else 0

    # Update favorite language based on usage frequency
    language_counts = {}
    user_subs = Submission.query.filter_by(user_id=user.id).all()
    for sub in user_subs:
        language_counts[sub.language] = language_counts.get(sub.language, 0) + 1
    stats.favorite_language = max(language_counts, key=language_counts.get) if language_counts else language

    stats.updated_at = datetime.now(timezone.utc)
    stats.problems_attempted = len(set(sub.problem_id for sub in user_subs))

    # Update streak information
    if is_correct:
        today = datetime.now().date()
        user.last_submission_date = today
        user.current_streak = calculate_user_streak(user)
        user.longest_streak = max(user.longest_streak, user.current_streak)
        user.total_solutions += 1

    db.session.commit()

"""
Evaluates the user's progress against achievement criteria and awards new achievements if conditions are met.
Inputs: user (User object)
Outputs: None
Contributors: Tej Gumaste, Brett Balquist, Daniel Neugent
"""
def check_and_award_achievements(user):
    """Check if user has earned any new achievements"""
    achievements = Achievement.query.all()
    user_achievement_ids = [ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user.id).all()]

    for achievement in achievements:
        if achievement.id in user_achievement_ids:
            continue

        criteria = json.loads(achievement.criteria)

        earned = True
        if 'min_streak' in criteria and user.current_streak < criteria['min_streak']:
            earned = False
        if 'total_solutions' in criteria and user.total_solutions < criteria['total_solutions']:
            earned = False
        if 'success_rate' in criteria and UserStats.query.filter_by(user_id=user.id).first().success_rate < criteria['success_rate']:
            earned = False

        if earned:
            user_achievement = UserAchievement(user_id=user.id, achievement_id=achievement.id)
            db.session.add(user_achievement)

    db.session.commit()

"""
Runs the user's submitted code against all defined test cases for a specific problem to verify correctness.
Inputs: problem (Problem object), language (string), code (string)
Outputs: is_valid (boolean), total_execution_time (float)
Contributors: Daniel Neugent, Jay Patel
"""
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
"""
Creates a long-lived JSON Web Token used to obtain new access tokens without re-login.
Inputs: user_id (integer)
Outputs: encoded_token (string)
Contributors: Arnav Jain, Tej Gumaste
"""
def generate_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=app.config['JWT_ACCESS_TOKEN_EXPIRE_MINUTES']),
        'iat': datetime.now(timezone.utc),
        'type': 'access'
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

"""
Creates a long-lived JSON Web Token used to obtain new access tokens without re-login.
Inputs: user_id (integer)
Outputs: encoded_token (string)
Contributors: Arnav Jain, Tej Gumaste
"""
def generate_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=app.config['JWT_REFRESH_TOKEN_EXPIRE_DAYS']),
        'iat': datetime.now(timezone.utc),
        'type': 'refresh'
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

"""
Decodes and validates the signature and expiration of a JSON Web Token.
Inputs: token (string)
Outputs: payload (dictionary) or None
Contributors: Brett Balquist, Jay Patel, Daniel Neugent
"""
def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

"""
Decorator that ensures a valid access token is present in the request headers before allowing access to a route.
Inputs: f (function)
Outputs: decorated_function (function)
Contributors: Tej Gumaste, Daniel Neugent, Arnav Jain, Brett Balquist, Jay Patel
"""
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

"""
Decorator that restricts access to a route to users with the 'admin' role only.
Inputs: f (function)
Outputs: decorated_function (function)
Contributors: Jay Patel, Brett Balquist
"""
def admin_required(f):
    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        user = User.query.get(request.user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

"""
Registers a new user account after validating email format and password strength.
Inputs: JSON payload (email, password)
Outputs: JSON response (success message, tokens, user info) or error
Contributors: Daniel Neugent, Arnav Jain
"""
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

"""
Authenticates a user by verifying credentials and returning access and refresh tokens.
Inputs: JSON payload (email, password)
Outputs: JSON response (tokens, user info) or error
Contributors: Daniel Neugent, Arnav Jain
"""
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

"""
Issues a new access token if a valid refresh token is provided.
Inputs: JSON payload (refresh_token)
Outputs: JSON response (new access_token) or error
Contributors: Tej Gumaste, Brett Balquist
"""
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

"""
Renders the main landing page of the application.
Inputs: None
Outputs: Rendered HTML template
Contributors: Jay Patel
"""
# Routes
@app.route('/')
def home():
    return render_template('home.html')

"""
Retrieves the details of the daily problem, including description and examples.
Inputs: None
Outputs: JSON response (problem details) or error
Contributors: Brett Balquist, Daniel Neugent
"""
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


"""
Processes a code submission, validates it against test cases, and updates user stats.
Inputs: JSON payload (language, code), User ID (from token)
Outputs: JSON response (success status, execution time) or error
Contributors: Tej Gumaste, Arnav Jain, Jay Patel
"""
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

    # Save submission - always save, even if incorrect, to track attempts
    submission = Submission(user_id=user_id, problem_id=problem.id,
                           language=language, code=code, exec_time=exec_time,
                           is_correct=is_correct)
    db.session.add(submission)
    db.session.commit()

    if not is_correct:
        return jsonify({'error': 'Incorrect solution'}), 400

    # Update user stats and streaks
    update_user_stats(user, language, is_correct)
    check_and_award_achievements(user)

    return jsonify({
        'message': 'Submission successful!',
        'execution_time': exec_time,
        'problem_id': problem.id
    }), 200

# New API Routes for Sprint 3

"""
Retrieves a ranked list of users based on streaks and success rates, filtered by time period.
Inputs: Query parameters (period, limit)
Outputs: JSON response (leaderboard list, current user rank)
Contributors: Brett Balquist, Tej Gumaste, Daniel Neugent
"""
@app.route('/api/leaderboard')
@token_required
def get_leaderboard():
    """Get leaderboard data with rankings by streaks and accuracy"""
    period = request.args.get('period', 'all-time')  # daily, weekly, all-time
    limit = request.args.get('limit', 50, type=int)

    # Base query for users with stats
    query = db.session.query(User, UserStats).join(UserStats)

    # Apply time filters
    if period == 'daily':
        # Users with submissions today
        today = datetime.now().date()
        user_ids = db.session.query(Submission.user_id).filter(
            Submission.submitted_at >= today
        ).distinct().all()
        user_ids = [uid[0] for uid in user_ids]
        query = query.filter(User.id.in_(user_ids))
    elif period == 'weekly':
        # Users with submissions in last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        user_ids = db.session.query(Submission.user_id).filter(
            Submission.submitted_at >= week_ago
        ).distinct().all()
        user_ids = [uid[0] for uid in user_ids]
        query = query.filter(User.id.in_(user_ids))

    # Calculate ranking score: streak + (success_rate / 10)
    leaderboard = []
    for user, stats in query.all():
        score = user.current_streak + (stats.success_rate / 10.0)
        leaderboard.append({
            'id': user.id,
            'email': user.email,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'total_solutions': user.total_solutions,
            'success_rate': round(stats.success_rate, 1),
            'score': round(score, 2)
        })

    # Sort by score descending
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    leaderboard = leaderboard[:limit]

    # Add ranking positions
    for i, entry in enumerate(leaderboard, 1):
        entry['rank'] = i

    # Highlight current user position
    current_user_id = request.user_id
    current_user_rank = None
    for entry in leaderboard:
        if entry['id'] == current_user_id:
            current_user_rank = entry['rank']
            break

    return jsonify({
        'leaderboard': leaderboard,
        'current_user_rank': current_user_rank,
        'period': period
    }), 200

"""
Fetches detailed statistics, achievements, and language usage data for a specific user.
Inputs: user_id (integer)
Outputs: JSON response (stats, achievements, language breakdown)
Contributors: Jay Patel, Arnav Jain
"""
@app.route('/api/user/stats/<int:user_id>')
@token_required
def get_user_stats(user_id):
    """Get detailed statistics for a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    stats = UserStats.query.filter_by(user_id=user_id).first()

    # If no stats record exists yet (new user), use default values
    if not stats:
        default_stats = {
            'total_attempts': 0,
            'total_correct': 0,
            'success_rate': 0.0,
            'favorite_language': 'python',
            'problems_attempted': 0
        }
    else:
        default_stats = {
            'total_attempts': stats.total_attempts,
            'total_correct': stats.total_correct,
            'success_rate': round(stats.success_rate, 1),
            'favorite_language': stats.favorite_language,
            'problems_attempted': stats.problems_attempted
        }

    # Get user achievements
    achievements = []
    user_achievements = UserAchievement.query.filter_by(user_id=user_id).join(Achievement).all()
    for ua in user_achievements:
        achievements.append({
            'id': ua.achievement.id,
            'name': ua.achievement.name,
            'description': ua.achievement.description,
            'icon': ua.achievement.icon,
            'earned_at': ua.earned_at.isoformat()
        })

    # Language usage statistics
    language_stats = {}
    submissions = Submission.query.filter_by(user_id=user_id).all()
    for sub in submissions:
        lang = sub.language
        if lang not in language_stats:
            language_stats[lang] = {'attempts': 0, 'correct': 0}
        language_stats[lang]['attempts'] += 1
        if sub.is_correct:
            language_stats[lang]['correct'] += 1

    return jsonify({
        'user': {
            'id': user.id,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        },
        'stats': {
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'total_solutions': user.total_solutions,
            'total_attempts': default_stats['total_attempts'],
            'success_rate': default_stats['success_rate'],
            'favorite_language': default_stats['favorite_language'],
            'problems_attempted': default_stats['problems_attempted']
        },
        'achievements': achievements,
        'language_stats': language_stats
    }), 200

"""
Retrieves a list of all problems with their metadata and success rates for administrative review.
Inputs: None (Requires Admin Token)
Outputs: JSON response (list of problems)
Contributors: Daniel Neugent, Brett Balquist
"""
@app.route('/api/admin/problems', methods=['GET'])
@admin_required
def get_admin_problems():
    """Get all problems for admin management"""
    problems = Problem.query.all()
    problems_data = []

    for problem in problems:
        # Get submission stats
        total_subs = Submission.query.filter_by(problem_id=problem.id).count()
        correct_subs = Submission.query.filter_by(problem_id=problem.id, is_correct=True).count()
        success_rate = (correct_subs / total_subs * 100) if total_subs > 0 else 0

        problems_data.append({
            'id': problem.id,
            'title': problem.title,
            'difficulty': problem.difficulty,
            'is_active': problem.is_active,
            'created_at': problem.created_at.isoformat(),
            'total_attempts': total_subs,
            'success_rate': round(success_rate, 1)
        })

    return jsonify({'problems': problems_data}), 200

"""
Allows an admin to create a new coding problem with description and test cases.
Inputs: JSON payload (title, description, difficulty, test_cases)
Outputs: JSON response (success message, problem_id)
Contributors: Daniel Neugent, Tej Gumaste
"""
@app.route('/api/admin/problems', methods=['POST'])
@admin_required
def create_problem():
    """Create a new problem"""
    data = request.get_json()

    if not data or not data.get('title') or not data.get('description') or not data.get('difficulty'):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate difficulty
    if data['difficulty'] not in ['Easy', 'Medium', 'Hard']:
        return jsonify({'error': 'Invalid difficulty level'}), 400

    # Validate test cases
    if not data.get('test_cases') or not isinstance(data['test_cases'], list):
        return jsonify({'error': 'Test cases must be provided as array'}), 400

    for test_case in data['test_cases']:
        if 'input' not in test_case or 'output' not in test_case:
            return jsonify({'error': 'Each test case must have input and output'}), 400

    problem = Problem(
        title=data['title'],
        description=data['description'],
        difficulty=data['difficulty'],
        input_example=data.get('input_example', ''),
        output_example=data.get('output_example', ''),
        test_cases=json.dumps(data['test_cases'])
    )

    try:
        db.session.add(problem)
        db.session.commit()
        return jsonify({
            'message': 'Problem created successfully',
            'problem_id': problem.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create problem'}), 500

"""
Updates the details of an existing problem identified by its ID.
Inputs: problem_id (integer), JSON payload (fields to update)
Outputs: JSON response (success message) or error
Contributors: Jay Patel, Brett Balquist
"""
@app.route('/api/admin/problems/<int:problem_id>', methods=['PUT'])
@admin_required
def update_problem(problem_id):
    """Update an existing problem"""
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update allowed fields
    allowed_fields = ['title', 'description', 'difficulty', 'input_example', 'output_example', 'is_active']
    for field in allowed_fields:
        if field in data:
            if field == 'difficulty' and data[field] not in ['Easy', 'Medium', 'Hard']:
                return jsonify({'error': 'Invalid difficulty level'}), 400
            setattr(problem, field, data[field])

    # Update test cases if provided
    if 'test_cases' in data and isinstance(data['test_cases'], list):
        setattr(problem, 'test_cases', json.dumps(data['test_cases']))

    try:
        db.session.commit()
        return jsonify({'message': 'Problem updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update problem'}), 500

"""
Deletes a specific problem from the database.
Inputs: problem_id (integer)
Outputs: JSON response (success message) or error
Contributors: Arnav Jain, Daniel Neugent
"""
@app.route('/api/admin/problems/<int:problem_id>', methods=['DELETE'])
@admin_required
def delete_problem(problem_id):
    """Delete a problem"""
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    try:
        db.session.delete(problem)
        db.session.commit()
        return jsonify({'message': 'Problem deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete problem'}), 500

"""
Retrieves a list of all registered users and their basic statistics for admin management.
Inputs: None (Requires Admin Token)
Outputs: JSON response (list of users)
Contributors: Tej Gumaste, Jay Patel
"""
@app.route('/api/admin/users')
@admin_required
def get_admin_users():
    """Get users for admin management"""
    users = User.query.all()
    users_data = []

    for user in users:
        stats = UserStats.query.filter_by(user_id=user.id).first()
        users_data.append({
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'current_streak': user.current_streak,
            'total_solutions': user.total_solutions,
            'success_rate': round(stats.success_rate, 1) if stats else 0,
            'created_at': user.created_at.isoformat()
        })

    return jsonify({'users': users_data}), 200

"""
Aggregates and returns platform-wide analytics such as total submissions and difficulty breakdowns.
Inputs: None (Requires Admin Token)
Outputs: JSON response (overview stats, difficulty breakdown)
Contributors: Brett Balquist, Arnav Jain, Daniel Neugent
"""
@app.route('/api/admin/analytics')
@admin_required
def get_admin_analytics():
    """Get platform analytics"""
    # Overall stats
    total_users = User.query.count()
    total_problems = Problem.query.count()
    total_submissions = Submission.query.count()
    total_correct = Submission.query.filter_by(is_correct=True).count()
    overall_success_rate = (total_correct / total_submissions * 100) if total_submissions > 0 else 0

    # Daily active users (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    daily_active = db.session.query(Submission.user_id).filter(
        Submission.submitted_at >= thirty_days_ago
    ).distinct().count()

    # Problem difficulty breakdown
    difficulty_stats = {}
    for difficulty in ['Easy', 'Medium', 'Hard']:
        problems = Problem.query.filter_by(difficulty=difficulty)
        correct = Submission.query.filter(
            Submission.problem_id.in_([p.id for p in problems]),
            Submission.is_correct == True
        ).count()
        total = Submission.query.filter(
            Submission.problem_id.in_([p.id for p in problems])
        ).count()
        difficulty_stats[difficulty] = {
            'count': problems.count(),
            'attempts': total,
            'success_rate': round((correct / total * 100) if total > 0 else 0, 1)
        }

    return jsonify({
        'overview': {
            'total_users': total_users,
            'total_problems': total_problems,
            'total_submissions': total_submissions,
            'overall_success_rate': round(overall_success_rate, 1),
            'daily_active_users': daily_active
        },
        'difficulty_breakdown': difficulty_stats
    }), 200

"""
Returns a list of all available achievements and indicates which ones the current user has earned.
Inputs: User ID (from token)
Outputs: JSON response (list of achievements)
Contributors: Tej Gumaste, Jay Patel
"""
@app.route('/api/achievements')
@token_required
def get_achievements():
    """Get all available achievements and user progress"""
    achievements = Achievement.query.filter_by(is_active=True).all()
    user_achievements = UserAchievement.query.filter_by(user_id=request.user_id).all()
    earned_ids = [ua.achievement_id for ua in user_achievements]

    achievements_data = []
    for achievement in achievements:
        achievements_data.append({
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'icon': achievement.icon,
            'points': achievement.points,
            'earned': achievement.id in earned_ids
        })

    return jsonify({'achievements': achievements_data}), 200

"""
Checks the availability of hints for a specific problem and the user's daily hint usage.
Inputs: problem_id (integer), User ID (from token)
Outputs: JSON response (hint availability, usage counts)
Contributors: Daniel Neugent, Brett Balquist
"""
@app.route('/api/hints/<int:problem_id>')
@token_required
def get_hints(problem_id):
    """Get hints for a problem with daily usage limits"""
    user_id = request.user_id
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    # Check daily hint usage (max 3 per day total)
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_hint_usage = UserHintUsage.query.filter(
        UserHintUsage.user_id == user_id,
        UserHintUsage.used_at >= today_start
    ).count()

    if today_hint_usage >= 3:
        return jsonify({'error': 'Daily hint limit reached (3 hints per day)'}), 429

    # Get existing hint usage for this problem today
    problem_hint_usage = UserHintUsage.query.filter(
        UserHintUsage.user_id == user_id,
        UserHintUsage.problem_id == problem_id,
        UserHintUsage.used_at >= today_start
    ).first()

    hints = {}
    if problem.hint_text:
        hints['partial'] = problem.hint_text
    if problem.full_solution:
        hints['full'] = problem.full_solution

    response = {
        'hints_available': bool(hints),
        'daily_usage': today_hint_usage,
        'max_daily_usage': 3,
        'problem_hinted_today': problem_hint_usage is not None
    }

    if hints:
        if problem_hint_usage and problem_hint_usage.hint_level == 'partial':
            response['hints'] = hints  # Already used partial, show all
        elif not problem_hint_usage:
            response['hints'] = {'partial': hints.get('partial', 'No hint available')}
        else:
            response['hints'] = hints

    return jsonify(response), 200

"""
Reveals a specific hint level (partial or full) for a problem, updating the user's daily usage count.
Inputs: problem_id (integer), hint_level (string), User ID (from token)
Outputs: JSON response (hint text, cost info) or error
Contributors: Daniel Neugent, Tej Gumaste, Jay Patel
"""
@app.route('/api/hints/<int:problem_id>/<hint_level>', methods=['POST'])
@token_required
def reveal_hint(problem_id, hint_level):
    """Reveal a specific hint level for a problem"""
    if hint_level not in ['partial', 'full']:
        return jsonify({'error': 'Invalid hint level'}), 400

    user_id = request.user_id
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    # Check daily limit
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_hint_usage = UserHintUsage.query.filter(
        UserHintUsage.user_id == user_id,
        UserHintUsage.used_at >= today_start
    ).count()

    if hint_level == 'full' and today_hint_usage >= 3:
        return jsonify({'error': 'Cannot reveal full solution - daily hint limit reached'}), 429

    # Check if partial hint was already used for this problem today
    existing_usage = UserHintUsage.query.filter(
        UserHintUsage.user_id == user_id,
        UserHintUsage.problem_id == problem_id,
        UserHintUsage.used_at >= today_start
    ).first()

    if hint_level == 'full':
        if existing_usage and existing_usage.hint_level == 'partial':
            # Already paid partial cost (1 usage), reveal full
            existing_usage.hint_level = 'full'
            db.session.commit()
            return jsonify({
                'hint': problem.full_solution or 'No full solution available',
                'daily_usage': today_hint_usage,
                'cost': 1  # Additional cost for full when partial was used
            }), 200
        elif not existing_usage:
            # First time usage for full hint (costs 2)
            if today_hint_usage >= 2:  # 2 remaining slots needed
                return jsonify({'error': 'Not enough hint usage remaining for full solution'}), 429
            usage = UserHintUsage(user_id=user_id, problem_id=problem_id, hint_level='full')
            db.session.add(usage)
            db.session.commit()
            return jsonify({
                'hint': problem.full_solution or 'No full solution available',
                'daily_usage': today_hint_usage + 2,
                'cost': 2
            }), 200
        else:
            # Already revealed full
            return jsonify({'error': 'Full solution already revealed'}), 400
    else:  # partial
        if not existing_usage:
            usage = UserHintUsage(user_id=user_id, problem_id=problem_id, hint_level='partial')
            db.session.add(usage)
            db.session.commit()
            return jsonify({
                'hint': problem.hint_text or 'No hint available',
                'daily_usage': today_hint_usage + 1,
                'cost': 1
            }), 200
        else:
            # Partial already revealed
            return jsonify({'error': 'Hint already revealed'}), 400

"""
Accepts and stores user feedback ratings and comments about the platform.
Inputs: JSON payload (rating, feedback_text)
Outputs: JSON response (success message)
Contributors: Arnav Jain, Brett Balquist
"""
@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    """Submit user feedback (anonymous OK)"""
    data = request.get_json()

    if not data or not data.get('rating') or not data.get('feedback_text'):
        return jsonify({'error': 'Rating and feedback text are required'}), 400

    rating = data['rating']
    feedback_text = data['feedback_text']

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    # Get user_id from token if authenticated, otherwise None
    user_id = getattr(request, 'user_id', None)

    feedback = FeedbackSubmission(
        user_id=user_id,
        rating=rating,
        feedback_text=feedback_text
    )

    try:
        db.session.add(feedback)
        db.session.commit()
        return jsonify({'message': 'Feedback submitted successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to submit feedback'}), 500


"""
Entry point for the script that initializes the database tables and seeds default problems, achievements, and admin users if they do not exist.
Inputs: None
Outputs: Running Flask server on port 5001
Contributors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, Arnav Jain
"""
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
            for prob in problems_data:
                problem = Problem(**prob)
                db.session.add(problem)
            db.session.commit()

        # Seed achievements if not exist
        if Achievement.query.count() == 0:
            achievements_data = [
                {
                    'name': 'First Win',
                    'description': 'Solve your first problem',
                    'criteria': json.dumps({'total_solutions': 1}),
                    'icon': 'trophy',
                    'points': 10
                },
                {
                    'name': 'Problem Solver',
                    'description': 'Solve 10 problems',
                    'criteria': json.dumps({'total_solutions': 10}),
                    'icon': 'star',
                    'points': 25
                },
                {
                    'name': 'Streak Beginner',
                    'description': 'Maintain a 3-day streak',
                    'criteria': json.dumps({'min_streak': 3}),
                    'icon': 'fire',
                    'points': 20
                },
                {
                    'name': 'Streak Master',
                    'description': 'Maintain a 7-day streak',
                    'criteria': json.dumps({'min_streak': 7}),
                    'icon': 'flame',
                    'points': 50
                },
                {
                    'name': 'Accuracy Expert',
                    'description': 'Achieve 90% success rate with at least 10 attempts',
                    'criteria': json.dumps({'success_rate': 90}),
                    'icon': 'target',
                    'points': 30
                },
                {
                    'name': 'Century Club',
                    'description': 'Solve 100 problems',
                    'criteria': json.dumps({'total_solutions': 100}),
                    'icon': 'medal',
                    'points': 100
                }
            ]
            for ach_data in achievements_data:
                achievement = Achievement(**ach_data)
                db.session.add(achievement)
            db.session.commit()

        # Create admin user if not exists (for testing)
        if User.query.filter_by(role='admin').count() == 0:
            admin_password = generate_password_hash('admin123')
            admin_user = User(
                email='admin@leetle.com',
                password_hash=admin_password,
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True, host='0.0.0.0', port=5001)
