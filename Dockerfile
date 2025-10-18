FROM python:3.13-slim

# Configurações gerais do Python e Poetry
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
  && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false

# Copia manifestos primeiro (cache das dependências)
COPY pyproject.toml poetry.lock* ./

# Instala dependências principais
RUN poetry install --no-interaction --no-ansi --only main --no-root

# 🔹 Instala debugpy explicitamente (pode estar fora das deps principais)
RUN pip install debugpy

# Copia o código da aplicação
COPY core ./core
COPY utils ./utils
COPY middleware ./middleware
COPY main.py ./main.py

# Permite imports absolutos simples
ENV PYTHONPATH="/app"

# Expor portas da aplicação e do debug
EXPOSE 8000 5678

# 🔹 Comando de inicialização com debugpy + reload
CMD ["sh", "-c", "python -m debugpy --listen 0.0.0.0:5678 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
