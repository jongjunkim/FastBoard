from pydantic import BaseModel, validator
from fastapi import HTTPException


class BoardCreate(BaseModel):
    name : str
    public : bool

    @validator('name')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v


#BoardCreate 상속
class BoardUpdate(BoardCreate):
    board_id : int
  

class BoardDelete(BaseModel):
    board_id : int