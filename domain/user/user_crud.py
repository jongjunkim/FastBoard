from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def sign_up(db: Session, new_user: UserCreate):
    db_user = User(fullname=new_user.fullname,
                   password=pwd_context.hash(new_user.password1),
                   email=new_user.email)
    db.add(db_user)
    db.commit()

def get_user(db: Session, email: str):
    return db.query(User).filter((User.email == email)).first()