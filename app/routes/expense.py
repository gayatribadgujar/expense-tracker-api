from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.db import get_db
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_expense = Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        user_id=current_user.id
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@router.get("/", response_model=list[ExpenseResponse])
def get_expenses(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * limit
    return (
        db.query(Expense)
        .filter(Expense.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/count")
def get_expense_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(Expense).filter(Expense.user_id == current_user.id).count()
    return {"total": total}


@router.get("/report")
def get_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_expenses = db.query(Expense).filter(Expense.user_id == current_user.id).count()

    total_amount = (
        db.query(func.sum(Expense.amount))
        .filter(Expense.user_id == current_user.id)
        .scalar()
        or 0
    )

    category_data = (
        db.query(Expense.category, func.sum(Expense.amount).label("total"))
        .filter(Expense.user_id == current_user.id)
        .group_by(Expense.category)
        .all()
    )

    category_summary = []
    for category, total in category_data:
        category_summary.append({
            "category": category,
            "total": total
        })

    return {
        "total_expenses": total_expenses,
        "total_amount": total_amount,
        "category_summary": category_summary
    }


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )

    if not existing_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    existing_expense.title = expense.title
    existing_expense.amount = expense.amount
    existing_expense.category = expense.category
    existing_expense.description = expense.description

    db.commit()
    db.refresh(existing_expense)
    return existing_expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )

    if not existing_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(existing_expense)
    db.commit()

    return {"message": "Expense deleted successfully"}