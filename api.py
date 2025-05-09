from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Conversation(BaseModel):
    id: int
    query: str
    response: str
    timestamp: str
    likes: int
    model_used: str

def get_db_connection():
    conn = sqlite3.connect('research_chat.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/conversations/", response_model=List[Conversation])
def read_conversations(limit: int = 5):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?", (limit,))
    conversations = cursor.fetchall()
    conn.close()
    return conversations

@app.get("/conversations/{conv_id}", response_model=Conversation)
def read_conversation(conv_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
    conversation = cursor.fetchone()
    conn.close()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.post("/conversations/")
def create_conversation(query: str, response: str, model_used: str = "unknown"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (query, response, timestamp, model_used) VALUES (?, ?, datetime('now'), ?)",
        (query, response, model_used)
    )
    conn.commit()
    conv_id = cursor.lastrowid
    conn.close()
    return {"id": conv_id}

@app.put("/conversations/{conv_id}/like")
def like_conversation(conv_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversations SET likes = likes + 1 WHERE id = ?",
        (conv_id,)
    )
    conn.commit()
    conn.close()
    return {"message": "Like added"}

@app.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()
    return {"message": "Conversation deleted"}