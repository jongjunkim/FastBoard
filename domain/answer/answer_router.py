from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from models import User
from database import get_async_db, get_redis_connection
from domain.post import post_crud
from domain.board import board_crud
from domain.answer import answer_schema, answer_crud
from domain.user.user_router import get_current_user

import redis
import json
from sqlalchemy.ext.asyncio import AsyncSession
import aioredis
from sqlalchemy.future import select

router = APIRouter(
    prefix="/api/answer",
)

@router.post("/create/{board_id}/{post_id}", status_code=status.HTTP_200_OK)
async def answer_create(board_id: int, post_id: int, _answer_create: answer_schema.AnswerCreate, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):

    board = await board_crud.get_board_id(db, board_id=board_id)

    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시판이 존재 하지 않습니다.")

    if board.user_id != current_user.id and not board.public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시판 접근 권한이 없습니다.")

    post = await post_crud.get_post_id(db, post_id = post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 존재 하지 않습니다.")

    await answer_crud.create_answer(db=db, user=current_user, board=board, post = post, new_answer=_answer_create)

    return {"message": "Answer created successfully"}


@router.put("/update", status_code=status.HTTP_200_OK)
async def answer_update(_answer_update: answer_schema.AnswerUpdate, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):

    db_answer = await answer_crud.get_answer_id(db, answer_id = _answer_update.answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="댓글을 찾을 수 없습니다.")

    if db_answer.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다.")

    await answer_crud.update_answer(db=db, db_answer = db_answer, answer_update = _answer_update)

    return {"message": "수정이 완료되었습니다"}


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def answer_delete(_answer_delete: answer_schema.AnswerDelete, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):

    db_answer = await answer_crud.get_answer_id(db, answer_id=_answer_delete.answer_id)
    
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="댓글을 찾을 수 없습니다.")
    
    if db_answer.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="삭제 권한이 없습니다.")

    await answer_crud.delete_answer(db=db, db_answer=db_answer)

    return {"message": "삭제가 완료되었습니다"}