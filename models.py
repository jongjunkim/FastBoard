from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    fullname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    create_date = Column(DateTime, nullable=False)



class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    public = Column(Boolean, default="false")
    user_id = Column(Integer, ForeignKey("users.id"))
    create_date = Column(DateTime, nullable=False)
    modified_date = Column(DateTime, nullable=False)

    user = relationship("User", backref="user_boards")


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    board_id = Column(Integer, ForeignKey("board.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    create_date = Column(DateTime, nullable=False)
    modified_date = Column(DateTime, nullable=False)
    
    board = relationship("Board", backref="board_posts")
    user = relationship("User", backref="user_posts")

class Answer(Base):
    __tablename__ = "answer"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    board_id = Column(Integer, ForeignKey("board.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("post.id"))
    create_date = Column(DateTime, nullable=False)
    modified_date = Column(DateTime, nullable=False)

    user = relationship("User", backref = "user_answer")
    board = relationship("Board", backref = "baord_answer")
    post = relationship("Post", backref = "post_answer")