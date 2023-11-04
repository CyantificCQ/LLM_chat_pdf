from fastapi import FastAPI, UploadFile, Depends, HTTPException, status
from fastapi.security import  OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Annotated
from dotenv import load_dotenv
import shutil
from datetime import timedelta
import os
from utils import authenticate_user, Token, User, fake_users_db
from utils import create_access_token, get_current_active_user
# importing the class/model that has the answer

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")


class Base(BaseModel):
    prompt: str 


app = FastAPI()
@app.get("/health")
def hello():
    return {"Hello world"}



@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=40)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]



@app.post("/predict")
async def predict(prompt: Base, files: List[UploadFile]):
    path = "pdf_files/"
    file_check = os.listdir(path=path)
    for file in files:
        if file.content_type != "application/pdf":
            print("One or more files are not pdf-s. Please try again")
        else:
            if file.filename not in file_check:
                with open(f"{path}{file.filename}", "wb") as f:
                    shutil.copyfileobj(file.file, f)


    # or shutil.copyfileobj(file.file, f) 
    # if one already has embeddings skip that one or more
    # then create chunks of the pdf files check the prompt and then give back the answer"""
    # response = ""
    return {"Prompt": prompt, "Files":[file.filename for file in files]}


