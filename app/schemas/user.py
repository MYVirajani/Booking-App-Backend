import uuid

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr | None = None
    password: str


class UserLogin(BaseModel):
    phone: str
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    email: EmailStr | None = None
    is_owner: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"