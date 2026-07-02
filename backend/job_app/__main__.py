# job_app/__main__.py
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv  # Import the loader engine

# 🔒 CRITICAL: Load environment variables from .env BEFORE any other imports!
_ = load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine, Base
from .dependency import valkey_client
from .routers import auth, jobs

# ==========================================
# 1. Lifespan Context Manager (Startup/Shutdown)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("🚀 [STARTUP] Booting AI Job Tracker Backend...")
    
    # Optional DB Migration: Automatically provision schemas if tables are absent
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("📡 [STARTUP] PostgreSQL database tables initialized successfully.")
    
    yield  # The FastAPI application runs while execution pauses here
    
    # Shutdown actions
    print("🛑 [SHUTDOWN] Wiping cache connections...")
    await valkey_client.close()
    print("👋 [SHUTDOWN] Backend server deactivated smoothly.")


# ==========================================
# 2. FastAPI Application Core Initialization
# ==========================================
app = FastAPI(
    title="AI Job Tracker Spreadsheet Backend",
    version="1.0.0",
    lifespan=lifespan
)


# ==========================================
# 3. CORS Middleware Configuration (For React Frontend)
#
# Only applies during development (i.e. not in production)
# ==========================================
# # Update origins list when deployment URLs or local development ports shift
# origins = [
#     "http://localhost:3000",  # Default React development port
#     "http://127.0.0.1:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,     # 🔒 CRITICAL: Allows browser to pass Valkey cookies back and forth
#     allow_methods=["*"],        # Allows GET, POST, OPTIONS, PATCH, DELETE
#     allow_headers=["*"],
# )


# ==========================================
# 4. Router Mounting
# ==========================================
app.include_router(auth.router)
app.include_router(jobs.router)


@app.get("/health", tags=["System Health"])
async def health_check():
    """Simple baseline route for health pings and deployment smoke-tests."""
    return {"status": "healthy", "service": "ai-job-tracker"}


# ==========================================
# 5. Mount resources from static files (i.e. npm run build)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(current_dir, "..", "dist"))

app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

# 4. Catch-all route to serve index.html for React Router (SPA tracking)
@app.get("/{catchall:path}")
def serve_react_app(catchall: str):
    # Prevent intercepting API routes
    if catchall.startswith("api/"):
        return {"error": "Not Found"}
        
    index_path = os.path.join(frontend_dir, "index.html")
    return FileResponse(index_path)


# Executable entry point hook if script run via python directly
if __name__ == "__main__":
    uvicorn.run("job_app.__main__:app", host="127.0.0.1", port=8000, reload=True)
