import datetime

from pydantic import BaseModel, validator
from domain.user.user_schema import User
from domain.post.post_schema import Post

class Board(BaseModel):
    id: int
    name : str
    num_post : int = 0
    create_date: datetime.datetime
    modified_date: datetime.datetime | None = None
    board_posts: list[Post] = []
    
    class Config:
        from_attributes = True

class BoardCreate(BaseModel):
    name : str
    public : bool = False

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

class BoardList(BaseModel):
    total : int = 0
    board_list : list[Board] = []
  