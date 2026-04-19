"""
FastAPI Experiments — Beginner to Intermediate
================================================
Run:  uvicorn fastapi_experiments:app --reload
Docs: http://127.0.0.1:8000/docs

Covers every concept from fastapi_doc.md:
  - Path / Query / Body parameters
  - Pydantic models & Field validation
  - Full CRUD with in-memory store
  - Response models & status codes
  - Custom error handling
  - Dependency injection
  - APIRouter
  - Middleware (timing header + CORS)
  - Background tasks
  - File uploads
  - Async routes
  - JWT-style protected route (simplified)
"""

import asyncio
import shutil
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Cookie,
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Path as FPath,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

# ─────────────────────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="FastAPI Experiments",
    description="A single-file playground covering every concept in fastapi_doc.md",
    version="1.0.0",
    docs_url="/docs",
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Timing Middleware ──────────────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.time() - start):.4f}s"
    return response


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — HELLO WORLD
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["1. Hello World"])
def read_root():
    """Basic GET — returns a greeting message."""
    return {"message": "Hello, FastAPI! Visit /docs to explore all endpoints."}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — PATH PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

class Department(str, Enum):
    hr = "hr"
    engineering = "engineering"
    finance = "finance"


@app.get("/path/users/me", tags=["2. Path Parameters"])
def get_current_user_path():
    """Fixed path — must be declared BEFORE the dynamic /{user_id} route."""
    return {"user": "current_user"}


@app.get("/path/users/{user_id}", tags=["2. Path Parameters"])
def get_user_by_id(user_id: int):
    """Path parameter with automatic int conversion and validation."""
    return {"user_id": user_id}


@app.get("/path/users/{user_id}/posts/{post_id}", tags=["2. Path Parameters"])
def get_user_post(user_id: int, post_id: int):
    """Multiple path parameters in one route."""
    return {"user_id": user_id, "post_id": post_id}


@app.get("/path/departments/{dept_name}", tags=["2. Path Parameters"])
def get_department(dept_name: Department):
    """Path parameter restricted to an Enum — only hr / engineering / finance allowed."""
    return {"department": dept_name, "value": dept_name.value}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — QUERY PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/query/items", tags=["3. Query Parameters"])
def list_items_with_pagination(skip: int = 0, limit: int = 10):
    """Optional query params with defaults — try /query/items?skip=5&limit=3"""
    fake_items = [{"id": i, "name": f"Item {i}"} for i in range(1, 51)]
    return {"total": len(fake_items), "results": fake_items[skip: skip + limit]}


@app.get("/query/search", tags=["3. Query Parameters"])
def search_items(q: Optional[str] = None, active: bool = True):
    """Optional string query param + boolean param."""
    if q:
        return {"query": q, "active": active, "results": f"Searching for: {q}"}
    return {"query": None, "active": active, "results": "No query provided"}


@app.get("/query/users/{user_id}/items", tags=["3. Query Parameters"])
def get_user_items(user_id: int, active: bool = True, limit: int = 5):
    """Combining path + multiple query parameters."""
    return {"user_id": user_id, "active": active, "limit": limit}


@app.get("/query/filter", tags=["3. Query Parameters"])
def filter_by_tags(tags: List[str] = Query(default=[])):
    """Multi-value query param — try /query/filter?tags=python&tags=fastapi"""
    return {"tags": tags}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — REQUEST BODY (Pydantic Models)
# ─────────────────────────────────────────────────────────────────────────────

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Laptop",
                "description": "A high-performance laptop",
                "price": 999.99,
                "in_stock": True,
            }
        }
    }


@app.post("/body/items", tags=["4. Request Body"])
def create_item_body(item: Item):
    """POST with a JSON request body. FastAPI validates it against the Item schema."""
    item_dict = item.model_dump()
    item_dict["price_with_tax"] = round(item.price * 1.18, 2)
    return item_dict


# Nested model example
class Address(BaseModel):
    street: str
    city: str
    zip_code: str


class UserWithAddress(BaseModel):
    name: str
    age: int
    address: Address

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Alice",
                "age": 30,
                "address": {"street": "123 Main St", "city": "Hyderabad", "zip_code": "500001"},
            }
        }
    }


