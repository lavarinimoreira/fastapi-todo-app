# Models is a way for SQL alchemy understand what kind of database tables
# we are going to be creating within our database in the future.

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

# Users (1) ---- (0:n) Todos
# Relação 1:n. Um usuário pode ter zero ou vários "todos".
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String) # Confere se o usuário é administrador ou não. Endpoints específicos serão criados para admins.
    phone_number = Column(String)

# Um "todo" pertence obrigatoriamente a apenas um usuário.
# Na relação 1:n é criado uma coluna na tabela "n" contendo a chave estrangeira.
class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

"""
Revisando os tipos de relacionamento:

(1:1) Normalmente, os dados podem ser mantidos na mesma tabela, mas se houver necessidade de separação lógica
ou otimização de consultas, pode-se criar uma segunda tabela com uma chave estrangeira única referenciando a primeira.

(1:n) O lado "n" da relação recebe uma chave estrangeira referenciando a chave primária da tabela do lado um.

(n:n) Cria-se uma tabela.
"""