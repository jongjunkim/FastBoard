from pydantic import BaseModel, validator

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