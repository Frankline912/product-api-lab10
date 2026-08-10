from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional


# =========================
# APP CONFIGURATION
# =========================

app = FastAPI(title="Product API")

DATABASE_URL = "sqlite:///./product_api.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# =========================
# DATABASE SESSION
# =========================

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# SECURITY
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# =========================
# USER MODEL
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    full_name = Column(
        String,
        nullable=False
    )

    hashed_password = Column(
        String,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )


# =========================
# PRODUCT MODEL
# =========================

class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    price = Column(
        Float,
        nullable=False
    )

    stock = Column(
        Integer,
        default=0
    )


# Create tables
Base.metadata.create_all(bind=engine)


# =========================
# SCHEMAS
# =========================

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int

    class Config:
        from_attributes = True


# =========================
# PORTFOLIO HOMEPAGE
# =========================

@app.get("/", response_class=HTMLResponse)
async def portfolio():

    html_content = """
    <!DOCTYPE html>
    <html>

    <head>
        <title>Student Portfolio - Backend Assignments</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f5f5f5;
            }

            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }

            .student-info {
                background: #e8f4fd;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }

            .assignment {
                margin: 12px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }

            .assignment a {
                color: #0366d6;
                text-decoration: none;
                font-weight: 500;
            }

            .assignment a:hover {
                text-decoration: underline;
            }

            .lesson-topic {
                color: #7f8c8d;
                font-size: 0.9em;
            }

            .footer {
                margin-top: 30px;
                text-align: center;
                color: #95a5a6;
                font-size: 0.9em;
                border-top: 1px solid #ecf0f1;
                padding-top: 20px;
            }
        </style>
    </head>

    <body>

    <div class="container">

        <h1>📚 Backend Development Portfolio</h1>

        <div class="student-info">

            <p>
                <strong>Student Name:</strong>
                FRANKLINE MUCHUI MUTUA
            </p>

            <p>
                <strong>Student Registration Number:</strong>
                C027-01-0872/2024
            </p>

            <p>
                <strong>Student Email:</strong>
                frankline.muchui@students.dkut.ac.ke
            </p>

        </div>

        <h2>📝 Backend Assignments</h2>

        <p>
            Click on any assignment to view the complete code on GitHub.
        </p>


        <!-- LA1 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/gighub.api" target="_blank">
                <strong>LA1</strong>
                — HTTP & Your First API
            </a>

            <span class="lesson-topic">
                — FastAPI + Uvicorn, HTTP Methods, Status Codes
            </span>
        </div>


        <!-- LA2 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/cit-backend-course" target="_blank">
                <strong>LA2</strong>
                — Docker - Packaging Your API
            </a>

            <span class="lesson-topic">
                — Containers, Dockerfiles, Docker Compose
            </span>
        </div>


        <!-- LA3 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/library-api" target="_blank">
                <strong>LA3</strong>
                — Routing, Parameters & Request Bodies
            </a>

            <span class="lesson-topic">
                — Path Parameters, Query Parameters, Pydantic Validation
            </span>
        </div>


        <!-- LA4 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/healthtrack-api" target="_blank">
                <strong>LA4</strong>
                — PostgreSQL & SQLModel – Your First Database
            </a>

            <span class="lesson-topic">
                — ORM, Database Migrations, SQLModel
            </span>
        </div>


        <!-- LA5 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/product-api" target="_blank">
                <strong>LA5</strong>
                — CRUD Operations
            </a>

            <span class="lesson-topic">
                — Create, Read, Update, Delete with Error Handling
            </span>
        </div>


        <!-- LA6 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/product-api" target="_blank">
                <strong>LA6</strong>
                — Error Handling & Validation
            </a>

            <span class="lesson-topic">
                — HTTPException, Custom Validators, Global Handlers
            </span>
        </div>


        <!-- LA7 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/healthtrack-api" target="_blank">
                <strong>LA7</strong>
                — User Authentication – JWT & Password Hashing
            </a>

            <span class="lesson-topic">
                — JWT Tokens, bcrypt, Login/Register Endpoints
            </span>
        </div>


        <!-- LA8 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/clinicguard-api" target="_blank">
                <strong>LA8</strong>
                — Authorization & Rate Limiting
            </a>

            <span class="lesson-topic">
                — RBAC, Dependency Injection, Rate Limiting
            </span>
        </div>


        <!-- LA9 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/sendit-api" target="_blank">
                <strong>LA9</strong>
                — File Uploads & External APIs
            </a>

            <span class="lesson-topic">
                — File Validation, httpx, Environment Variables
            </span>
        </div>


        <!-- LA10 -->

        <div class="assignment">
            <a href="https://github.com/Frankline912/product-api-lab10" target="_blank">
                <strong>LA10</strong>
                — Testing & Deployment (Cloud)
            </a>

            <span class="lesson-topic">
                — Pytest, CI/CD, Render Deployment
            </span>
        </div>


        <div class="footer">

            <p>
                Deployed on Render | Last Updated: August 2026
            </p>

            <p>
                Click on any assignment link to view the complete
                source code on GitHub
            </p>

        </div>

    </div>

    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


# =========================
# AUTHENTICATION ENDPOINTS
# =========================

@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_session)
):

    # Check username
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    # Check email
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(
            user_data.password
        ),
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post(
    "/login",
    response_model=Token
)
def login_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session)
):

    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user or not verify_password(
        password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# GET CURRENT USER
# =========================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise credentials_exception

    return user


# =========================
# PRODUCT ENDPOINTS
# =========================

@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@app.get(
    "/products",
    response_model=list[ProductResponse]
)
def get_products(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    return db.query(Product).all()


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@app.patch(
    "/products/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if product_data.name is not None:
        product.name = product_data.name

    if product_data.description is not None:
        product.description = product_data.description

    if product_data.price is not None:
        product.price = product_data.price

    if product_data.stock is not None:
        product.stock = product_data.stock

    db.commit()
    db.refresh(product)

    return product


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return None