@app.post("/body/users", tags=["4. Request Body"])
def create_user_with_address(user: UserWithAddress):
    """Nested Pydantic model in a request body."""
    return {"message": f"User {user.name} from {user.address.city} created."}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — FULL CRUD (in-memory store)
# ─────────────────────────────────────────────────────────────────────────────

class Product(BaseModel):
    name: str
    price: float
    description: Optional[str] = None


class ProductResponse(Product):
    id: int


products_db: Dict[int, Product] = {}
product_counter = 0


@app.post("/crud/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["5. CRUD"])
def create_product(product: Product):
    """CREATE — POST /crud/products"""
    global product_counter
    product_counter += 1
    products_db[product_counter] = product
    return ProductResponse(id=product_counter, **product.model_dump())


@app.get("/crud/products", response_model=List[ProductResponse], tags=["5. CRUD"])
def list_products():
    """READ ALL — GET /crud/products"""
    return [ProductResponse(id=pid, **p.model_dump()) for pid, p in products_db.items()]


@app.get("/crud/products/{product_id}", response_model=ProductResponse, tags=["5. CRUD"])
def get_product(product_id: int):
    """READ ONE — GET /crud/products/{id}"""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(id=product_id, **products_db[product_id].model_dump())


@app.put("/crud/products/{product_id}", response_model=ProductResponse, tags=["5. CRUD"])
def update_product(product_id: int, product: Product):
    """FULL UPDATE — PUT /crud/products/{id}"""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    products_db[product_id] = product
    return ProductResponse(id=product_id, **product.model_dump())


@app.patch("/crud/products/{product_id}", response_model=ProductResponse, tags=["5. CRUD"])
def partial_update_product(product_id: int, product: Product):
    """PARTIAL UPDATE — PATCH /crud/products/{id} (only sends changed fields)"""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    stored = products_db[product_id].model_dump()
    update_data = product.model_dump(exclude_unset=True)
    stored.update(update_data)
    products_db[product_id] = Product(**stored)
    return ProductResponse(id=product_id, **stored)


@app.delete("/crud/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["5. CRUD"])
def delete_product(product_id: int):
    """DELETE — DELETE /crud/products/{id}"""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_db[product_id]


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — RESPONSE MODELS (filtering output fields)
# ─────────────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: str
    password: str   # <-- sensitive; should NOT appear in the response


class UserPublic(BaseModel):
    id: int
    username: str
    email: str      # password is intentionally absent here


@app.post(
    "/response/users",
    response_model=UserPublic,     # password is stripped from the output
    status_code=status.HTTP_201_CREATED,
    tags=["6. Response Models"],
)
def register_user(user: UserCreate):
    """response_model ensures 'password' is never returned even if present in the dict."""
    return {"id": 1, "username": user.username, "email": user.email, "password": user.password}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — PYDANTIC FIELD VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

class ValidatedUser(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="Full name")
    age: int = Field(ge=0, le=120, description="Age between 0 and 120")
    salary: float = Field(gt=0, description="Must be a positive number")
    bio: Optional[str] = Field(default=None, max_length=500, description="Short bio")

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Bob", "age": 28, "salary": 75000.0, "bio": "Software developer"}
        }
    }


@app.post("/validation/user", tags=["7. Field Validation"])
def create_validated_user(user: ValidatedUser):
    """Pydantic Field constraints — try sending age=200 or salary=-1 to see 422 errors."""
    return {"message": "Validation passed!", "user": user}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — PATH & QUERY PARAMETER VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/param-validation/users/{user_id}", tags=["8. Param Validation"])
def get_validated_user(
    user_id: int = FPath(ge=1, description="User ID must be a positive integer"),
    include_inactive: bool = Query(default=False, description="Include inactive users"),
):
    """Path() and Query() add validation + Swagger descriptions."""
    return {"user_id": user_id, "include_inactive": include_inactive}


@app.get("/param-validation/search", tags=["8. Param Validation"])
def validated_search(
    q: str = Query(min_length=3, max_length=50, description="Search term (3–50 chars)")
):
    """Query param with min/max length — try q='ab' to see a 422 error."""
    return {"query": q}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 — ERROR HANDLING
# ─────────────────────────────────────────────────────────────────────────────

# Custom exception class
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id


