# Casting Agency API

## Project Description

The **Casting Agency API** is a RESTful web service for managing movies and actors in a film production company. It provides endpoints for creating, reading, updating, and deleting movies and actors, with strict role-based access control (RBAC) enforced via Auth0. The API is designed to help executive producers, casting directors, and casting assistants securely manage creative assets and personnel.

### Motivation

Film production companies need secure, scalable tools to manage their creative data. This API demonstrates:
- Secure RESTful API design with Flask and Python
- Integration of RBAC using Auth0 and JWTs
- Best practices for API documentation, testing, and deployment

---

## Hosted API

**Production URL:**  
`https://casting-agency-api-pnv9.onrender.com`  

---

## Project Dependencies

- Python 3.6+
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- psycopg2-binary (for PostgreSQL)
- python-jose (for JWT handling)
- Auth0 (for authentication and RBAC)
- pytest or unittest (for testing)

---

## Local Development & Hosting Instructions

### 1. Clone the Repository

git clone https://github.com/steff32/casting-agency-api.git
cd casting-agency-api

### 2. Set Up a Virtual Environment

python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate


### 3. Install Dependencies

pip install -r requirements.txt

### 4. Configure Environment Variables
This project uses a shell script, `setup.sh`, to set all required environment variables. Change the variables' values as required.

**To set up your environment variables, run:**

source setup.sh

This will export all necessary variables for your Flask app, including database and Auth0 configuration.


### 5. Database Setup

Create your PostgreSQL database and initialize tables (for local testing)

In Python shell or as a script:
from models import db_drop_and_create_all
db_drop_and_create_all()


### 6. Run the Development Server

After running `source setup.sh`, start the Flask app:
export FLASK_APP=app.py
export FLASK_ENV=development
flask run

The API will be available at `http://localhost:5000/` if running locally.

---

## Authentication & RBAC Setup

### 1. Auth0 Configuration

- Create an Auth0 account at [auth0.com](https://auth0.com/).
- Register a new API in the Auth0 dashboard.
  - **Identifier**: `agency` (or your chosen audience)
  - **Domain**: e.g., `dev-xxxxxx.us.auth0.com`
- Create roles and permissions in Auth0:
  - **Casting Assistant**: `view:actors`, `view:movies`
  - **Casting Director**: All above, plus `add:actors`, `update:actors`, `delete:actors`, `update:movies`
  - **Executive Producer**: All above, plus `add:movies`, `delete:movies`
- Assign users to roles in Auth0.

### 2. Obtain JWT Tokens

- Use Auth0’s dashboard or the `/authorize` endpoint to log in as users with different roles.
- Use the resulting JWT access tokens in the `Authorization` header for API requests:

Authorization: Bearer <JWT_TOKEN>

---

## API Endpoints & RBAC Controls

| Endpoint                   | Methods | Permissions Required        | Description                      |
|----------------------------|---------|----------------------------|----------------------------------|
| `/movies`                  | GET     | `view:movies`              | List all movies                  |
| `/actors`                  | GET     | `view:actors`              | List all actors                  |
| `/movies`                  | POST    | `add:movies`               | Add a new movie                  |
| `/actors`                  | POST    | `add:actors`               | Add a new actor                  |
| `/movies/<int:movie_id>`   | PATCH   | `update:movies`            | Update a movie                   |
| `/actors/<int:actor_id>`   | PATCH   | `update:actors`            | Update an actor                  |
| `/movies/<int:movie_id>`   | DELETE  | `delete:movies`            | Delete a movie                   |
| `/actors/<int:actor_id>`   | DELETE  | `delete:actors`            | Delete an actor                  |

### RBAC Role Matrix

| Role                | Permissions                                                                                         |
|---------------------|-----------------------------------------------------------------------------------------------------|
| Casting Assistant   | `view:actors`, `view:movies`                                                                        |
| Casting Director    | All Casting Assistant perms + `add:actors`, `update:actors`, `delete:actors`, `update:movies`       |
| Executive Producer  | All Casting Director perms + `add:movies`, `delete:movies`                                          |

---

## Example Requests

**Get Movies**
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://localhost:5000/movies


**Add Actor**
curl -X POST -H "Authorization: Bearer <EXEC_PRODUCER_TOKEN>"
-H "Content-Type: application/json"
-d '{"name": "Jane Doe", "age": 30, "gender": "Female"}'
http://localhost:5000/actors


---

## Running Tests

python -m unittest test_app.py

or, if using pytest:
pytest test_app.py

