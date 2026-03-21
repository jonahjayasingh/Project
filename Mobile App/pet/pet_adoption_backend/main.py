from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database.db import engine, Base
from routes import auth_routes, pet_routes, chat_routes, payment_routes, admin_routes
<<<<<<< HEAD
=======
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
>>>>>>> fac2c57 (add)
import os

# Create database tables
Base.metadata.create_all(bind=engine)

<<<<<<< HEAD
app = FastAPI(title="Pet Adoption API")
=======
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app = FastAPI(title="Pet Adoption API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
>>>>>>> fac2c57 (add)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories if they don't exist
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)

# Mount static files for media access
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routes
app.include_router(auth_routes.router)
app.include_router(pet_routes.router)
app.include_router(chat_routes.router)
app.include_router(payment_routes.router)
app.include_router(admin_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pet Adoption API"}

if __name__ == "__main__":
    import uvicorn
<<<<<<< HEAD
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
=======
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
>>>>>>> fac2c57 (add)
