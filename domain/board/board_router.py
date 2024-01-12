from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status
from domain.user.user_router import get_current_user
from models import User

from database import get_db
from domain.board import board_crud, board_schema

router = APIRouter(
    prefix="/api/board",
)

@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def board_create(_board_create: board_schema.BoardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    board = board_crud.exisiting_board(db, _board = _board_create)

    if board:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 게시판 이름입니다")

    board_crud.create_board(db=db, new_board=_board_create, user = current_user)


@router.put("/update", status_code = status.HTTP_204_NO_CONTENT)
def board_update(_board_update: board_schema.BoardUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    db_board = board_crud.get_board_id(db, board_id = _board_update.board_id)
    if not db_board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="게시판을 찾을수 없습니다.")
    
    if current_user.id != db_board.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")


    board_crud.update_board(db=db, db_board = db_board, board_update = _board_update)


@router.delete("/delete", status_code = status.HTTP_204_NO_CONTENT)
def board_delete(_board_delete: board_schema.BoardDelete, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    db_board = board_crud.get_board_id(db, board_id = _board_delete.board_id)
    if not db_board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="게시판을 찾을수 없습니다.")
    
    if current_user.id != db_board.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")

    board_crud.delete_board(db=db, db_board = db_board)
