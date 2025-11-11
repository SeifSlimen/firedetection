# Fire Detection System - Authentication Module

## What We Built
A secure role-based authentication system where users can:
- Register with email (no username needed)
- Have specific roles (Admin/Supervisor/Agent)
- Access role-specific dashboards
- Use a modern Bootstrap UI

## Database Access & Management

### View Database (SQLite)
1. Using Django Admin:
   ```bash
   # Create admin user first
   python manage.py createsuperuser
   # Run server and visit
   python manage.py runserver
   # Go to: http://127.0.0.1:8000/admin/
   ```

2. Using Django Shell:
   ```bash
   python manage.py shell
   
   # List all users
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> User.objects.all()
   
   # Find specific user
   >>> User.objects.filter(email="example@email.com")
   
   # Check user roles
   >>> User.objects.values('email', 'user_type')
   ```

3. Direct Database Access (SQLite):
   ```bash
   # Open SQLite console
   python manage.py dbshell
   
   # View users table
   SELECT * FROM accounts_customuser;
   
   # View active users
   SELECT email, user_type, is_active FROM accounts_customuser WHERE is_active=1;
   ```

### Database Location
- Main database: `fire_detection/db.sqlite3`
- User table: `accounts_customuser`
- Sessions table: `django_session`

## Key Features

### 1. Authentication
- Email & password login
- Account activation via link
- Session-based (more secure than JWT)
- Automatic logout on browser close

### 2. Role System
- Three roles: Admin, Supervisor, Agent
- Each role has its own dashboard
- Role-specific navigation and features
- Protected routes by role

### 3. Security
- Server-side sessions (nothing sensitive in browser)
- CSRF protection on all forms
- Password strength checking
- Secure password storage (hashed)

### 4. User Interface
- Clean, modern Bootstrap design
- Mobile-responsive
- Password strength meter
- Loading states and feedback

## Quick Demo Steps
1. Start server: `python manage.py runserver`
2. Register: http://127.0.0.1:8000/accounts/register/
3. Activate account via link
4. Login: http://127.0.0.1:8000/accounts/login/
5. See your role-specific dashboard

## Pages & URLs
- `/accounts/register/` - Sign up
- `/accounts/login/` - Sign in
- `/accounts/dashboard/admin/` - Admin area
- `/accounts/dashboard/supervisor/` - Supervisor area
- `/accounts/dashboard/agent/` - Agent area