from fastapi import APIRouter
from .endpoints import patients, tests

api_router = APIRouter()

api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
