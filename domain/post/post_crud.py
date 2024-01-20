from sqlalchemy.orm import Session, selectinload
from domain.post.post_schema import PostCreate, PostUpdate, PostDelete
from models import User, Board, Post
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
<<<<<<< HEAD

=======
from domain.answer import answer_crud
from sqlalchemy.orm import joinedload
>>>>>>> answer


async def create_post(db:AsyncSession, board: Board, user: User, post_create: PostCreate):
    db_post = Post(title = post_create.title,
                   content = post_create.content,
                   board = board,
                   user = user,
                   create_date=datetime.now(),
                   modified_date=datetime.now())
    db.add(db_post)
    await db.commit()

async def get_post_id(db: AsyncSession, post_id: int):
    result = await db.execute(
        select(Post).options(joinedload(Post.post_answer)).filter(Post.id == post_id)
    )
    return result.scalars().first()

async def update_post(db: AsyncSession, db_post: Post, post_update: PostUpdate):
    db_post.title = post_update.title
    db_post.content = post_update.content
    db_postmodified_date = datetime.now()
    db.add(db_post)
    await db.commit()

async def delete_post(db: AsyncSession, db_post: PostDelete):
    await db.delete(db_post)
    await db.commit()

async def get_post_list(db: AsyncSession, board_id: int, current_user: User, skip: int = 0, limit: int = 10):
    query = select(Post).options(selectinload(Post.post_answer)).filter(Post.board_id == board_id)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()

    post_list_result = await db.execute(query.offset(skip).limit(limit))
    post_list = post_list_result.scalars().all()

    return total, post_list
