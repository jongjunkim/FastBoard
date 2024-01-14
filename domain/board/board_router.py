from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from domain.user.user_router import get_current_user
from models import User

from database import get_async_db, get_redis_connection
from domain.board import board_crud, board_schema

import redis
import json
import aioredis

router = APIRouter(
    prefix="/api/board",
)

@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
async def board_create(_board_create: board_schema.BoardCreate, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):

    board = await board_crud.exisiting_board(db, _board = _board_create)

    if board:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 게시판 이름입니다")

    await board_crud.create_board(db=db, new_board=_board_create, user = current_user)


@router.put("/update", status_code=status.HTTP_200_OK)
async def board_update(_board_update: board_schema.BoardUpdate, db: AsyncSession  = Depends(get_async_db), current_user: User = Depends(get_current_user)):

    db_board = await board_crud.get_board_id(db, board_id = _board_update.board_id)
    if not db_board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="게시판을 찾을수 없습니다.")
    
    if current_user.id != db_board.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")

    await board_crud.update_board(db=db, db_board = db_board, board_update = _board_update)

    return {"message": "수정이 완료되었습니다"}


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def board_delete(_board_delete: board_schema.BoardDelete, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):

    db_board = await board_crud.get_board_id(db, board_id = _board_delete.board_id)
    if not db_board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="게시판을 찾을수 없습니다.")
    
    if current_user.id != db_board.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")

    await board_crud.delete_board(db=db, db_board = db_board)

    return {"message": "삭제가 완료되었습니다"}


@router.get("/get/{board_id}", status_code=status.HTTP_200_OK)
async def board_get(board_id: int, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user), 
            redis_conn: redis.StrictRedis = Depends(get_redis_connection)):
   
    cache_board_key = f"board_user_{current_user.id}_{board_id}"

    cached_board = await redis_conn.get(cache_board_key)

    if cached_board:
        print("cache hit")
        return json.loads(cached_board.decode('utf-8'))

    db_board = await board_crud.get_board_id(db, board_id=board_id)
    if not db_board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시판을 찾을 수 없습니다.")

    if not db_board.public and db_board.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="조회 권한이 없습니다.")

    await redis_conn.setex(cache_board_key, timedelta(hours=2), json.dumps({'board_id': db_board.id,'board_name': db_board.name}))

    return {'board_id': db_board.id,'board_name': db_board.name}


@router.get("/list", response_model=board_schema.BoardList)
async def board_get_list(db: AsyncSession = Depends(get_async_db),current_user: User = Depends(get_current_user),page: int = 0,size: int = 10,
                    redis_conn: redis.StrictRedis = Depends(get_redis_connection)):
    
    cache_board_list_key = f"board_list_user_{current_user.id}_{page}_{size}"

    cached_board_list = await redis_conn.get(cache_board_list_key)
    if cached_board_list:
        return json.loads(cached_board_list.decode('utf-8'))

    total, _board_list = await board_crud.get_board_list(db, current_user, skip=page * size, limit=size)

    board_list_serializable = [{'id': board.id,'name': board.name, 'num_post': board.num_post} for board in _board_list]
    cache_data = json.dumps({"total": total, "board_list": board_list_serializable})

    
    await redis_conn.set(cache_board_list_key, timedelta(hours=2), cache_data )

    return {"total": total, "board_list": board_list_serializable}


