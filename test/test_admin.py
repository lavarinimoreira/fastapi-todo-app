"""
    This file contains tests for the admin endpoints of the API.

    Always make sure to import all the dependencies and functions needed for the tests to run.
"""
from .utils import *
from routers.admin import get_db, get_current_user # OVERRIDE this functions to use the test database and a fake user
from models import Todos as TodosModel # Import the TodosModel to create a test todo

app.dependency_overrides[get_db] = override_get_db # Override the get_db function to use the test database
app.dependency_overrides[get_current_user] = override_get_current_user # Override the get_current_user function to use a fake user


def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id": 1, 
                                "title": "Test Todo", 
                                "description": "Test Description", 
                                "priority": 3, 
                                "complete": False, 
                                "owner_id": 1}]
    

def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(TodosModel).filter(TodosModel.id == 1).first()
    assert model is None


def test_admin_delete_todo_not_found(test_todo):
    response = client.delete("/admin/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}
