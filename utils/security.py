from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde à senha com hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha em texto plano."""
    return pwd_context.hash(password)

if __name__ == "__main__":
    # Testando as funções de hash e verificação
    senha = "tracker2025"
    senha_hash = get_password_hash(senha)
    print(f"Senha original: {senha}")
    print(f"Senha com hash: {senha_hash}")
    print(f"Verificação da senha: {verify_password(senha, senha_hash)}")