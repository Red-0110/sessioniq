# SessionIQ

SessionIQ is a training performance tracking web application designed for athletes who want to log workouts and analyze training load over time.

The app calculates training loads and provides insights such as:
- Acute:Chronic Workload Ratio (ACWR)
- Week over week load change
- Four (4) week training trends

## Live Demo
https://sessioniq-production.up.railway.app/login

## Features
- User authentication (register, login, logout)
- Activity management (e.g. Tennis, Climbing, Strength Training)
- Session logging with duration and RPE
- Automatic training load calculation
- Interactive dashboard with charts (Chart.js)
- CSV export of training data
- Secure per-user data isolation

## Tech Stack
- **Backend:** Flask, SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend:** Jinja2, HTML/CSS, Chart.js
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Deployment:** Render
- **Auth & Security:** Password hashing, CSRF protection

## Why this project?
This project demonstrates full-stack fundamentals:
- Relational data modeling
- Authentication and authorization
- Server-side rendering
- Analytics logic (rolling windows, ACWR)
- Production deployment practices

## Setup (Local)
```bash
git clone https://github.com/<your-username>/sessioniq.git
cd sessioniq
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py

