from pydantic import BaseModel
from typing import Optional
from datetime import date

# 👤 User Schema
class UserCreate(BaseModel):
    username: str
    password: str


# 🔐 Login Schema
class UserLogin(BaseModel):
    username: str
    password: str


# ✅ Task Create Schema
class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    priority: str
    due_date: Optional[date]


# 📤 Task Response Schema
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[date]

    class Config:
        from_attributes = True