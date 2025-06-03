from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.academic_advisor import agent

class Message(BaseModel):
    text: str

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the WestTrack v2.0 back end."}

@app.post("/prompt")
def prompt(msg: Message):
    response: str = agent.turn(msg.text)
    
    return {
        "message": response,
        "prompt": msg.text
    }