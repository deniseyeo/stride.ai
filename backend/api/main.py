import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Add the current directory (backend) to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app
app = FastAPI()

# Get frontend URL from environment variable or use default
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
print(f"Using frontend URL: {frontend_url}")  # Debug print

# Add CORS middleware FIRST (before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Then add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("API_SECRET_KEY"),
    same_site="lax",
    https_only=False,
)

from routes import strava, training_plan

app.include_router(strava.router)
app.include_router(training_plan.router)

for route in app.routes:
    print(f"Route: {route.path} [{','.join(route.methods)}]")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
