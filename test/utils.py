# Importações necessárias do SQLAlchemy para criar e gerenciar a conexão com o banco de dados
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# Importações do projeto (Base para os modelos do banco, app para a aplicação FastAPI e dependências de autenticação)
from database import Base
from main import app

# Importações do FastAPI TestClient para testar a API
from fastapi.testclient import TestClient
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