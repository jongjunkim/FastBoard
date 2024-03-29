from models import Board, User, Post
from domain.board.board_schema import BoardCreate, BoardUpdate, BoardDelete
from sqlalchemy import and_, func
from sqlalchemy.future import select
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

async def create_board(db: AsyncSession, new_board: BoardCreate, user:User):
    db_board = Board(name = new_board.name,
                    public = new_board.public,
                    user = user,
                    create_date=datetime.now(),
                    modified_date=datetime.now())
    db.add(db_board)
    await db.commit()


async def exisiting_board(db:AsyncSession, _board: BoardCreate):
    existing = await db.execute(select(Board).filter(Board.name == _board.name))
    return existing.scalars().first()

async def get_board_id(db: AsyncSession, board_id: int):
    result = await db.execute(
        select(Board)
        .options(selectinload(Board.board_posts).selectinload(Post.post_answer))
        .filter(Board.id == board_id)
    )
    return result.scalars().first()


async def update_board(db: AsyncSession, db_board: Board, board_update: BoardUpdate):
    db_board.name = board_update.name
    db_board.public = board_update.public
    db_board.modified_date = datetime.now()
    db.add(db_board)
    await db.commit()

async def delete_board(db: AsyncSession, db_board: BoardDelete):
    await db.delete(db_board)
    await db.commit()


async def get_board_list(db: AsyncSession, current_user: User, skip: int = 0, limit: int = 10):
    query = (
        select(Board)
        .options(selectinload(Board.board_posts).selectinload(Post.post_answer))
        .filter((Board.user_id == current_user.id) | (Board.public == True))
        .offset(skip)
        .limit(limit)
    )

    board_list_result = await db.execute(query)
    board_list = board_list_result.scalars().all()

    total_count_query = (
        select(func.count(Board.id))
        .filter((Board.user_id == current_user.id) | (Board.public == True))
    )
    total_count_result = await db.execute(total_count_query)
    total = total_count_result.scalar_one()

    return total, board_list
