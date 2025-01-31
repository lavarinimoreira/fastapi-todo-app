from routers.todos import get_db, get_current_user
from fastapi import status
from .utils import *


# Substituímos as dependências originais da API por versões "mockadas" para testes
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user



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