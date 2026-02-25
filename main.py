from fastapi import FastAPI
from fastapi import HTTPException,responses,Depends,status,Response,Request,Form
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse ,RedirectResponse
from database import engine, get_db
import models
from models import User
from models import Todo
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import ToDoCreate,ToUpdate,TodoResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from routers import users
# Session middleware (required for login/logout)
from dotenv import load_dotenv
import os
from config import templates
from auth import get_current_user


load_dotenv()  # loads variables from .env file

SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


CurrentUser = Annotated[User, Depends(get_current_user)]

templates = Jinja2Templates(directory="templates")
app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
# Include user router
app.include_router(users.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
models.Base.metadata.create_all(bind=engine)
DBSession = Annotated[Session, Depends(get_db)]

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)
@app.get("/")
def welcome(request: Request):
    return templates.TemplateResponse(
        "welcome.html",
        {"request": request}
    )


@app.get("/todo", response_class=HTMLResponse, include_in_schema=False, name="home")
def home_page(
    request: Request,
    db: DBSession,
    current_user: CurrentUser 
):
    todos = db.execute(
        select(models.Todo).where(models.Todo.owner_id == current_user.id)
    ).scalars().all()

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "todos": todos, "user": current_user}
    )


@app.get("/todo/{todo_id}", include_in_schema=False)
def todo_page(request: Request, todo_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Todo).where(models.Todo.id == todo_id))
    todo = result.scalars().first()
    if todo:
        title = todo.title
        completed = todo.completed
        return templates.TemplateResponse(
            "home.html",
            
            {
                "request": request,
                "todos": [todo]},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")




@app.get("/add",include_in_schema=False)
def add_Todo_page(request:Request,db:DBSession):
    return templates.TemplateResponse("add.html", {"request": request})

@app.post("/add")
def add_todo_submit(
    request: Request,
    title: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    new_todo = Todo(
        title=title,
        completed=False,
        owner_id=user_id   # ✅ THIS IS THE FIX
    )

    db.add(new_todo)
    db.commit()
    return RedirectResponse(url="/todo", status_code=303)


@app.get("/delete/{todo_id}",include_in_schema=False)
def Delete_Todo(request: Request,
    db: Annotated[Session, Depends(get_db)],
    todo_id:int):
    result = db.execute(select(models.Todo).where(models.Todo.id == todo_id))
    todo = result.scalars().first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return templates.TemplateResponse(
        "delete.html",
        {
            "request": request,
            "todo": todo
        }
    )
@app.post("/delete/{todo_id}", include_in_schema=False)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    todo = db.scalar(
        select(models.Todo).where(models.Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return RedirectResponse(url="/", status_code=303)
    
@app.get("/edit/{todo_id}",include_in_schema=False)
def edit_Todo(request: Request,
    db: Annotated[Session, Depends(get_db)],
    todo_id:int):
    result = db.execute(select(models.Todo).where(models.Todo.id == todo_id))
    todo = result.scalars().first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return templates.TemplateResponse(
        "edit-todo.html",
        {
            "request": request,
            "todo": todo
            
        }
    )

@app.post("/edit/{todo_id}", include_in_schema=False)
def edit_todo(
    todo_id: int,
    title: str = Form(...),
    completed: str = Form(None),
    db: Session = Depends(get_db),

):
    todo = db.scalar(
        select(models.Todo).where(models.Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo.title = title
    todo.completed = completed == "on"
    db.commit()


    return RedirectResponse(url="/todo", status_code=303)


@app.get('/api')
def home():
    return {"message": "Welcome to To-Do API 🚀"}


@app.get('/api/todos')
def get_todos(
    db:DBSession
):
    result = db.execute(select(models.Todo))
    todos = result.scalars().all()
    return todos
    


@app.get('/api/todos/{todo_id}',response_model=TodoResponse)
def get_todo_id(todo_id:int,db:DBSession):
     result = db.execute(
        select(models.Todo).where(models.Todo.id == todo_id),
    )
     todo = result.scalars().first()
     if todo:
         return todo
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Message:ID Invalid")
    




@app.post('/api/todos',response_model=TodoResponse,status_code=status.HTTP_201_CREATED,)
def create_todo(todo:ToDoCreate,db:DBSession):
    result = db.execute(
        select(models.Todo).where(models.Todo.title == todo.title),
    )
    existing_todo = result.scalars().first()
    if existing_todo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Todo already exists",
        )
    new_todo = models.Todo(
        title=todo.title,
        completed=todo.completed
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo
    
   
@app.patch('/api/todos/{todo_id}',response_model=TodoResponse)
def todo_update(todo_id:int,todo_update:ToUpdate,db:DBSession):
    result = db.execute(
        select(models.Todo).where(models.Todo.id == todo_id),
    )
    todo = result.scalars().first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message: ID Invalid"
        )
    
    if todo_update.title is not None:
        todo.title = todo_update.title
        
    if todo_update.completed is not None:
        todo.completed = todo_update.completed
    

    db.commit()
    db.refresh(todo)
    return todo
  


@app.delete('/api/todos/{todo_id}',status_code=204)
def delete_todo(todo_id:int,db:DBSession):
    result = db.execute(
        select(models.Todo).where(models.Todo.id == todo_id),
    )
    todo = result.scalars().first()

    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message: ID Invalid"
        )
    db.delete(todo)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "request": request,
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        "error.html",
        {
             "request": request,  
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
    
