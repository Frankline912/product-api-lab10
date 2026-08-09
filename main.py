
from fastapi import FastAPI, Depends, HTTPException, status, Form
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

    id = Column(Integer, primary_key=True, index=True)

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
# ROOT ENDPOINT
# =========================

@app.get("/")
def root():
    return {
        "message": "Product API is running"
    }


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
