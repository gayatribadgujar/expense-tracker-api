from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.database.db import Base, engine
from app.routes.expense import router as expense_router
from app.routes.user import router as user_router
from app.models import expense as expense_model
from app.models import user as user_model

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(expense_router)
app.include_router(user_router)

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def root():
    return {"message": "Expense Tracker API running 🚀"}



@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )   


@app.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={}
    )
