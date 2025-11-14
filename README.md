# 🔥 Fire Detection System

A comprehensive Django-based web application for managing fire detection projects, zones, and RTSP cameras with role-based access control.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Management](#database-management)
- [API Endpoints](#api-endpoints)
- [Security](#security)
- [Contributing](#contributing)

## 🎯 Overview

The Fire Detection System is a web application designed to manage fire detection infrastructure through a hierarchical structure of Projects → Zones → Cameras. The system supports multiple user roles (Admin, Supervisor, Agent) with role-specific dashboards and permissions.

### Key Components

- **Projects**: High-level fire detection initiatives with status tracking
- **Zones**: Geographic areas within projects with polygon coordinates
- **Cameras**: RTSP-enabled cameras assigned to zones for fire monitoring
- **Agents**: Field agents assigned to projects for monitoring and response

## ✨ Features

### Authentication & Authorization
- ✅ Email-based authentication (no username required)
- ✅ Role-based access control (Admin, Supervisor, Agent)
- ✅ Account activation via email link
- ✅ Session-based authentication
- ✅ Protected routes with role-based decorators
- ✅ Secure password storage (hashed)

### Project Management
- ✅ Create and manage fire detection projects
- ✅ Project status tracking (Planned, In Progress, Completed, Cancelled)
- ✅ Supervisor assignment to projects
- ✅ Agent assignment to projects
- ✅ Project detail views with zones and cameras

### Zone & Camera Management
- ✅ Create zones within projects with polygon coordinates (JSON)
- ✅ Add RTSP cameras to zones
- ✅ Support for custom RTSP URLs or IP-based configuration
- ✅ Camera metadata (IP address, port, path, description)
- ✅ Zone and camera visualization

### User Management
- ✅ Agent profile management
- ✅ Agent assignment to projects
- ✅ Role-specific dashboards
- ✅ User activation workflow

## 🛠 Technology Stack

- **Backend**: Django 5.2.7
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Frontend**: Bootstrap (responsive UI)
- **Python**: 3.10+
- **Authentication**: Django's built-in session authentication
- **Camera Protocol**: RTSP (Real-Time Streaming Protocol)

## 📁 Project Structure

```
fire_detection/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database (not in git)
├── fire_detection/          # Main Django project package
│   ├── settings.py          # Project settings
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── accounts/                # Authentication app
│   ├── models.py            # CustomUser model (email-based)
│   ├── views.py             # Login, register, dashboards
│   ├── forms.py             # User registration/login forms
│   ├── decorators.py        # Role-based access decorators
│   └── templates/           # Auth templates
├── agents/                  # Agent management app
│   ├── models.py            # AgentProfile model
│   ├── views.py             # Agent CRUD operations
│   └── templates/           # Agent templates
└── projects/                # Project management app
    ├── models.py            # Project, Zone, Cam models
    ├── views.py             # Project/Zone/Cam CRUD
    ├── forms.py             # Project forms
    ├── templatetags/        # Custom template tags
    └── templates/           # Project templates
```

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd firedetection
```

#### 2. Navigate to Project Directory

```powershell
# Windows PowerShell
cd fire_detection
```

#### 3. Create Virtual Environment

```powershell
python -m venv .venv
```

#### 4. Activate Virtual Environment

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

#### 5. Install Dependencies

```powershell
# From project root
pip install -r ..\requirments.txt

# Or install directly
pip install Django==5.2.7
```

#### 6. Set Environment Variables

```powershell
# Windows PowerShell
$env:DJANGO_SECRET_KEY = 'your-secret-key-here'

# Linux/Mac
export DJANGO_SECRET_KEY='your-secret-key-here'
```

**⚠️ Important**: Generate a strong secret key for production. You can use:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 7. Run Migrations

```bash
python manage.py migrate
```

#### 8. Create Superuser

```bash
python manage.py createsuperuser --email admin@example.com
```

#### 9. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## ⚙️ Configuration

### Settings File

Key settings in `fire_detection/settings.py`:

- `AUTH_USER_MODEL = 'accounts.CustomUser'` - Custom user model
- `LOGIN_URL = 'login'` - Login redirect
- `LOGIN_REDIRECT_URL = '/'` - Post-login redirect
- `EMAIL_BACKEND` - Console backend for development

### Database Configuration

By default, the project uses SQLite. For production, update `DATABASES` in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📖 Usage

### Accessing the Application

1. **Register**: Visit `http://127.0.0.1:8000/accounts/register/`
2. **Login**: Visit `http://127.0.0.1:8000/accounts/login/`
3. **Admin Panel**: Visit `http://127.0.0.1:8000/admin/`

### User Roles

#### Admin
- Full system access
- User management
- Project oversight
- Dashboard: `/accounts/dashboard/admin/`

#### Supervisor
- Create and manage projects
- Assign agents to projects
- Manage zones and cameras
- Dashboard: `/accounts/dashboard/supervisor/`

#### Agent
- View assigned projects
- Monitor cameras
- Dashboard: `/accounts/dashboard/agent/`

### Workflow Example

1. **Supervisor** creates a new project
2. **Supervisor** adds zones to the project (with polygon coordinates)
3. **Supervisor** adds RTSP cameras to zones
4. **Supervisor** assigns agents to the project
5. **Agents** monitor cameras and respond to alerts

## 🗄 Database Management

### Using Django Admin

```bash
python manage.py createsuperuser
python manage.py runserver
# Visit: http://127.0.0.1:8000/admin/
```

### Using Django Shell

```bash
python manage.py shell
```

```python
# List all users
from accounts.models import CustomUser
CustomUser.objects.all()

# Find users by role
CustomUser.objects.filter(user_type='admin')

# List projects
from projects.models import Project
Project.objects.all()

# List cameras
from projects.models import Cam
Cam.objects.all()
```

### Direct Database Access (SQLite)

```bash
python manage.py dbshell
```

```sql
-- View users
SELECT * FROM accounts_customuser;

-- View projects
SELECT * FROM projects_project;

-- View cameras
SELECT * FROM projects_cam;
```

## 🔗 API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/accounts/register/` | GET, POST | User registration |
| `/accounts/login/` | GET, POST | User login |
| `/accounts/logout/` | POST | User logout |
| `/accounts/activate/<uidb64>/<token>/` | GET | Account activation |

### Dashboards

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/accounts/dashboard/admin/` | GET | Admin dashboard | Admin only |
| `/accounts/dashboard/supervisor/` | GET | Supervisor dashboard | Supervisor only |
| `/accounts/dashboard/agent/` | GET | Agent dashboard | Agent only |

### Projects

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/projects/create/` | GET, POST | Create new project |
| `/projects/list/` | GET | List all projects |
| `/projects/<id>/` | GET | Project details |
| `/projects/<id>/delete/` | POST | Delete project |

### Zones

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/projects/add_zone/<project_id>/` | GET, POST | Add zone to project |

### Cameras

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/projects/add_cam/<zone_name>/` | GET, POST | Add camera to zone |

### Agents

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents/add/` | GET, POST | Add new agent |
| `/agents/list/` | GET | List all agents |

## 🔒 Security

### Best Practices Implemented

- ✅ CSRF protection on all forms
- ✅ Password hashing (Django's PBKDF2)
- ✅ Session-based authentication
- ✅ Role-based access control
- ✅ Secure password validation
- ✅ Environment variable for SECRET_KEY

### Security Recommendations

1. **Never commit** `db.sqlite3` or `.env` files
2. **Rotate SECRET_KEY** if accidentally committed
3. **Use HTTPS** in production
4. **Set DEBUG=False** in production
5. **Configure ALLOWED_HOSTS** for production
6. **Use strong passwords** for superuser accounts
7. **Regular security updates** for Django and dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write docstrings for functions and classes
- Add tests for new features
- Update documentation as needed

## 📝 Notes

- The project uses SQLite by default for easy development
- Email backend is set to console for development (emails print to terminal)
- RTSP camera URLs can be configured as full URLs or IP-based
- Zone coordinates are stored as JSON for polygon shapes
- Database migrations are included in each app's `migrations/` folder

## 📄 License

[Specify your license here]

## 👥 Authors

[Your name/team]

## 🙏 Acknowledgments

- Django framework and community
- Bootstrap for UI components

---

**⚠️ Important Reminders:**

- Do NOT commit `.venv/`, `db.sqlite3`, or `.env` files
- Always set `DJANGO_SECRET_KEY` via environment variable
- Use a production-ready database (PostgreSQL) for deployment
- Configure proper email backend for production
