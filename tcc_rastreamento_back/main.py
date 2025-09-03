
from fastapi import FastAPI

from tcc_rastreamento_back.utils.base import Base


# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Rastreamento de Frota",
    description="API para o TCC de Análise e Desenvolvimento de Sistemas.",
    version="1.0.0"
)

# Inclui apenas o roteador de usuários, que agora contém o login
app.include_router(usuario.router, prefix="/api/v1/usuarios", tags=["Usuarios"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Rastreamento!"}