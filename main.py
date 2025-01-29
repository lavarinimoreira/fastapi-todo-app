from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, admin, users


app = FastAPI()

# A linha do código abaixo será executado somente se o "todo database" não existir.
models.Base.metadata.create_all(bind=engine)

@app.get('/healthy')
def health_check():
    return{'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

# Observações:

# Pydantic v1 vs Pydantic v2
# FastAPI agora é compatível com Pydantic v1 e Pydantic v2.

# Com base na nova versão do FastAPI, pode haver pequenas alterações no nome do método.

# As três maiores são:

# A função .dict() agora foi renomeada para .model_dump()

# A função schema_extra dentro de uma classe Config agora foi renomeada para json_schema_extra

# Variáveis ​​opcionais precisam de um exemplo =None: id: Opcional[int] = None
