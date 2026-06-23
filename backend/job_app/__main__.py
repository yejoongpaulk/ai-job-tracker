# job_app/__main__.py
import uvicorn
from fastapi import FastAPI

# Import the configured router object
from .routers.auth import auth_router
# from .routers.jobs import jobs_router

app = FastAPI(title="Job Application Management API")

# Register your modular endpoints
app.include_router(auth_router)
# app.include_router(jobs_router)

@app.get("/")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("job_app.__main__:app", host="127.0.0.1", port=8000, reload=True)
