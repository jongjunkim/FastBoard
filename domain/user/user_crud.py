from datetime import datetime
from passlib.context import CryptContext
from domain.user.user_schema import UserCreate
from models import User
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def sign_up(db: AsyncSession, new_user: UserCreate):
    db_user = User(fullname=new_user.fullname,
                   password=pwd_context.hash(new_user.password1),
                   email=new_user.email,
                   create_date=datetime.now())
    db.add(db_user)
    await db.commit()
    
async def get_user(db: AsyncSession, email: str):
<<<<<<< HEAD
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
=======
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()
>>>>>>> answer
