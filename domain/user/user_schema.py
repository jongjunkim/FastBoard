from pydantic import BaseModel, EmailStr, validator

from fastapi import HTTPException

class User(BaseModel):
    id : int
    fullname : str
    email : str

class UserCreate(BaseModel):
    fullname: str
    email: EmailStr
    password1: str
    password2: str


    @validator('fullname', 'email', 'password1', 'password2')
    def is_empty(cls, v):
        if not v or not v.strip():
            raise HTTPException(status_code = 442, detail = "보이는 항목들을 채워주세요")
        return v

    @validator('password2')
    def passwords_match(cls, v, values):
        if 'password1' in values and v != values['password1']:
            raise HTTPException(status_code = 442, detail = "비밀번호가 일치하지 않습니다")
        return v


class Token(BaseModel):
    access_token: str
    token_type : str
    email : EmailStr




