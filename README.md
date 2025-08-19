# SE Project - Life Skills App for School-Aged Children

Software Engineering Project - May 2025, Team 25

## Problem Statement

**Problem Statement 2: Life Skills App for School-Aged Children**

Design and build a web or mobile application aimed at helping school-aged children (roughly ages 8–14) develop essential life skills. These might include time management, emotional intelligence, financial literacy, communication, or healthy habits. You are required to actually talk to users to identify genuine concerns and propose features that directly respond to those concerns. Choose a skill area that is age-appropriate and impactful, and create a solution that engages and supports kids in learning or practicing that skill.

## Project Structure

```
├── backend/                        # Flask backend application
│   ├── __init__.py
│   ├── API_GUIDE.md
│   ├── app.py                      # Main Flask application
│   ├── chatbot_prompt.md
│   ├── config.py                   # Configuration settings
│   ├── instance/
│   │   └── app.db                  # Database files
│   ├── models.py                   # Database models
│   ├── package.json
│   ├── requirements.txt            # Python dependencies
│   ├── safe_test_runner.sh
│   ├── safe_test_setup.py
│   ├── services/                   # Backend services
│   │   ├── __init__.py
│   │   └── psychometry.py          # Assessment engine
│   ├── static/                     # Static assets (images, drawings)
│   │   ├── drawings/
│   │   └── reference_images/
│   ├── test_config.py
│   ├── test_files/                 # Test documentation and scripts
│   └── venv/
├── frontend/                       # Vue.js frontend application
│   ├── .gitattributes
│   ├── .gitignore
│   ├── .prettierrc.json
│   ├── README.md
│   ├── index.html
│   ├── jsconfig.json
│   ├── node_modules/
│   ├── package-lock.json
│   ├── package.json                # Node.js dependencies
│   ├── public/                     # Public assets
│   │   ├── audio/
│   │   └── favicon.ico
│   ├── src/                        # Source code
│   │   ├── App.vue
│   │   ├── assets/
│   │   ├── components/
│   │   ├── main.js
│   │   ├── router/
│   │   ├── services/
│   │   ├── utils/
│   │   └── views/
│   └── vite.config.js
├── LICENSE
├── README.md                       # Project overview
├── requirements.txt                # Root Python dependencies
├── team_25_kidquest.yaml
└── venv/
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:

   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

### Demo Credentials

For demo purposes, you can use the following credentials:

- **Admin**: Username: `admin`, Password: `admin123`
- **Child**: Username: `child`, Password: `childchild`
- **Parent**: Username: `parent`, Password: `parentparent`
- **Teacher**: Username: `teacher`, Password: `teacherteacher`

## Features

- Session-based AI chatbot with mood detection
- Drawing Pad and creative activities
- Story Builder activity
- Memory Game activity
- Pomodoro Timer for focus
- Task Tracker for productivity
- Health Tracker and wellness streaks
- Psychometric assessments
- Parent-child interaction features
- Achievements and rewards system
- Notification system
- Admin, Teacher, Parent, and Child dashboards
- Educational modules: Good Touch Bad Touch, Science Explorer, Word Wizard, Math Magic, Safety Measures
- Analytics dashboard for user activity and engagement

## 📑 Backend Test Files & Instructions

The backend contains comprehensive test suites for all major modules and APIs. Each test file is located in `backend/test_files/` and is accompanied by detailed documentation. Below is a summary of each test area and how to use the documentation:

### Admin User Management

- **Test File:** `test_admin_user_crud.py`
- **Docs:** `Admin_User_CRUD_Test_Documentation.md`
- **Covers:** Admin/parent/child/teacher CRUD, authentication, security, data integrity
- **How to use:** See the Markdown doc for endpoint details, test cases, and setup/teardown patterns.

### Doodling API

- **Test File:** `test_doodling_session.py`
- **Docs:** `Doodling_Test_Documentation.md`
- **Covers:** Drawing session management, save/load, reference images
- **How to use:** Follow the doc for API payloads, expected responses, and authentication notes.

### Finance Tracker

- **Test File:** `test_finance.py`
- **Docs:** `Finance_Test_Documentation.md`
- **Covers:** Transactions, goals, finance endpoints, JWT auth
- **How to use:** Use the doc for request/response examples and test flows.

### LLM Chat Sessions

- **Test File:** `test_llm_chat_sessions.py`
- **Docs:** `LLM_Chat_Session_Test_Documentation.md`
- **Covers:** Chat messaging, session history, summaries, JWT auth
- **How to use:** See doc for payloads, endpoints, and test logic.

### Notifications

- **Test File:** `test_notifications.py`
- **Docs:** `Notifications_Test_Documentation.md`
- **Covers:** Notification delivery, marking as read, login, JWT auth
- **How to use:** Reference doc for test flows and API details.

### Parent Dashboard

- **Test File:** `test_parent_dashboard.py`
- **Docs:** `Parent_Dashboard_Test_Documentation.md`
- **Covers:** Parent-child task access, mood summaries, role-based auth
- **How to use:** See doc for setup, test cases, and expected results.

### Psychometry Assessment

- **Test File:** `test_psychometry.py`
- **Docs:** `Psychometry_Test_Documentation.md`
- **Covers:** Start/submit psychometry, results, JWT auth
- **How to use:** Use doc for API flows and test data.

### Task Tracker

- **Test File:** `test_task_tracker.py`
- **Docs:** `Task_Tracker_Test_Documentation.md`
- **Covers:** Homework/task CRUD, status updates, JWT auth
- **How to use:** See doc for endpoints, payloads, and test logic.

### Teacher Dashboard

- **Test File:** `test_teacher_dashboard.py`
- **Docs:** `Teacher_Dashboard_Test_Documentation.md`
- **Covers:** Student management, homework assignment, JWT/manual auth
- **How to use:** Reference doc for test cases and API usage.

### Remaining APIs & Health Tracker

- **Test Files:** `test_health_tracker.py`, others
- **Docs:** `Remaining_APIs_Test_Documentation.md`
- **Covers:** Health tasks, streaks, water tracking, and other child dashboard APIs
- **How to use:** See doc for endpoint coverage and test instructions.

> For each area, open the corresponding Markdown documentation in `backend/test_files/` for detailed test case steps, API payloads, and expected results. All tests are run using `pytest` from the `backend` directory.

## 🧪 Testing

This project includes tests for both the backend (Flask) and frontend (Vue.js).

### Backend (Flask) Testing

Run all backend tests using pytest:

```bash
cd ./backend
pytest
```

This command runs all Python tests in the `backend/test_files/` directory and outputs the results.

If you are at the project root, you can also run all tests directly with:

```bash
pytest
```

This will execute the entire backend test suite without additional flags.

> **Note:** Ensure you have installed all dependencies (`npm install` for frontend, `pip install -r requirements.txt` for backend) before running tests.

## 🚀 Deployment

### Netlify Deployment (Frontend)

The frontend is ready for deployment to Netlify with the following configuration:

1. **Quick Deployment:**

   ```bash
   # Windows
   deploy.bat

   # Linux/Mac
   ./deploy.sh
   ```

2. **Manual Steps:**

   - Deploy your backend to Heroku/Railway/etc.
   - Update `frontend/.env.production` with your backend URL
   - Push to GitHub and connect to Netlify
   - Set build settings: base `frontend/`, command `npm run build`, publish `frontend/dist/`
   - Add environment variables in Netlify dashboard

3. **Configuration Files:**
   - `netlify.toml` - Netlify configuration with redirects and headers
   - `frontend/.env.production` - Production environment variables
   - `frontend/vite.config.js` - Optimized build configuration

📖 **See [NETLIFY_DEPLOYMENT_GUIDE.md](NETLIFY_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.**

### Backend Deployment (Render) - READY FOR PRODUCTION! 🚀

The Flask backend is **fully configured** for Render deployment:

#### ✅ **What's Included:**

- **Complete `requirements.txt`** - All dependencies with proper versions
- **`Procfile`** - Render deployment configuration
- **`render.yaml`** - Infrastructure as Code setup
- **`wsgi.py`** - Production WSGI entry point
- **Deployment scripts** - `deploy-backend.sh` and `deploy-backend.bat`

#### 🎯 **Recommended Platform: Render**

- **Free Tier Available** - Perfect for testing and development
- **Auto-Deploy** - Connects directly to GitHub
- **PostgreSQL Support** - Production-ready database
- **SSL Certificates** - Automatic HTTPS
- **Easy Scaling** - Upgrade when needed

#### 📖 **Deployment Guide:**

**See [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) for complete step-by-step instructions.**

#### ⚡ **Quick Start:**

```bash
# Run the deployment preparation script
./deploy-backend.bat  # Windows
# or
./deploy-backend.sh   # Linux/Mac
```

#### 🔧 **Other Platforms:**

The backend can also be deployed to Heroku, Railway, DigitalOcean, or PythonAnywhere using the same `requirements.txt`.
