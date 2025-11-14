# Pet Adoption Management System

A comprehensive web-based database management system for pet adoption shelters, built with Flask and MySQL. This system provides role-based access control, automated workflows, and a user-friendly interface for managing pets, adoption applications, payments, and user accounts.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Role-Based Access Control](#role-based-access-control)
- [SQL Files](#sql-files)
- [Authors](#authors)

## Features

- **User Management**: Registration, authentication, and role-based access control
- **Pet Management**: Register, view, update, and delete pet records
- **Adoption Applications**: Submit and manage adoption applications with approval workflows
- **Payment Management**: Track and manage adoption payments
- **Dashboard Analytics**: View statistics and summaries for pets, applications, users, and payments
- **Role-Based Permissions**: Different access levels for admins, shelter workers, adopters, and general users
- **Stored Procedures & Triggers**: Automated business logic and data integrity enforcement
- **Responsive UI**: Modern, Bootstrap-based interface

## Technology Stack

- **Backend**: Python 3.x, Flask
- **Database**: MySQL 8.0
- **Database Connector**: PyMySQL, mysql-connector-python
- **Frontend**: HTML, CSS, Bootstrap
- **Environment Management**: python-dotenv

## Prerequisites

- Python 3.7 or higher
- MySQL 8.0 or higher
- pip (Python package manager)
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Pet-Adoption-Management-System
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

### Important: Branch Selection

- **For SQL Role-Based Access Control (RBAC)**: Switch to the `miniproject/RBAC` branch
  ```bash
  git checkout miniproject/RBAC
  ```
- **For standard setup**: Use the `main` branch
  ```bash
  git checkout main
  ```

### Standard Database Setup

1. **Create the database and tables**
   ```bash
   mysql -u root -p < sql/DDL_Commands_927_907.sql
   ```

2. **Create triggers, procedures, and functions**
   ```bash
   mysql -u root -p < sql/Trigger_Procedure_Function_927_907.sql
   ```

### SQL RBAC Setup (miniproject/RBAC branch only)

If you're on the `miniproject/RBAC` branch, additionally run:

```bash
mysql -u root -p < sql/Role_Based_Access_Control.sql
```

This will create MySQL roles and grant appropriate privileges for role-based access control at the database level.

## Configuration

1. **Create a `.env` file** in the project root directory:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASS=your_mysql_password
   DB_NAME=pet_adoption_db
   SECRET_KEY=your-secret-key-change-in-production
   ```

2. **Update the values** according to your MySQL configuration.

## Running the Application

1. **Activate your virtual environment** (if using one)
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Run the Flask application**
   ```bash
   python app.py
   ```

3. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - The application will redirect to the login page if not authenticated

## Project Structure

```
Pet-Adoption-Management-System/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
├── pages/                         # Page handlers
│   ├── auth.py                   # Authentication logic
│   ├── dashboard.py              # Dashboard data
│   ├── add_user.py               # User registration/management
│   ├── manage_pets.py             # Pet CRUD operations
│   ├── view_pets.py               # Pet viewing
│   ├── register_pet.py            # Pet registration
│   ├── add_application.py         # Adoption application submission
│   ├── manage_applications.py     # Application management
│   ├── manage_my_applications.py  # User's own applications
│   ├── manage_payments.py         # Payment management
│   ├── manage_users.py            # User management (admin)
│   ├── view_worker_applications.py # Worker role requests
│   ├── request_worker_role.py     # Request worker role
│   ├── view_all_data.py           # Admin data views
│   └── test_procedural_extensions.py # Test procedures/functions
├── templates/                      # HTML templates
│   ├── base.html                  # Base template
│   ├── login.html                 # Login page
│   ├── dashboard.html             # Dashboard
│   └── ...                        # Other page templates
├── static/                         # Static files
│   └── styles.css                  # Custom CSS
├── utils/                          # Utility modules
│   └── db.py                       # Database connection and query utilities
├── sql/                            # SQL scripts
│   ├── DDL_Commands_927_907.sql   # Database schema and seed data
│   ├── Trigger_Procedure_Function_927_907.sql # Procedures, functions, triggers
│   └── Role_Based_Access_Control.sql # RBAC setup (RBAC branch only)
└── Reports/                        # Project documentation
    ├── ER_RelationalDiagram_927_907.pdf
    ├── DDL_DML_927_907.pdf
    └── TRIGGERS_PROCEDURES_FUNCTIONS_927_907.pdf
```

## Role-Based Access Control

The system supports four user roles with different permissions:

### Admin
- Full system access
- User management
- All pet and application operations
- Payment management
- View all data and analytics
- Manage worker role requests

### Shelter Worker
- Register and manage pets
- Manage adoption applications
- Process payments
- View all data
- Request role upgrades

### Adopter / General User
- View available pets
- Submit adoption applications
- View own applications
- Request worker role

### SQL-Level RBAC (miniproject/RBAC branch)

On the `miniproject/RBAC` branch, the system implements MySQL-level role-based access control. Each application role maps to a MySQL role with specific database privileges:

- `admin_role`: Full privileges on all tables
- `shelter_worker_role`: CRUD on pets, applications, payments
- `adopter_role`: Read pets, create applications
- `general_role`: Read-only access to pets

The application automatically sets the appropriate MySQL role for each database connection based on the user's application role.

## SQL Files

- **DDL_Commands_927_907.sql**: Contains all table definitions, constraints, views, and seed data
- **Trigger_Procedure_Function_927_907.sql**: Contains stored procedures, functions, and triggers for business logic
- **Role_Based_Access_Control.sql**: MySQL roles and privileges (available on `miniproject/RBAC` branch)

## Authors

- **Shakirth Anisha**
- **Samridhi Shreya**

## Notes

- The application uses session-based authentication
- Database logs are written to `db_log.txt` in the project root
- All timestamps are automatically managed by the database
- The system includes automated triggers for data integrity and logging

## Troubleshooting

- **Database connection errors**: Verify your `.env` file has correct MySQL credentials
- **Import errors**: Ensure all Python dependencies are installed via `pip install -r requirements.txt`
- **SQL errors**: Make sure you've run the SQL scripts in the correct order (DDL first, then triggers/procedures)
- **RBAC errors**: If using RBAC features, ensure you're on the `miniproject/RBAC` branch and have run `Role_Based_Access_Control.sql`
