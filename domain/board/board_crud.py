from sqlalchemy.orm import Session
from models import Board, User
from domain.board.board_schema import BoardCreate, BoardUpdate




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

def delete_board(db: Session, db_board: Board):
    db.delete(db_board)
    db.commit()

#def get()



#def List()