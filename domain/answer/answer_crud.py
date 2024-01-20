from models import Board, User, Post, Answer
from domain.answer.answer_schema import AnswerCreate, AnswerDelete, AnswerUpdate
from sqlalchemy import and_, func
from sqlalchemy.future import select
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload



async def create_answer(db: AsyncSession, user:User, board:Board, post:Post, new_answer: AnswerCreate):
    db_answer = Answer(content = new_answer.content,
                        board = board,
                        user = user,
                        post = post,
                        create_date=datetime.now(),
                        modified_date=datetime.now())

    db.add(db_answer)
    await db.commit()


async def update_answer(db: AsyncSession, db_answer: Answer, answer_update: AnswerUpdate):
    db_answer.content = answer_update.content
    db_answer.modified_date = datetime.now()
    db.add(db_answer)
    await db.commit()


async def get_answer_id(db: AsyncSession, answer_id: int):
    result = await db.execute(select(Answer).filter(Answer.id == answer_id))
    return result.scalars().first()


async def delete_answer(db: AsyncSession, db_answer: AnswerDelete):
    await db.delete(db_answer)
    await db.commit()

