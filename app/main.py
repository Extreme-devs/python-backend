from fastapi import FastAPI
from app.routers import user, llm, vector_db, image_search
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.auth import AuthMiddleware

app = FastAPI(
    title="User Management API",
    description="This is a FastAPI CRUD application for managing users with PostgreSQL.",
    version="1.0.0",
    docs_url="/docs",  # URL for Swagger UI
    redoc_url="/redoc",  # URL for ReDoc UI
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# app.add_middleware(AuthMiddleware)

app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(llm.router, prefix="/api/v1/llm", tags=["llm"])
app.include_router(vector_db.router, prefix="/api/v1/vector_db", tags=["vector_db"])
app.include_router(image_search.router, prefix="/api/v1/image_search", tags=["image_search"])


@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI CRUD application"}
