import datetime
from pydantic import BaseModel, validator
from domain.answer.answer_schema import Answer
from domain.user.user_schema import User


class Post(BaseModel):
    id: int
    title: str
    content: str
    create_date: datetime.datetime
    modified_date: datetime.datetime | None = None
    post_answer: list[Answer] = []

    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title : str
    content: str

    @validator('title', 'content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

#PostCreate 상속
class PostUpdate(PostCreate):
    post_id : int

class PostDelete(BaseModel):
    post_id : int

class PostList(BaseModel):
    total : int = 0
    post_list : list[Post] = []
