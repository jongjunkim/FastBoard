from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException, Response, Request
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status
from domain.user.user_crud import pwd_context

from database import get_async_db, get_redis_connection
from domain.user import user_crud, user_schema
import redis
import uuid
import aioredis

from sqlalchemy.ext.asyncio import AsyncSession

ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = "12063be504231ea7b8538a49adc46582ac8c99e40becf99f968647de4943ae35"
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

router = APIRouter(
    prefix="/api/user",
)

@router.post("/signup", status_code=status.HTTP_204_NO_CONTENT)
async def user_create(_user_create: user_schema.UserCreate, db: AsyncSession = Depends(get_async_db)):
    
    user = await user_crud.get_user(db, _user_create.email)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다.")
    
    await user_crud.sign_up(db=db, new_user=_user_create)


@router.post("/login", response_model=user_schema.Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):

    user = await user_crud.get_user(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="존재하지 않는 이메일입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 맞지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jti = str(uuid.uuid4())
    
    # make access token
    data = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": jti
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    response.set_cookie(key="access_token", value=access_token, expires=ACCESS_TOKEN_EXPIRE_MINUTES, httponly=True)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email
    }

@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, request: Request, redis_conn: redis.StrictRedis = Depends(get_redis_connection)):
    access_token = request.cookies.get("access_token")
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        token_id = payload.get("jti")

        if token_id:
            await redis_conn.setex(token_id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), 'blacklisted')
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰 디코딩 실패")
    
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        email: str = payload.get("sub") #FastAPI의 security 패키지에 있는 OAuth2PasswordBearer에 의해 자동 매핑
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        email = await user_crud.get_user(db, email)
        if email is None:
            raise credentials_exception
        return email