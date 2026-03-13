from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database.db import engine, Base
from routes import auth_routes, pet_routes, chat_routes, payment_routes, admin_routes
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pet Adoption API")

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
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
