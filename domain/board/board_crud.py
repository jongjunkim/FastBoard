from sqlalchemy.orm import Session
from models import Board, User, Post
from domain.board.board_schema import BoardCreate, BoardUpdate, BoardDelete
from sqlalchemy import and_, func




def create_board(db: Session, new_board: BoardCreate, user:User):
    db_board = Board(name = new_board.name,
                    public = new_board.public,
                    user = user)
    db.add(db_board)
    db.commit()


def exisiting_board(db:Session, _board: BoardCreate):
    return db.query(Board).filter((Board.name == _board.name)).first()

def get_board_id(db:Session, board_id: int):
    return db.query(Board).get(board_id)
    
def update_board(db: Session, db_board: Board, board_update: BoardUpdate):
    db_board.name = board_update.name
    db_board.public = board_update.public
    db.add(db_board)
    db.commit()

def delete_board(db: Session, db_board: BoardDelete):
    db.delete(db_board)
    db.commit()

#게시판에 있는 게시물 순서대로 정렬 해야함
def get_board_list(db: Session, current_user: User, skip: int = 0, limit: int = 10):
    
    query = (
        db.query(Board.id, Board.name, func.count(Post.board_id).label('num_post'))
        .outerjoin(Post, and_(Board.id == Post.board_id))
        .group_by(Board.id)
        .order_by(func.count(Post.board_id).desc())
    )

    query = query.filter((Board.user_id == current_user.id) | (Board.public == True))

    total = query.count()
    board_list = query.offset(skip).limit(limit).all()

    return total, board_list