from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Register(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone_number: str = Field(..., min_length=7)
    business_name: str
    business_address: Optional[str] = None
    password: Optional[str] = Field(..., max_length=6)


class Login(BaseModel):
    phone_number:str = Field(..., min_length=7)
    password: str = Field(...,max_length=6)
    
class UserOut(BaseModel):
    id: int
    name: str
    business_name: str

class Update(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(default=None, min_length=7)
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    password: Optional[str] = None
    
class AuthResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True
