from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str
    description: str | None = None


class ExpenseUpdate(BaseModel):
    title: str
    amount: float
    category: str
    description: str | None = None


class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    description: str | None = None
    user_id: int

    class Config:
        from_attributes = True