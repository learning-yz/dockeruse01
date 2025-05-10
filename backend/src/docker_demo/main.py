from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from uuid import uuid4, UUID
import os

MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]
client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING,
                            uuidRepresentation="standard")
db = client.todolist # todolist is the database name, should be created automatically when you first insert a data.
todos = db.todos # todos is the collection name, should be created automatically when you first insert a data.

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoItem(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    content: str

class TodoItemCreate(BaseModel):
    content: str


# todos: list[TodoItem] = []
# id_counter = 1

@app.post("/todos", response_model=TodoItem)
async def create_todo(item: TodoItemCreate):
    # global id_counter
    # new_todo = TodoItem(id=id_counter, content=item.content)
    # todos.append(new_todo)
    # id_counter += 1
    new_todo = TodoItem(content=item.content)
    await todos.insert_one(new_todo.model_dump(by_alias=True))
    return new_todo

@app.get("/todos", response_model=list[TodoItem])
async def read_todos():
    # return todos
    return await todos.find().to_list(length=None)

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: UUID):
# async def delete_todo(todo_id: int):
    # for index, todo in enumerate(todos):
    #     if todo.id == todo_id:
    #         todos.pop(index)
    #         return {"message": "Todo item deleted successfully."}
    delete_result = await todos.delete_one({"_id": todo_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo item not found.")
    else:
        return {"message": "Todo item deleted successfully."}
    