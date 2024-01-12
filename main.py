from fastapi import FastAPI
from domain.user import user_router
from domain.board import board_router

app = FastAPI()

app.include_router(user_router.router)
app.include_router(board_router.router)
