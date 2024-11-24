from pydantic import BaseModel


# User
class UserBase(BaseModel):
    name: str
    password: str
    active: bool = True

class UserCreate(UserBase):
    pass

class user(UserBase):
    user_id: int

    class Config:
        from_attributes = True

class SignInSchema(BaseModel):
    user_name: str
    user_password: str

# class User


# Token
class TokenInfo(BaseModel):
    access_token: str
    token_type: str