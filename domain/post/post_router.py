from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models import User
from database import get_db, get_redis_connection
from domain.post import post_schema, post_crud
from domain.user.user_router import get_current_user
from domain.board import board_crud
import redis
import json

router = APIRouter(
    prefix="/api/post",
)

@router.post("/create/{board_id}", status_code=status.HTTP_200_OK)
def post_create(board_id: int, _post_create: post_schema.PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Check if the user has permission to create a post in the specified board
    board = board_crud.get_board_id(db, board_id=board_id)
    if not board or (board.user_id != current_user.id and not board.public):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시판 접근 권한이 없습니다.")

    # Create the post
    post_crud.create_post(db=db, board=board, user=current_user, post_create=_post_create)

    return {"message": "Post created successfully"}

@router.put("/update", status_code=status.HTTP_200_OK)
def post_update(_post_update: post_schema.PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    db_post = post_crud.get_post_id(db, post_id = _post_update.post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="게시글을 찾을수 없습니다.")
    
    if current_user.id != db_post.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")


    post_crud.update_post(db=db, db_post = db_post, post_update = _post_update)

    return {"message": "수정이 완료되었습니다"}

@router.delete("/delete", status_code=status.HTTP_200_OK)
def post_delete(_post_delete: post_schema.PostDelete, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    db_post = post_crud.get_post_id(db, post_id=_post_delete.post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="게시글을 찾을 수 없습니다.")
    
    if current_user.id != db_post.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")

    post_crud.delete_post(db=db, db_post=db_post)

    return {"message": "삭제가 완료되었습니다"}

@router.get("/get/{post_id}", status_code=status.HTTP_200_OK)
def post_get(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
            redis_conn: redis.StrictRedis = Depends(get_redis_connection)):
    
    cache_post_key = f"post_user_{current_user.id}_{post_id}"

    cached_post = redis_conn.get(cache_post_key)

    if cached_post:
        return json.loads(cached_post.decode('utf-8'))

    db_post = post_crud.get_post_id(db, post_id=post_id)
    
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    # 본인이 생성한 게시글이거나 전체 공개된 게시판의 게시글인 경우 조회 가능
    if db_post.user_id != current_user.id and not is_board_public(db, db_post.board_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="조회 권한이 없습니다.")

    redis_conn.setex(cache_post_key, timedelta(hours=2), json.dumps({"post_id": db_post.id, "title": db_post.title, "content": db_post.content}))

    return {"post_id": db_post.id, "title": db_post.title, "content": db_post.content}




# 해당 게시판에 작성된 게시글의 개수로 정렬
@router.get("/list/{board_id}", response_model = post_schema.PostList)
def post_get_list(board_id: int, db:Session = Depends(get_db), current_user: User = Depends(get_current_user),  page:int = 0, size:int = 10,
                    redis_conn: redis.StrictRedis = Depends(get_redis_connection)):

    cache_post_list_key = f"board_{board_id}_user_{current_user.id}_posts_{page}_{size}"

    cached_posts = redis_conn.get(cache_post_list_key)
    if cached_posts:
        return json.loads(cached_posts.decode('utf-8'))


    db_board = board_crud.get_board_id(db, board_id=board_id)

    if not db_board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시판을 찾을 수 없습니다.")

    if not db_board.public and db_board.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="조회 권한이 없습니다.")

    total, _post_list = post_crud.get_post_list(db, board_id, current_user, skip = page * size, limit = size)

    post_list_serializable = [{'id': post.id, 'title': post.title, 'content': post.content} for post in _post_list]
    cache_data = json.dumps({'total': total, 'post_list': post_list_serializable})

    redis_conn.setex(cache_post_list_key, timedelta(hours=2), cache_data)

    return {'total': total,'post_list': _post_list}


def is_board_public(db: Session, board_id: int) -> bool:
    db_board = board_crud.get_board_id(db, board_id=board_id)

    return db_board.public if db_board else False