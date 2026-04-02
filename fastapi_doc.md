# FastAPI Documentation: Beginner to Intermediate Guide

> **Target Audience:** Developers with 1–2 years of Python experience  
> **Prerequisites:** Basic Python, understanding of HTTP, some REST API knowledge

---

## Table of Contents

1. [What is FastAPI?](#1-what-is-fastapi)
2. [Installation & Setup](#2-installation--setup)
3. [Your First FastAPI App](#3-your-first-fastapi-app)
4. [Path Parameters](#4-path-parameters)
5. [Query Parameters](#5-query-parameters)
6. [Request Body & Pydantic Models](#6-request-body--pydantic-models)
7. [HTTP Methods (CRUD)](#7-http-methods-crud)
8. [Response Models & Status Codes](#8-response-models--status-codes)
9. [Data Validation with Pydantic](#9-data-validation-with-pydantic)
10. [Pydantic Field Validation](#10-pydantic-field-validation)
11. [Path & Query Parameter Validation](#11-path--query-parameter-validation)
12. [Handling Errors & HTTPException](#12-handling-errors--httpexception)
13. [Dependency Injection](#13-dependency-injection)
14. [Routers (APIRouter)](#14-routers-apirouter)
15. [Middleware](#15-middleware)
16. [Background Tasks](#16-background-tasks)
17. [File Uploads](#17-file-uploads)
18. [Authentication: OAuth2 & JWT](#18-authentication-oauth2--jwt)
19. [Database Integration (SQLAlchemy)](#19-database-integration-sqlalchemy)
20. [Async & Await in FastAPI](#20-async--await-in-fastapi)
21. [Testing FastAPI Applications](#21-testing-fastapi-applications)
22. [Project Structure Best Practices](#22-project-structure-best-practices)

---

## 1. What is FastAPI?

FastAPI is a modern, high-performance Python web framework for building APIs. It is built on top of **Starlette** (for the ASGI web server) and **Pydantic** (for data validation).

### Key Features

| Feature | Description |
|---|---|
| **Speed** | On par with NodeJS and Go — one of the fastest Python frameworks |
| **Auto Docs** | Automatic Swagger UI (`/docs`) and ReDoc (`/redoc`) generation |
| **Type hints** | Uses Python type hints for automatic validation and editor support |
| **Async support** | Native `async/await` support via ASGI |
| **Data validation** | Powered by Pydantic — validates and serializes data automatically |

### How FastAPI Compares

```
Flask      → Lightweight, but no built-in validation, sync only
Django     → Full-stack, heavier, not API-first
FastAPI    → API-first, async, modern, type-safe
```

---

## 2. Installation & Setup

### Install FastAPI and Uvicorn

```bash
pip install fastapi uvicorn
```

- **fastapi** — the web framework
- **uvicorn** — the ASGI server used to run your app (like Gunicorn for Django/Flask)

### Optional but recommended

```bash
pip install "fastapi[all]"
```

This installs extras like `python-multipart` (file uploads), `email-validator`, `jinja2`, etc.

### Verify Installation

```bash
python -c "import fastapi; print(fastapi.__version__)"
```

---

## 3. Your First FastAPI App

### Create `main.py`

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
```

### Run the Server

```bash
uvicorn main:app --reload
```

- `main` → the filename (`main.py`)
- `app` → the FastAPI instance inside that file
- `--reload` → restarts the server automatically on file changes (use in development only)

### Access the API

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Your endpoint |
| `http://127.0.0.1:8000/docs` | Swagger UI (interactive docs) |
| `http://127.0.0.1:8000/redoc` | ReDoc documentation |
| `http://127.0.0.1:8000/openapi.json` | Raw OpenAPI schema |

### How it Works

```
Client Request
     |
     v
Uvicorn (ASGI server)
     |
     v
FastAPI (routes the request to the correct function)
     |
     v
Your function runs → returns data
     |
     v
FastAPI serializes response to JSON
     |
     v
Client receives JSON response
```

---

## 4. Path Parameters

Path parameters are **variable parts of the URL path**.

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

- `{user_id}` in the path is a placeholder
- FastAPI automatically converts `user_id` to `int` and validates it
- If you pass `/users/abc`, FastAPI returns a `422 Unprocessable Entity` automatically

### Multiple Path Parameters

```python
@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

### Important: Order Matters for Fixed vs Dynamic Paths

```python
# This MUST come before the dynamic route
@app.get("/users/me")
def get_current_user():
    return {"user": "current user"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

If `/users/me` is declared after `/users/{user_id}`, the string `"me"` would fail `int` conversion and cause an error.

### Path Parameters with Enums (Restricted values)

```python
from enum import Enum

class Department(str, Enum):
    hr = "hr"
    engineering = "engineering"
    finance = "finance"

@app.get("/departments/{dept_name}")
def get_department(dept_name: Department):
    return {"department": dept_name}
```

Only `hr`, `engineering`, or `finance` will be accepted. Any other value returns a `422` error.

---

## 5. Query Parameters

Query parameters are the `?key=value` parts in a URL like `/items?skip=0&limit=10`.

```python
@app.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    fake_items = list(range(100))
    return fake_items[skip : skip + limit]
```

- Parameters with **default values** are optional query parameters
- Parameters **without** default values are required

### Optional Query Parameters

```python
from typing import Optional

@app.get("/search")
def search_items(q: Optional[str] = None):
    if q:
        return {"results": f"Searching for: {q}"}
    return {"results": "No query provided"}
```

### Combining Path and Query Parameters

```python
@app.get("/users/{user_id}/items")
def get_user_items(user_id: int, active: bool = True, limit: int = 5):
    return {"user_id": user_id, "active": active, "limit": limit}
```

Request: `GET /users/42/items?active=false&limit=3`

---

## 6. Request Body & Pydantic Models

When a client sends data (e.g., creating a resource), it sends a **request body** — typically as JSON.

### Define a Pydantic Model

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str = None   # optional field
    price: float
    in_stock: bool = True     # optional with default
```

### Use the Model in a Route

```python
@app.post("/items")
def create_item(item: Item):
    return {"message": "Item created", "item": item}
```

FastAPI will:
1. Read the JSON request body
2. Validate it against the `Item` model
3. Pass a typed `Item` object to your function
4. Return a 422 error automatically if validation fails

### Example JSON Body

```json
{
  "name": "Laptop",
  "description": "A high-performance laptop",
  "price": 999.99
}
```

### Accessing Model Fields

```python
@app.post("/items")
def create_item(item: Item):
    item_dict = item.dict()          # convert to Python dict
    item_dict["total"] = item.price * 1.18  # add calculated field
    return item_dict
```

---

## 7. HTTP Methods (CRUD)

FastAPI supports all standard HTTP methods. Here's a full CRUD example using an in-memory store:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

# In-memory "database"
items_db: Dict[int, Item] = {}
counter = 0

# CREATE
@app.post("/items", status_code=201)
def create_item(item: Item):
    global counter
    counter += 1
    items_db[counter] = item
    return {"id": counter, "item": item}

# READ ALL
@app.get("/items")
def list_items():
    return items_db

# READ ONE
@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

# UPDATE (full replacement)
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item
    return {"message": "Updated", "item": item}

# PARTIAL UPDATE
@app.patch("/items/{item_id}")
def partial_update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    stored = items_db[item_id].dict()
    update_data = item.dict(exclude_unset=True)   # only fields sent in the request
    stored.update(update_data)
    items_db[item_id] = Item(**stored)
    return items_db[item_id]

# DELETE
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
```

### HTTP Method Summary

| Method | Use Case | Request Body | Typical Status Codes |
|---|---|---|---|
| GET | Fetch data | No | 200 |
| POST | Create resource | Yes | 201 |
| PUT | Full update | Yes | 200 |
| PATCH | Partial update | Yes (partial) | 200 |
| DELETE | Remove resource | No | 204 |

---

## 8. Response Models & Status Codes

### Response Model

You can define what gets returned using `response_model`. This ensures sensitive fields are never accidentally exposed.

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str        # input includes password

class UserResponse(BaseModel):
    id: int
    username: str
    email: str           # password is NOT here — will be filtered out

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    # Simulate saving to DB
    return {"id": 1, "username": user.username, "email": user.email, "password": user.password}
    # Even though we return "password", response_model filters it out
```

### Status Codes

```python
from fastapi import status

@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    return item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    pass
```

### Common HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | OK — successful GET/PUT |
| 201 | Created — successful POST |
| 204 | No Content — successful DELETE |
| 400 | Bad Request — client sent invalid data |
| 401 | Unauthorized — not authenticated |
| 403 | Forbidden — authenticated but not authorized |
| 404 | Not Found |
| 422 | Unprocessable Entity — validation failed |
| 500 | Internal Server Error |

### Response with List

```python
from typing import List

@app.get("/items", response_model=List[UserResponse])
def get_all_users():
    return [{"id": 1, "username": "alice", "email": "alice@example.com"}]
```

---

## 9. Data Validation with Pydantic

Pydantic is the backbone of FastAPI's data validation. When you define a model, Pydantic ensures the data matches the types you specified.

### Basic Types

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Product(BaseModel):
    id: int
    name: str
    tags: List[str] = []
    price: float
    created_at: datetime
    is_available: Optional[bool] = None
```

### Nested Models

```python
class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    age: int
    address: Address      # nested model
```

Usage:

```json
{
  "name": "Alice",
  "age": 30,
  "address": {
    "street": "123 Main St",
    "city": "Hyderabad",
    "zip_code": "500001"
  }
}
```

### Model with Example (for Swagger Docs)

```python
class Item(BaseModel):
    name: str
    price: float

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Widget",
                "price": 29.99
            }
        }
```

---

## 10. Pydantic Field Validation

Use `Field` from Pydantic to add constraints and metadata to fields.

```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="Full name of the user")
    age: int = Field(ge=0, le=120, description="Age must be between 0 and 120")
    email: EmailStr                     # validates email format
    salary: float = Field(gt=0, description="Salary must be positive")
    bio: str = Field(default=None, max_length=500)
```

`pip install "pydantic[email]"` is required for `EmailStr`.

### Field Constraints Reference

| Argument | Applies to | Meaning |
|---|---|---|
| `min_length` | str | Minimum string length |
| `max_length` | str | Maximum string length |
| `gt` | int/float | Greater than |
| `ge` | int/float | Greater than or equal to |
| `lt` | int/float | Less than |
| `le` | int/float | Less than or equal to |
| `regex` | str | Must match regex pattern |
| `description` | all | Shown in Swagger docs |
| `default` | all | Default value |

---

## 11. Path & Query Parameter Validation

FastAPI lets you add validation to path and query parameters using `Path` and `Query`.

```python
from fastapi import Path, Query

@app.get("/users/{user_id}")
def get_user(
    user_id: int = Path(ge=1, description="User ID must be positive"),
    include_inactive: bool = Query(default=False, description="Include inactive users")
):
    return {"user_id": user_id, "include_inactive": include_inactive}
```

### Query with String Validation

```python
@app.get("/search")
def search(
    q: str = Query(min_length=3, max_length=50, description="Search query string")
):
    return {"query": q}
```

### Multiple Values for a Query Parameter

```python
from typing import List

@app.get("/filter")
def filter_items(tags: List[str] = Query(default=[])):
    return {"tags": tags}
```

Request: `GET /filter?tags=python&tags=fastapi&tags=web`

---

## 12. Handling Errors & HTTPException

### Raising HTTP Errors

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id > 100:
        raise HTTPException(
            status_code=404,
            detail=f"Item with ID {item_id} not found"
        )
    return {"item_id": item_id}
```

### Custom Error Response Headers

```python
raise HTTPException(
    status_code=403,
    detail="Not enough permissions",
    headers={"X-Error": "Authorization failed"}
)
```

### Custom Exception Handlers

For app-wide error handling, register exception handlers:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": f"Item {exc.item_id} does not exist"}
    )

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id > 100:
        raise ItemNotFoundError(item_id=item_id)
    return {"item_id": item_id}
```

### Validation Error Override

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)}
    )
```

---

## 13. Dependency Injection

Dependency Injection (DI) is one of FastAPI's most powerful features. It allows you to **share logic across routes** without repeating code.

### Simple Dependency

```python
from fastapi import Depends

def get_query_params(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@app.get("/items")
def read_items(params: dict = Depends(get_query_params)):
    return params

@app.get("/users")
def read_users(params: dict = Depends(get_query_params)):
    return params
```

Both routes now share the same pagination logic.

### Class-Based Dependencies

```python
class Pagination:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit

@app.get("/products")
def get_products(pagination: Pagination = Depends(Pagination)):
    return {"skip": pagination.skip, "limit": pagination.limit}
```

### Dependency with Database (Pattern for Later)

```python
def get_db():
    db = SessionLocal()
    try:
        yield db         # <-- yield means this is a generator dependency
    finally:
        db.close()       # cleanup runs after request finishes

@app.get("/users")
def get_users(db = Depends(get_db)):
    return db.query(User).all()
```

### Chained Dependencies

```python
def verify_token(token: str):
    if token != "secret":
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

def get_current_user(token: str = Depends(verify_token)):
    return {"user": "alice", "token": token}

@app.get("/profile")
def profile(user = Depends(get_current_user)):
    return user
```

### Global Dependencies (Applied to All Routes)

```python
def log_request(request: Request):
    print(f"Request to: {request.url}")

app = FastAPI(dependencies=[Depends(log_request)])
```

---

## 14. Routers (APIRouter)

As your app grows, you should split routes into separate files using `APIRouter`.

### Folder Structure

```
project/
├── main.py
├── routers/
│   ├── __init__.py
│   ├── users.py
│   └── items.py
```

### `routers/users.py`

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/users",          # all routes start with /users
    tags=["Users"],           # groups in Swagger UI
)

@router.get("/")
def list_users():
    return [{"id": 1, "name": "Alice"}]

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}

@router.post("/", status_code=201)
def create_user():
    return {"message": "User created"}
```

### `routers/items.py`

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)

@router.get("/")
def list_items():
    return [{"id": 1, "name": "Widget"}]
```

### `main.py`

```python
from fastapi import FastAPI
from routers import users, items

app = FastAPI()

app.include_router(users.router)
app.include_router(items.router)

@app.get("/")
def root():
    return {"message": "Welcome to the API"}
```

Now your routes are:
- `GET /users/`
- `GET /users/{user_id}`
- `POST /users/`
- `GET /items/`

---

## 15. Middleware

Middleware runs **before and after every request**. Use it for logging, CORS, authentication checks, timing, etc.

### Custom Middleware

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### CORS Middleware

CORS (Cross-Origin Resource Sharing) is essential when your frontend runs on a different origin than your API.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> **Security Note:** Never use `allow_origins=["*"]` in production with `allow_credentials=True`. Always specify exact allowed origins.

### Trusted Host Middleware

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["myapp.com", "*.myapp.com", "localhost"]
)
```

---

## 16. Background Tasks

Background tasks let you execute operations **after returning a response** — useful for sending emails, logging, or cleanup without making the client wait.

```python
from fastapi import BackgroundTasks

def send_welcome_email(email: str, username: str):
    # Simulate sending an email (blocking I/O)
    print(f"Sending welcome email to {email} for user {username}")

@app.post("/register")
def register_user(username: str, email: str, background_tasks: BackgroundTasks):
    # ... save user to DB ...
    background_tasks.add_task(send_welcome_email, email, username)
    return {"message": "User registered. Welcome email will be sent shortly."}
```

### Multiple Background Tasks

```python
@app.post("/process")
def process(background_tasks: BackgroundTasks):
    background_tasks.add_task(log_activity, "process started")
    background_tasks.add_task(send_notification, "admin@company.com")
    return {"status": "Processing started"}
```

> Background tasks run in the same process but after the response is sent. For heavy/long-running tasks, use a proper task queue like **Celery** with **Redis/RabbitMQ**.

---

## 17. File Uploads

### Install Required Package

```bash
pip install python-multipart
```

### Single File Upload

```python
from fastapi import File, UploadFile

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content)
    }
```

### Save Uploaded File to Disk

```python
import shutil
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "path": str(file_path)}
```

### Multiple File Uploads

```python
from typing import List

@app.post("/upload-multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    return [{"filename": f.filename, "content_type": f.content_type} for f in files]
```

### File + Form Data Together

```python
from fastapi import Form

@app.post("/upload-with-metadata")
async def upload_with_metadata(
    description: str = Form(...),
    file: UploadFile = File(...)
):
    return {"description": description, "filename": file.filename}
```

> **Note:** You cannot mix `Body()` (JSON) with `File()` / `Form()` in the same request since multipart form data and JSON are different content types.

---

## 18. Authentication: OAuth2 & JWT

### Install Required Packages

```bash
pip install "python-jose[cryptography]" passlib[bcrypt]
```

### Full JWT Authentication Example

```python
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ── Config ───────────────────────────────────────────────
SECRET_KEY = "your-very-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ── Fake DB ───────────────────────────────────────────────
fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": pwd_context.hash("secret"),
        "email": "alice@example.com",
    }
}

# ── Schemas ───────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: str

# ── Utilities ─────────────────────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = fake_users_db.get(token_data.username)
    if user is None:
        raise credentials_exception
    return user

# ── Routes ────────────────────────────────────────────────
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user
```

### How the Auth Flow Works

```
1. User POSTs to /token with username + password
2. Server verifies credentials
3. Server returns JWT access token
4. User sends token in Authorization: Bearer <token> header
5. Server validates token on every protected route via Depends(get_current_user)
```

---

## 19. Database Integration (SQLAlchemy)

### Install Packages

```bash
pip install sqlalchemy
# For SQLite (built into Python — great for learning)
# For PostgreSQL:
pip install psycopg2-binary
```

### Project Structure

```
project/
├── main.py
├── database.py
├── models.py
├── schemas.py
└── crud.py
```

### `database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./app.db"
# For PostgreSQL: "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `models.py`

```python
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
```

### `schemas.py`

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True   # Enables ORM mode (Pydantic v2+)
```

### `crud.py`

```python
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

### `main.py`

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, crud, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)   # creates tables

app = FastAPI()

@app.post("/users", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users", response_model=list[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## 20. Async & Await in FastAPI

### Sync vs Async Route Functions

```python
# Sync — blocks the thread while waiting
@app.get("/sync")
def sync_route():
    import time
    time.sleep(2)           # blocks the entire thread
    return {"type": "sync"}

# Async — non-blocking, other requests can be handled while waiting
@app.get("/async")
async def async_route():
    import asyncio
    await asyncio.sleep(2)  # yields control, doesn't block
    return {"type": "async"}
```

### When to Use `async def` vs `def`

| Scenario | Use |
|---|---|
| Calling `await`-able operations (async DB, HTTP client) | `async def` |
| Regular sync operations (math, string processing) | `def` |
| Calling blocking I/O (SQLAlchemy sync, `requests` library) | `def` (FastAPI runs it in a threadpool) |

> FastAPI is smart: if you use `def`, it runs the function in a thread pool so it doesn't block the event loop. If you use `async def`, it runs on the event loop.

### Async HTTP Requests with `httpx`

```bash
pip install httpx
```

```python
import httpx

@app.get("/external")
async def call_external_api():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com")
        return response.json()
```

### Async Database with `databases` or `asyncpg`

```bash
pip install databases[asyncpg] asyncpg
```

```python
import databases

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
database = databases.Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/users")
async def get_users():
    query = "SELECT id, username FROM users"
    return await database.fetch_all(query)
```

---

## 21. Testing FastAPI Applications

FastAPI provides a `TestClient` (built on `httpx`) for testing.

### Install

```bash
pip install pytest httpx
```

### Basic Test

```python
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI!"}
```

### Testing CRUD Endpoints

```python
def test_create_item():
    response = client.post(
        "/items",
        json={"name": "Laptop", "price": 999.99}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["item"]["name"] == "Laptop"

def test_item_not_found():
    response = client.get("/items/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_create_item_invalid():
    response = client.post(
        "/items",
        json={"name": "Laptop", "price": "not-a-number"}   # invalid
    )
    assert response.status_code == 422
```

### Testing with Authentication

```python
def test_protected_route_without_token():
    response = client.get("/users/me")
    assert response.status_code == 401

def test_protected_route_with_token():
    # First get a token
    login = client.post("/token", data={"username": "alice", "password": "secret"})
    token = login.json()["access_token"]

    # Then use the token
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "alice"
```

### Testing with Database Override (Dependency Override)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Use a separate test SQLite DB
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)
client = TestClient(app)

def test_create_user():
    response = client.post("/users", json={"username": "bob", "email": "bob@example.com"})
    assert response.status_code == 201
    assert response.json()["username"] == "bob"
```

### Run Tests

```bash
pytest                   # run all tests
pytest -v                # verbose output
pytest test_main.py -v   # specific file
pytest -k "test_create"  # run tests matching pattern
```

---

## 22. Project Structure Best Practices

A well-organized FastAPI project for a real-world application:

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app instance, include routers
│   ├── config.py                # Settings (env vars, configs)
│   ├── database.py              # DB engine, SessionLocal, Base
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   │
│   ├── schemas/                 # Pydantic schemas (input/output)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   │
│   ├── crud/                    # DB operations (Create, Read, Update, Delete)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   │
│   ├── routers/                 # APIRouter instances
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   └── email_service.py
│   │
│   └── dependencies/            # Reusable Depends() functions
│       ├── __init__.py
│       └── auth.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_users.py
│   └── test_items.py
│
├── .env                         # Environment variables (never commit!)
├── .env.example                 # Template for env vars
├── requirements.txt
└── README.md
```

### `config.py` — Using Environment Variables

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    allowed_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

```bash
pip install pydantic-settings
```

### `.env` file

```
DATABASE_URL=postgresql://user:password@localhost/mydb
SECRET_KEY=a-very-long-and-random-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### `main.py` — Clean Entry Point

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, items
from app.config import settings
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="A well-structured FastAPI project",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
```

---

## Quick Reference: FastAPI Cheatsheet

### Route Decorators

```python
@app.get("/path")        # Read
@app.post("/path")       # Create
@app.put("/path/{id}")   # Full update
@app.patch("/path/{id}") # Partial update
@app.delete("/path/{id}")# Delete
```

### Parameter Types

```python
# Path parameter
@app.get("/items/{id}")
def func(id: int): ...

# Query parameter
@app.get("/items")
def func(skip: int = 0, limit: int = 10): ...

# Request body
@app.post("/items")
def func(item: ItemModel): ...

# Header
from fastapi import Header
def func(x_token: str = Header(...)): ...

# Cookie
from fastapi import Cookie
def func(session_id: str = Cookie(None)): ...
```

### Dependency Injection

```python
def dependency(param: str = Query(...)):
    return param

@app.get("/")
def route(value = Depends(dependency)): ...
```

### Common Imports

```python
from fastapi import (
    FastAPI, APIRouter, Depends, HTTPException,
    Request, Response, status,
    Path, Query, Body, Header, Cookie,
    File, UploadFile, Form,
    BackgroundTasks
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pydantic import BaseModel, Field, EmailStr
```

---

*Documentation written for FastAPI beginners to intermediate developers | April 2026*