@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "custom_not_found", "message": f"Item {exc.item_id} does not exist"},
    )


@app.get("/errors/http/{item_id}", tags=["9. Error Handling"])
def demo_http_exception(item_id: int):
    """Raises a standard HTTPException when item_id > 10."""
    if item_id > 10:
        raise HTTPException(
            status_code=404,
            detail=f"Item {item_id} not found (only IDs 1–10 exist)",
            headers={"X-Error-Code": "ITEM_NOT_FOUND"},
        )
    return {"item_id": item_id}


@app.get("/errors/custom/{item_id}", tags=["9. Error Handling"])
def demo_custom_exception(item_id: int):
    """Raises a custom exception handled by the registered exception_handler above."""
    if item_id > 10:
        raise ItemNotFoundError(item_id=item_id)
    return {"item_id": item_id}


@app.get("/errors/forbidden", tags=["9. Error Handling"])
def demo_forbidden():
    """Raises a 403 Forbidden."""
    raise HTTPException(status_code=403, detail="You do not have permission to access this resource")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 — DEPENDENCY INJECTION
# ─────────────────────────────────────────────────────────────────────────────

# Simple function dependency
def common_pagination(skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100)):
    return {"skip": skip, "limit": limit}


# Class-based dependency
class Pagination:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit


# Chained dependency: token → user
def verify_token(x_token: str = Header(default="secret")):
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Invalid X-Token header")
    return x_token


def get_current_user_dep(token: str = Depends(verify_token)):
    return {"user": "alice", "token": token}


@app.get("/deps/items", tags=["10. Dependency Injection"])
def dep_items(pagination: dict = Depends(common_pagination)):
    """Shared pagination dependency — reusable across routes."""
    return {"pagination": pagination}


@app.get("/deps/products", tags=["10. Dependency Injection"])
def dep_products(pg: Pagination = Depends(Pagination)):
    """Class-based dependency for pagination."""
    return {"skip": pg.skip, "limit": pg.limit}


@app.get("/deps/profile", tags=["10. Dependency Injection"])
def dep_profile(user=Depends(get_current_user_dep)):
    """Chained dependency: token validation → user extraction.
    Pass header  X-Token: secret  to access this."""
    return {"profile": user}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 11 — APIROUTER (modular routes)
# ─────────────────────────────────────────────────────────────────────────────

orders_router = APIRouter(prefix="/orders", tags=["11. APIRouter"])

orders_db: Dict[int, dict] = {}
order_counter = 0


@orders_router.get("/")
def list_orders():
    return list(orders_db.values())


@orders_router.post("/", status_code=201)
def create_order(product_id: int = Body(...), quantity: int = Body(...)):
    global order_counter
    order_counter += 1
    order = {"id": order_counter, "product_id": product_id, "quantity": quantity}
    orders_db[order_counter] = order
    return order


@orders_router.get("/{order_id}")
def get_order(order_id: int):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]


app.include_router(orders_router)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 12 — BACKGROUND TASKS
# ─────────────────────────────────────────────────────────────────────────────

def send_welcome_email(email: str, username: str):
    """Simulated background email send (runs after response is returned)."""
    print(f"[Background] Sending welcome email to {email} for user '{username}'...")


def log_activity(action: str):
    print(f"[Background] Activity logged: {action} at {datetime.utcnow().isoformat()}")


@app.post("/background/register", tags=["12. Background Tasks"])
def register_with_background(username: str, email: str, background_tasks: BackgroundTasks):
    """Response is returned immediately; email and log happen in the background."""
    background_tasks.add_task(send_welcome_email, email, username)
    background_tasks.add_task(log_activity, f"registered:{username}")
    return {"message": f"User '{username}' registered. Background tasks queued."}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 13 — FILE UPLOADS
# ─────────────────────────────────────────────────────────────────────────────

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/files/upload", tags=["13. File Uploads"])
async def upload_single_file(file: UploadFile = File(...)):
    """Upload a single file — returns filename, content-type, and size."""
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
    }


@app.post("/files/upload-save", tags=["13. File Uploads"])
async def upload_and_save_file(file: UploadFile = File(...)):
    """Uploads a file and saves it to the ./uploads/ directory."""
    dest = UPLOAD_DIR / file.filename
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "saved_to": str(dest)}


