from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from models import User
from database import get_async_db
from domain.post import post_schema, post_crud
from domain.user.user_router import get_current_user
from domain.board import board_crud
import redis
import json
from sqlalchemy.ext.asyncio import AsyncSession
import aioredis
from sqlalchemy.future import select


router = APIRouter(
    prefix="/api/post",
)

@router.post("/create/{board_id}", status_code=status.HTTP_200_OK)
async def post_create(board_id: int, _post_create: post_schema.PostCreate, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):

    board = await board_crud.get_board_id(db, board_id=board_id)

    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시판을 찾을 수 없습니다.")

    if board.user_id != current_user.id and not board.public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시판 접근 권한이 없습니다.")

    await post_crud.create_post(db=db, board=board, user=current_user, post_create=_post_create)

    return {"message": "Post created successfully"}

@router.put("/update", status_code=status.HTTP_200_OK)
async def post_update(_post_update: post_schema.PostUpdate, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):

    db_post = await post_crud.get_post_id(db, post_id = _post_update.post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다.")

    await post_crud.update_post(db=db, db_post = db_post, post_update = _post_update)

    return {"message": "수정이 완료되었습니다"}

@router.delete("/delete", status_code=status.HTTP_200_OK)
async def post_delete(_post_delete: post_schema.PostDelete, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):

    db_post = await post_crud.get_post_id(db, post_id=_post_delete.post_id)
    
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
    
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="삭제 권한이 없습니다.")

    await post_crud.delete_post(db=db, db_post=db_post)

    return {"message": "삭제가 완료되었습니다"}

@router.get("/get/{post_id}", response_model=post_schema.Post)
async def post_get(post_id: int, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):
    
    db_post = await post_crud.get_post_id(db, post_id=post_id)
    
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    if db_post.user_id != current_user.id and not await is_board_public(db, db_post.board_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="조회 권한이 없습니다.")

    # return {"id": db_post.id, "title": db_post.title, "content": db_post.content, "create_date": db_post.create_date, "modified_date": db_post.modified_date}
    return db_post

@router.get("/list/{board_id}", response_model = post_schema.PostList)
async def post_get_list(board_id: int, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user),  page:int = 0, size:int = 10):

    db_board = await board_crud.get_board_id(db, board_id=board_id)

    if not db_board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시판을 찾을 수 없습니다.")

    if not db_board.public and db_board.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="조회 권한이 없습니다.")

    total, _post_list = await post_crud.get_post_list(db, board_id, current_user, skip = page * size, limit = size)

    return {'total': total,'post_list': _post_list}


async def is_board_public(db: AsyncSession, board_id: int) -> bool:
    db_board = await board_crud.get_board_id(db, board_id=board_id)

    if db_board is None:
        return False 
    
    return db_board.public



