from fastapi import FastAPI, UploadFile, Depends, HTTPException, status, File
from pydantic import BaseModel
from typing import List, Annotated, Union
from dotenv import load_dotenv
from database import SessionLocal, engine
from sqlalchemy.orm import Session
import asyncio
import models
import shutil
import openai
from datetime import timedelta
import os
import auth
from auth import get_current_user
from chat import Chatbot
# importing the class/model that has the answer

chatbot = Chatbot()


class Base(BaseModel):
    prompt: str

chat_llm = Chatbot()

app = FastAPI() 
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db  
    finally: 
        db.close() 


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@app.get("/user", status_code=status.HTTP_200_OK)
async def user(user:user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return {"User": user}

@app.get("/status")
async def get_status():
    return {"status": "OK"}

@app.post("/predict")
async def predict(prompt: str, user:user_dependency, files: List[UploadFile]):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    for file in files:
        if file.content_type != "application/pdf":
            print("One or more files are not pdf-s. Please try again")
            break
        else:
            _, files = chat_llm.get_path()
            if file.filename not in files:
                with open(f"pdf_files/{file.filename}", "wb") as f:
                    shutil.copyfileobj(file.file, f)
        chain = chatbot.get_chain().run(question=prompt)
        try:
            return {"prompt": prompt, "response": chain}
        except openai.APITimeoutError as e:
            print(e)


        





