""" Main file for our API server """
from fastapi import FastAPI
from api import calendar_backend

# Initialize other processes
# TODO

# API
app = FastAPI()
app.include_router(calendar_backend.router, prefix="/calendar", tags=["calendar"])

# Allow cross-origin requests: allows us to request resources from a different origin.
# in our case our frontend will reside on the origins below
origins = [
    "http://localhost:5173",
    "localhost:5173"
]


# Homepage
@app.get("/", tags=["root"])
async def root():
    return {"Hello World"}

@app.get("/health", tags=["health check"])
async def health():
    return {"status": "ok"}
