from fastapi.responses import RedirectResponse
from database import get_db
import models
from fastapi import APIRouter, Request, Form, Depends
from sqlalchemy.orm import Session
from auth import hash_password, login_user,verify_password
from config import templates
from typing import Annotated

router = APIRouter()

@router.get("/signup", include_in_schema=False)
def signup_page(request: Request):
    return templates.TemplateResponse(
        "sign_up.html",
        {"request": request}
    )


@router.post("/signup", include_in_schema=False)
def signup(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    email: str = Form(...),
    password: str = Form(...),
):
    user = db.query(models.User).filter(models.User.email == email).first()

    if user:
        return templates.TemplateResponse(
            "sign_up.html",
            {"request": request, "error": "Email already exists"},
        )

    new_user = models.User(
        email=email,
        hashed_password=hash_password(password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    login_user(request, new_user)

    return RedirectResponse("/todo", status_code=303)



@router.get("/login",include_in_schema=False)
def login_page(request:Request):
    return templates.TemplateResponse(
        "login.html",
        {"request":request}

    )

@router.post('/login',include_in_schema=False)
def login(request:Request,
        db: Annotated[Session, Depends(get_db)],
        email: str = Form(...),
        password: str = Form(...),
          
          ):
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid email or password"
            },
        )
    login_user(request, user)

    return RedirectResponse("/todo", status_code=303)



@router.get("/logout", include_in_schema=False)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/account", include_in_schema=False)
def account_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")  # get logged-in user id from session
    user = db.query(models.User).get(user_id) if user_id else None

    return templates.TemplateResponse(
        "Account.html",
        {"request": request, "user": user}  # pass user to template
    )

    