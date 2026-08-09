# Product API – Lab 10

A RESTful Product Catalog API built with **FastAPI**, **SQLAlchemy**, **PostgreSQL/SQLite**, **Docker**, and **Pytest**.

## Features

* Product CRUD operations
* User authentication
* Protected API endpoints
* Database integration
* Automated API tests
* Docker support
* CI workflow with GitHub Actions
* API documentation using Swagger UI

## Technologies Used

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **Pydantic**
* **Pytest**
* **PostgreSQL**
* **Docker**
* **GitHub Actions**

## Project Structure

```text
product-api-lab10/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_main.py
│   └── test_products.py
│
├── .gitignore
├── Dockerfile
├── main.py
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Frankline912/product-api-lab10.git
cd product-api-lab10
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

Start the FastAPI development server:

```bash
python -m uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Running Tests

Run all tests with:

```bash
pytest -v
```

The test suite covers authentication and product API functionality.

## Docker

Build the Docker image:

```bash
docker build -t product-api-lab10 .
```

Run the container:

```bash
docker run -p 8000:8000 product-api-lab10
```

The API can then be accessed at:

```text
http://127.0.0.1:8000
```

## Environment Variables

Sensitive configuration is stored in a `.env` file.

The `.env` file is intentionally excluded from Git using `.gitignore`.

Do not commit passwords, secret keys, or other sensitive credentials to the repository.

## GitHub Actions

The project includes a GitHub Actions workflow located at:

```text
.github/workflows/ci.yml
```

The workflow automatically runs the project's tests when changes are pushed to GitHub.

## Author

**Frankline912**

Business Information Technology Student
