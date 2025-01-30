# Importações necessárias do SQLAlchemy para criar e gerenciar a conexão com o banco de dados
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# Importações do projeto (Base para os modelos do banco, app para a aplicação FastAPI e dependências de autenticação)
from database import Base
from main import app
from routers.todos import get_db, get_current_user

# Importações do FastAPI TestClient para testar a API
from fastapi.testclient import TestClient
from fastapi import status

import pytest
from models import Todos as TodosModel


# Configuração do banco de dados para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Criação do mecanismo de banco de dados SQLite para testes
# Usamos `StaticPool` para evitar problemas de concorrência em testes
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

# Criamos uma sessão de banco de dados específica para testes
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criamos as tabelas no banco de testes com base nos modelos definidos na aplicação
Base.metadata.create_all(bind=engine)


# Função que substitui a dependência do banco de dados original pela versão de teste
def override_get_db():
    db = TestingSessionLocal()  # Criamos uma nova sessão de banco de dados
    try:
        yield db  # Passamos a sessão para os testes
    finally:
        db.close()  # Fechamos a sessão após o teste


# Função que substitui a autenticação real por um usuário fictício
def override_get_current_user():
    return {'sub': 'test_user', 'id': 1, 'role': 'admin'}  # Retorna um usuário fictício para os testes


# Substituímos as dependências originais da API por versões "mockadas" para testes
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Criamos um cliente de teste para fazer requisições à API simulada
client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = TodosModel(
        title='Test Todo',
        description='Test Description', 
        priority=3, 
        complete=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    # APÓS O TESTE, LIMPA O BANCO DE DADOS
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


# Teste para verificar se a rota '/' responde corretamente para usuários autenticados
def test_read_all_authenticated(test_todo):
    response = client.get('/')  # Faz uma requisição GET na raiz da API

    assert response.status_code == status.HTTP_200_OK  # Verifica se o status retornado é 200 (OK)
    assert response.json() == [{
        'complete': False, 
        'title': 'Test Todo', 
        'description': 'Test Description', 
        'id': 1, 
        'priority': 3, 
        'owner_id': 1
    }]


def test_read_one_authenticated(test_todo):
    response = client.get('/todo/1')  # Faz uma requisição GET na raiz da API

    assert response.status_code == status.HTTP_200_OK  # Verifica se o status retornado é 200 (OK)
    assert response.json() == {
        'complete': False, 
        'title': 'Test Todo', 
        'description': 'Test Description', 
        'id': 1, 
        'priority': 3, 
        'owner_id': 1
    }

def test_read_one_authenticated_not_found():
    response = client.get('/todo/999')  # Faz uma requisição GET na raiz da API

    assert response.status_code == status.HTTP_404_NOT_FOUND  # Verifica se o status retornado é 404 (NOT FOUND)
    assert response.json() == {'detail': 'Todo not found.'}

def test_create_todo(test_todo):
    request_data = {
        'title': 'New Todo',
        'description': 'New todo description',
        'priority': 5,
        'complete': False
    }

    response = client.post('/todo', json=request_data)  # Faz uma requisição POST na rota '/todo'
    assert response.status_code == status.HTTP_201_CREATED  # Verifica se o status retornado é 201 (CREATED)

    db = TestingSessionLocal()
    model = db.query(TodosModel).filter(TodosModel.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

def test_update_todo(test_todo):
    request_data = {
        'title': 'Updated Todo',
        'description': 'Updated todo description',
        'priority': 1,
        'complete': True
    }

    response = client.put('/todo/1', json=request_data)  # Faz uma requisição PUT na rota '/todo'
    assert response.status_code == status.HTTP_204_NO_CONTENT  # Verifica se o status retornado é 204 (NO CONTENT)

    db = TestingSessionLocal()
    model = db.query(TodosModel).filter(TodosModel.id == 1).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Updated Todo',
        'description': 'Updated todo description',
        'priority': 1,
        'complete': True
    }

    response = client.put('/todo/999', json=request_data)  # Faz uma requisição PUT na rota '/todo'
    assert response.status_code == status.HTTP_404_NOT_FOUND  # Verifica se o status retornado é 404 (NOT FOUND)
    assert response.json() == {'detail': 'Todo not found.'}  # Verifica se a mensagem de erro é a esperada


def test_delete_todo(test_todo):
    response = client.delete('/todo/1')  # Faz uma requisição DELETE na rota '/todo'
    assert response.status_code == status.HTTP_204_NO_CONTENT  # Verifica se o status retornado é 204 (NO CONTENT)

    db = TestingSessionLocal()
    model = db.query(TodosModel).filter(TodosModel.id == 1).first()
    assert model is None  # Verifica se o registro foi removido do banco de dados


def test_delete_todo_not_found():
    response = client.delete('/todo/999')  # Faz uma requisição DELETE na rota '/todo'
    assert response.status_code == status.HTTP_404_NOT_FOUND  # Verifica se o status retornado é 404 (NOT FOUND)
    assert response.json() == {'detail': 'Todo not found.'}  # Verifica se a mensagem de erro é a esperada