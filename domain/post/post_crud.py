from sqlalchemy.orm import Session
from domain.post.post_schema import PostCreate, PostUpdate, PostDelete
from models import User, Board, Post


def create_post(db:Session, board: Board, user: User, post_create: PostCreate):
    db_post = Post(title = post_create.title,
                   content = post_create.content,
                   board = board,
                   user = user)
    db.add(db_post)
    db.commit()

def get_post_id(db:Session, post_id: int):
    return db.query(Post).get(post_id)

def update_post(db: Session, db_post: Post, post_update: PostUpdate):
    db_post.title = post_update.title
    db_post.content = post_update.content
    db.add(db_post)
    db.commit()

def delete_post(db: Session, db_post: PostDelete):
    db.delete(db_post)
    db.commit()


def get_post_list(db: Session, board_id: int, current_user:User, skip: int = 0, limit: int = 10):

    query = db.query(Post)

    query = query.filter((Post.board_id == board_id))

    total = query.count()
    post_list = query.offset(skip).limit(limit).all()

    return total, post_list