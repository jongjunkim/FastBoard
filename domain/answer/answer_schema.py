import datetime
from pydantic import BaseModel, validator
from domain.user.user_schema import User


class Answer(BaseModel):
    id: int
    content: str
    create_date: datetime.datetime
    modified_date: datetime.datetime 

    class Config:
        from_attributes = True

class AnswerCreate(BaseModel):
    content: str

    @validator('content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

class AnswerUpdate(AnswerCreate):
    answer_id: int
 
class AnswerDelete(BaseModel):
    answer_id: int

    