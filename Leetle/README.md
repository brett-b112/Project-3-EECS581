# Leetle - Daily Coding Challenge Platform

Leetle is a coding challenge platform where users solve daily algorithmic problems using Python, JavaScript, or Java. Track streaks, earn achievements, use hints when stuck, and compete on leaderboards.

## Features

### Sprint 4 Features Implemented

#### **Reward Systems & Achievements**
- **Badge System**: Earn badges for solving problems, maintaining streaks, and achieving high success rates
- **Streak Tracking**: Daily submission tracking with streak counters and longest streak records
- **Achievement Unlocks**: Automatic badge awarding with criteria-based achievements

#### **Hint System**
- **Partial Hints**: Get helpful clues for 1 hint charge (max 3 per day)
- **Full Solutions**: Reveal complete solutions for 2 hint charges
- **Usage Limits**: Daily hint limits prevent overuse and encourage learning
- **Problem-Specific**: Hints tailored to each daily challenge

#### **Performance Optimizations**
- **Lazy Loading**: Page components loaded on-demand for faster initial loads
- **Response Compression**: Gzip compression reduces data transfer
- **Caching**: Client-side caching for API responses reduces server load
- **Database Optimization**: Indexed queries for leaderboard and user stats

#### **Beta Feedback System**
- **In-App Feedback**: Rating system (1-5 stars) with optional text feedback
- **Anonymous Submissions**: Feedback collection without authentication required
- **Admin Analytics**: Platform administrators can analyze user sentiment trends

#### **Security & Production Readiness**
- **Environment Configuration**: Secure environment variable handling
- **JWT Authentication**: Stateless authentication with refresh tokens
- **Deployment Configs**: Ready for Render and Vercel deployment

## Architecture

### Backend (Flask + SQLAlchemy)
- **Framework**: Flask with SQLAlchemy ORM
- **Authentication**: JWT-based auth with refresh tokens
- **Database**: SQLite (easily swappable to PostgreSQL)
- **Code Execution**: Docker-based secure code execution
- **API**: RESTful endpoints with CORS support

### Frontend (React + Vite)
- **Framework**: React 18 with Vite build tool
- **Styling**: Tailwind CSS with custom components
- **State Management**: React hooks with context API
- **Code Editor**: Monaco Editor integration
- **Performance**: Code splitting with lazy loading

### Database Models
- `User`: User accounts with streak tracking
- `Problem`: Daily challenges with hint content
- `Submission`: User code submissions with execution results
- `Achievement`: Badge definitions and criteria
- `UserAchievement`: User-earned badges
- `UserStats`: Performance analytics
- `UserHintUsage`: Hint usage tracking for rate limiting
- `FeedbackSubmission`: User feedback collection

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker (for code execution)

### Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations and seed data
python app.py  # First run creates database and seeds it
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Development server on http://localhost:5173
```

### Backend Server
```bash
python app.py  # Runs on http://localhost:5001
```

## API Documentation

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access tokens

### Core Features
- `GET /problem` - Get today's coding challenge
- `POST /submit` - Submit code solution
- `GET /api/leaderboard` - Get ranked leaderboard
- `GET /api/user/stats/:user_id` - Get user statistics
- `GET /api/achievements` - Get available achievements

### Sprint 4 Features
- `GET /api/hints/:problem_id` - Get hint availability
- `POST /api/hints/:problem_id/:level` - Reveal hints (partial/full)
- `POST /api/feedback/submit` - Submit user feedback

### Admin Functions
- Full problem management (CRUD)
- User analytics and statistics
- System health monitoring

## Deployment

### Backend (Render)
- Service: Python web service
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`
- Environment: Set `SECRET_KEY` and `FLASK_ENV=production`

### Frontend (Vercel)
- Build: `npm run build`
- Output: `./dist`
- SPA routing configured for React Router

## Development Guidelines

### Code Style
- **Backend**: Follow PEP 8 with Black formatting
- **Frontend**: ESLint configuration with Prettier
- **Commits**: Conventional commit messages

### Testing
- **Backend**: pytest for unit tests (TBD)
- **Frontend**: Jest + Cypress for E2E (TBD)
- **API**: Postman collections for endpoint testing

## Known Issues & Limitations

- **Database**: SQLite suitable for development; migrate to PostgreSQL for production scale
- **Code Execution**: Docker-based execution ensures security but has timeout limits
- **File Uploads**: No file upload support (future enhancement)
- **Real-time**: No WebSocket integration for live updates
- **Social Features**: No chat or direct messaging system
- **Mobile App**: PWA capabilities undeveloped
- **Multilingual**: English-only interface
- **Analytics**: Basic metrics; advanced analytics pending
- **Documentation**: API docs need expansion
- **Testing**: E2E test coverage incomplete
- **Accessibility**: WCAG compliance partial
- **Performance**: Lighthouse scores target 90+ but may vary
- **Security**: Basic auth; add rate limiting and monitoring for production

## Future Enhancements

### Short Term
- Complete E2E test suite
- Advanced analytics dashboard
- Social sharing without OAuth
- Mobile app responsiveness validation
- Performance monitoring integration

### Medium Term
- PostgreSQL migration
- Redis caching layer
- WebSocket real-time notifications
- Multi-tenant support
- Advanced problem difficulty algorithms

### Long Term
- Machine learning-powered problem recommendations
- Code execution sandbox improvements
- Mobile native apps
- AI-powered hint generation
- Global leaderboard competitions

## Contributors

- **Daniel Neugent**: Achievement system, backend API development
- **Brett Balquist**: Hint system implementation, UI/UX design
- **Jay Patel**: Performance optimizations, deployment engineering
- **Arnav Jain**: Security enhancements, testing infrastructure
- **Tej Gumaste**: Documentation, feedback system integration

## License

This project is developed for educational purposes as part of EECS 581 coursework.
