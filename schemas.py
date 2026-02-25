from pydantic import BaseModel, Field,ConfigDict


class TodoResponse(BaseModel):
    id: int
    title: str = Field(max_length=100, min_length=5)
    completed: bool

    model_config = ConfigDict(from_attributes=True)

class ToUpdate(BaseModel):
    title:str |None = Field(default=None,max_length=100,min_length=5)
    completed:bool|None = None

class ToDoCreate(BaseModel):
    title:str = Field(max_length=100,min_length=5)
    completed:bool


