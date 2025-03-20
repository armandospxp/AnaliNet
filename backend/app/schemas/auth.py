from pydantic import BaseModel, EmailStr
from typing import Optional, List
from ..models.auth import Permission

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    role_id: int

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    role_id: int
    is_active: bool

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: str

class RoleCreate(RoleBase):
    permissions: List[Permission]

class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permissions: Optional[List[Permission]] = None

class RoleResponse(RoleBase):
    id: int
    permissions: List[Permission]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    permissions: List[Permission]
