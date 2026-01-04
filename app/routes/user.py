from typing import List
from fastapi import APIRouter

user_router = APIRouter()

# login users, logout, visit profile, update profle, delete (soft delete for 30 days then clean up permanently)