# SE Project - Life Skills App for School-Aged Children

Software Engineering Project - May 2025, Team 25

## Problem Statement
**Problem Statement 2: Life Skills App for School-Aged Children**

Design and build a web or mobile application aimed at helping school-aged children (roughly ages 8–14) develop essential life skills. These might include time management, emotional intelligence, financial literacy, communication, or healthy habits. You are required to actually talk to users to identify genuine concerns and propose features that directly respond to those concerns. Choose a skill area that is age-appropriate and impactful, and create a solution that engages and supports kids in learning or practicing that skill.

## Project Structure

```
├── backend/                    # Flask backend application
│   ├── app.py                 # Main Flask application
│   ├── models.py              # Database models
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── instance/              # Database files
│   ├── static/                # Static assets (images, drawings)
│   └── services/              # Backend services
│       └── psychometry.py     # Assessment engine
├── frontend/                   # Vue.js frontend application
│   ├── src/                   # Source code
│   ├── public/                # Public assets
│   └── package.json           # Node.js dependencies
├── run_backend.py             # Backend entry point
└── package.json               # Root project configuration
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

## Features
- Session-based chatbot with mood detection
- Drawing and creative activities
- Health tracking and wellness modules
- Psychometric assessments
- Parent-child interaction features
- Teacher dashboard for educational content
