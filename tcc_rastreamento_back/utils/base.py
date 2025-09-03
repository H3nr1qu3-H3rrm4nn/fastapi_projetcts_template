# Este arquivo define a Base declarativa do SQLAlchemy.
# Todas as classes de modelo da sua aplicação (como Usuario, Veiculo, etc.)
# deverão herdar desta 'Base' para serem mapeadas corretamente para
# as tabelas do banco de dados.

from sqlalchemy.orm import declarative_base

# Cria a classe Base da qual todos os modelos ORM herdarão.
Base = declarative_base()