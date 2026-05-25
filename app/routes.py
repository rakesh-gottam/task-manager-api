from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.auth import (
    create_access_token,
    verify_token,
    oauth2_scheme,
    hash_password,
    verify_password
)

router = APIRouter()

# ✅ Root
@router.get("/")
def root():
    return {"message": "Task Manager API Running Successfully 🚀"}


# ✅ DB Connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔐 Get Current User from Token
from fastapi import Depends
from app.auth import verify_token, oauth2_scheme

def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user_id

# 👤 Register
@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user.username,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}


# 🔐 Login
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"user_id": db_user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
   


# ✅ Create Task (Protected)
@router.post("/tasks")
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    new_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        status="pending",
        user_id=user_id
    )

    db.add(new_task)
    db.commit()

    return {"message": "Task created"}


# ✅ Get Tasks (Protected)
@router.get("/tasks")
def get_tasks(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    return db.query(models.Task).filter(models.Task.user_id == user_id).all()


# ✅ Delete Task (Protected)
@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted"}

# ✏️ Update Task
@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    updated_task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = updated_task.title
    task.description = updated_task.description
    task.priority = updated_task.priority
    task.due_date = updated_task.due_date

    db.commit()

    return {"message": "Task updated successfully"}