@app.post("/files/upload-multiple", tags=["13. File Uploads"])
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload multiple files at once."""
    return [
        {"filename": f.filename, "content_type": f.content_type}
        for f in files
    ]


@app.post("/files/upload-with-metadata", tags=["13. File Uploads"])
async def upload_with_metadata(
    description: str = Form(...),
    file: UploadFile = File(...),
):
    """File upload combined with a form field (description)."""
    content = await file.read()
    return {
        "description": description,
        "filename": file.filename,
        "size_bytes": len(content),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 14 — ASYNC ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/async/sync-route", tags=["14. Async vs Sync"])
def sync_route():
    """Synchronous route — FastAPI runs this in a thread pool automatically."""
    time.sleep(0.1)   # simulates blocking I/O
    return {"type": "sync", "note": "FastAPI ran this in a thread pool"}


@app.get("/async/async-route", tags=["14. Async vs Sync"])
async def async_route():
    """Async route — non-blocking, yields control during await."""
    await asyncio.sleep(0.1)   # non-blocking sleep
    return {"type": "async", "note": "This ran on the event loop, non-blocking"}


@app.get("/async/compare", tags=["14. Async vs Sync"])
async def compare_routes():
    """Explains when to use async def vs def."""
    return {
        "use_async_def_when": [
            "You are calling async libraries (httpx, asyncpg, aiomysql)",
            "You have multiple I/O-bound awaitable operations",
        ],
        "use_def_when": [
            "You are using sync libraries (SQLAlchemy sync, requests)",
            "The function is purely CPU-bound (math, string operations)",
        ],
        "tip": "FastAPI handles both safely. Sync functions run in a thread pool.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 15 — HEADERS & COOKIES (bonus)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/extras/headers", tags=["15. Headers & Cookies"])
def read_headers(user_agent: Optional[str] = Header(default=None)):
    """Read a request header — FastAPI auto-converts user-agent → user_agent."""
    return {"User-Agent": user_agent}


@app.get("/extras/cookies", tags=["15. Headers & Cookies"])
def read_cookie(session_id: Optional[str] = Cookie(default=None)):
    """Read a cookie named 'session_id' from the request."""
    if not session_id:
        return {"message": "No session_id cookie found"}
    return {"session_id": session_id}


@app.get("/extras/custom-response-headers", tags=["15. Headers & Cookies"])
def custom_response_headers(response: JSONResponse = None):
    """Return extra custom headers in the response."""
    from fastapi.responses import JSONResponse as JR
    return JR(
        content={"message": "Check the response headers!"},
        headers={"X-Custom-Header": "my-value", "X-App-Version": "1.0.0"},
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 16 — SIMPLIFIED AUTH (token check without full JWT library)
# ─────────────────────────────────────────────────────────────────────────────

FAKE_SECRET_TOKEN = "fastapi-rocks"

fake_users = {
    "alice": {"username": "alice", "email": "alice@example.com", "password": "secret"},
    "bob":   {"username": "bob",   "email": "bob@example.com",   "password": "password"},
}


class LoginRequest(BaseModel):
    username: str
    password: str

    model_config = {
        "json_schema_extra": {"example": {"username": "alice", "password": "secret"}}
    }


@app.post("/auth/login", tags=["16. Auth (Simplified)"])
def login(credentials: LoginRequest):
    """POST username + password → receive a fake token.
    Try: username=alice, password=secret"""
    user = fake_users.get(credentials.username)
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {
        "access_token": FAKE_SECRET_TOKEN,
        "token_type": "bearer",
        "user": {"username": user["username"], "email": user["email"]},
    }


def get_authenticated_user(authorization: Optional[str] = Header(default=None)):
    """Dependency: checks Authorization: Bearer <token> header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.split(" ")[1]
    if token != FAKE_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user": "alice"}


@app.get("/auth/protected", tags=["16. Auth (Simplified)"])
def protected_route(current_user=Depends(get_authenticated_user)):
    """Protected route — requires  Authorization: Bearer fastapi-rocks  header."""
    return {"message": "Access granted!", "user": current_user}


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_experiments:app", host="0.0.0.0", port=8000, reload=True)
