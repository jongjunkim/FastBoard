from fastapi import FastAPI
from domain.user import user_router
from domain.board import board_router
from domain.post import post_router
from domain.answer import answer_router

app = FastAPI()

app.include_router(user_router.router)
app.include_router(board_router.router)
app.include_router(post_router.router)
app.include_router(answer_router.router)
