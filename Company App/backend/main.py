import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import Websitedata, userAuth
from models import Base, engine

# ============================================================
# App initialization
# ============================================================
app = FastAPI(
    title="Website CMS API",
    description="API for user authentication and website content management",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================
# Database setup
# ============================================================
# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# ============================================================
# Static file serving
# ============================================================
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================
# Middleware configuration (CORS)
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for production, use specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Router registration
# ============================================================

app.include_router(userAuth.router)
app.include_router(Websitedata.router)

