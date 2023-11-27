from datetime import timedelta, datetime 
from typing import Annotated 
from fastapi import APIRouter, Depends, HTTPException 
from pydantic import BaseModel 
from sqlalchemy.orm import Session 
from database import SessionLocal 
from models import Users
from dotenv import load_dotenv
from passlib.context import CryptContext 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
from jose import jwt, JWTError 
from starlette import status
import os

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(""))) + "\\Secret" + "\\.env" )

load_dotenv(dotenv_path=env_path)
secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
outh2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str 
    password: str 

class Token(BaseModel):
    access_token: str 
    token_type: str 


def get_db():
    db = SessionLocal()
    try: 
        yield db 
    finally: 
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,create_user_request: CreateUserRequest):
    create_user_model = Users(
        username = create_user_request.username,
        hashed_password = bcrypt_context.hash(create_user_request.password)
    )


    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    user= authenticate_user(form_data.username, form_data.password, db)
    if not user: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")
    token = create_access_token(user.username, user.id, timedelta(minutes=520))

    return {"access_token": token, "token_type": "bearer"}



def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, secret_key, algorithm=algorithm)


def get_current_user(token:Annotated[str, Depends(outh2_bearer)]):
    jwterror = JWTError()
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user")
        return {"username": username, "id": user_id}
    except jwterror:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not authorize user")
    



def authenticate_user(username:str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user: 
        return False 
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
