from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Path
from models import Todos as TodosModel
from database import SessionLocal
from .auth import get_current_user


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



# Pydantic para validação
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


# READ routers --------------------------------------------------------------
@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
    return db.query(TodosModel).filter(TodosModel.owner_id == user.get('id')).all()



@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
    
    todo_model = db.query(TodosModel).filter(TodosModel.id == todo_id)\
        .filter(TodosModel.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')





# CREATE routers ----------------------------------------------------------
@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency ,db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')

    # Transformando a requisição (TodoRequest[ou schema...]) para
    # o formado do BANCO DE DADOS TodosModel
    todo_model = TodosModel(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()





# UPDATE routers -----------------------------------------------------------

# update_todo
@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0) ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')

    todo_model = db.query(TodosModel).filter(TodosModel.id == todo_id)\
        .filter(TodosModel.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()




# DELETE routers ---------------------------------------------------------

# delete_todo
@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
    
    todo_model = db.query(TodosModel).filter(TodosModel.id == todo_id)\
        .filter(TodosModel.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')

    db.query(TodosModel).filter(TodosModel.id == todo_id, TodosModel.owner_id == user.get('id')).delete()
    db.commit()