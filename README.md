# Clientora

Clientora is a lightweight Customer Relationship Management (CRM) system designed to manage contacts, deals, and business activities through a simple web interface and a FastAPI backend.

The project is structured with a **FastAPI backend** and a **static HTML/CSS frontend** that communicates with the backend through HTTP APIs.

---

# Project Structure

```
Clientora
│
├── backend/              # FastAPI application
│   ├── main.py           # Application entry point
│   ├── database.py       # Database configuration
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   ├── auth.py           # Authentication logic
│   ├── dependencies.py   # Shared dependencies
│   │
│   └── routers/
│       ├── auth.py
│       ├── contacts.py
│       ├── deals.py
│       └── dashboard.py
│
├── frontend/             # Client-side interface
│   ├── index.html        # Login page
│   ├── dashboard.html    # CRM dashboard
│   └── css/
│       └── style.css
│
├── README.md
└── .gitignore
```

---

# Backend

The backend is built using **FastAPI** and provides REST APIs that power the CRM.

## Features

* User authentication
* Contact management
* Deal management
* Dashboard data aggregation
* Structured API routing
* Database abstraction layer

## Core Components

### `main.py`

Entry point of the FastAPI application.
Responsible for:

* Creating the FastAPI app
* Registering routers
* Starting the server

### `database.py`

Handles the database connection and session management.

### `models.py`

Defines the database tables used by the application.

Typical entities include:

* Users
* Contacts
* Deals

### `schemas.py`

Defines the request and response structures using **Pydantic models**.

These ensure:

* Input validation
* Structured API responses

### `auth.py`

Handles authentication logic such as:

* Login validation
* Password handling
* Token generation

### `dependencies.py`

Contains reusable dependencies used by routes, such as:

* Database session injection
* Authentication guards

### Routers

Routers separate the API into logical modules.

**auth.py**

Handles user authentication endpoints.

Example:

```
POST /login
POST /register
```

**contacts.py**

Manages customer contacts.

Example:

```
GET /contacts
POST /contacts
DELETE /contacts/{id}
```

**deals.py**

Manages business deals and pipeline stages.

Example:

```
GET /deals
POST /deals
UPDATE /deals/{id}
```

**dashboard.py**

Provides aggregated data for the dashboard.

Example:

```
GET /dashboard
```

---

# Frontend

The frontend provides a simple web interface for interacting with the CRM.

It is built using:

* HTML
* CSS
* JavaScript (via browser API requests)

The frontend communicates with the backend through HTTP requests.

## Pages

### `index.html`

Login page for accessing the CRM.

Responsibilities:

* Collect user credentials
* Send login request to the backend
* Redirect authenticated users to the dashboard

---

### `dashboard.html`

Main application interface.

Displays:

* Contacts
* Deals
* Dashboard statistics

The page fetches data from the backend API and renders it dynamically.

---

### `css/style.css`

Provides styling for the entire frontend interface.

Includes styles for:

* Layout
* Navigation
* Forms
* Dashboard components

---

# Running the Project

## 1. Start the Backend

Navigate to the backend directory:

```
cd backend
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the server:

```
uvicorn main:app --reload
```

The API will start at:

```
http://127.0.0.1:8000
```

---

## 2. Open the Frontend

Navigate to the `frontend` folder and open:

```
index.html
```

in your browser.

You can also serve it with a simple server:

```
python -m http.server
```

---

# Future Improvements

Possible improvements for the project include:

* JavaScript frontend framework integration
* Role-based authentication
* Workflow automation
* Activity tracking
* File attachments for contacts and deals
* Real-time updates

---

# License

This project is currently under development.
