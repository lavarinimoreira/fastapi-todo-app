from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Path
from models import Todos as TodosModel
from models import Users as UsersModel
from database import SessionLocal
from .auth import get_current_user

# Importação do CryptContext para a rota de atualização de senha
from passlib.context import CryptContext


router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 



class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)




# READ routers --------------------------------------------------------------

# read_user
@router.get('/', status_code=status.HTTP_200_OK)
async def read_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return db.query(UsersModel).filter(UsersModel.id == user.get('id')).first()



# UPDATE routers -------------------------------------------------------------

# change_password
@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
    # UserVerification: body of the request.
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
     
    # Getting the model from the database to see if everything is ok:
    user_model = db.query(UsersModel).filter(UsersModel.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(user_model)
    db.commit()



# change_phone_number
@router.put('/phonenumber/{phone_number}', status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    user_model = db.query(UsersModel).filter(UsersModel.id == user.get('id')).first()
    user_model.phone_number = phone_number

    db.add(user_model)
    db.commit()
