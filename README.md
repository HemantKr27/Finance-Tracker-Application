# Finance Tracker API

## Description

Finance Tracker API is a backend-focused personal finance management application built using FastAPI and PostgreSQL. It allows users to register securely, manage financial accounts, record income and expenses, organize transactions with categories, and set budgets for better spending control. The project is designed with a production-style backend structure using RESTful APIs, database relationships, validation, authentication, and migration support.

## Features

- User registration and login with JWT authentication
- Secure password hashing and protected API routes
- Account creation and management
- Income and expense transaction tracking
- Category-based transaction organization
- Budget creation and budget monitoring
- Category-wise budget allocation
- Input validation using Pydantic
- Database modeling and relationships using SQLAlchemy
- Database schema migrations using Alembic
- Docker-ready backend setup

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Authentication:** JWT
- **Migrations:** Alembic
- **Containerization:** Docker

## Project Structure

app/
├── api/
│   ├── deps.py
│   └── v1/
│       ├── endpoints/
│       └── router.py
├── core/
│   ├── config.py
│   └── security.py
├── crud/
├── db/
│   ├── base.py
│   ├── dependencies.py
│   ├── init_db.py
│   └── session.py
├── models/
├── schemas/
└── main.py

• api/ contains route definitions and API versioning
• core/ contains configuration and security logic
• crud/ contains database operation logic
• db/ contains database setup, session, and initialization
• models/ contains SQLAlchemy models
• schemas/ contains Pydantic request and response schemas

##Database Design

The application is built around the following core entities:

User: stores user credentials and account ownership
Account: stores financial accounts such as cash, bank, or wallet
Category: stores transaction categories such as food, salary, rent, or transport
Transaction: stores user income and expense records
Budget: stores user-defined budget plans
BudgetCategory: stores category-wise budget allocation inside a budget

##ER Diagram / Relationships

#Main Relationships

One user can have many accounts
One user can have many transactions
One user can have many categories
One user can have many budgets
One account belongs to one user
One transaction belongs to one account
One transaction belongs to one category
One budget belongs to one user
One budget can have multiple category allocations through BudgetCategory

##Installation
1. Clone the repository
git clone https://github.com/your-username/finance-tracker-api.git
cd finance-tracker-api

2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

For Windows:
.venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Run database migrations
alembic upgrade head

5. Environment Variables

#Create a .env file in the project root and add the required environment variables:

PROJECT_NAME=Finance Tracker API
DATABASE_URL=postgresql://postgres:password@localhost:5432/finance_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_ISSUER=finance-tracker
JWT_AUDIENCE=finance-users

6. Run the App

Start the FastAPI application with:
uvicorn app.main:app --reload

7. API Docs

After running the server, API documentation is available at:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

8. Main Endpoints

Auth
POST /api/v1/auth/register — Register a new user
POST /api/v1/auth/login — Login and receive access token

Accounts
POST /api/v1/accounts/ — Create a new account
GET /api/v1/accounts/ — Get all user accounts

Transactions
POST /api/v1/transactions/ — Add a new transaction
GET /api/v1/transactions/ — Get all user transactions

Categories
POST /api/v1/categories/ — Create a category
GET /api/v1/categories/ — Get user categories

Budgets
POST /api/v1/budgets/ — Create a budget
GET /api/v1/budgets/ — Get all budgets

9. Workflow

User registers and logs in to the application
User creates an account such as Cash, Bank, or Wallet
User adds income and expense transactions
User organizes transactions using categories
User creates budgets to manage spending
User allocates amounts to specific categories inside a budget
User tracks financial activity and budget usage through API responses
