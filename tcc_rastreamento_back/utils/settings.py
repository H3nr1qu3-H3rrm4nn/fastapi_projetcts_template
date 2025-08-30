from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.app_enviroment import AppEnvironment

class Settings(BaseSettings):
    """
    Define as configurações lidas de variáveis de ambiente ou de um arquivo .env.
    """
    # Carrega as variáveis de um arquivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    # Configurações do Ambiente
    APP_ENV: AppEnvironment = AppEnvironment.DEVELOPMENT

    # Configurações do Banco de Dados
    DATABASE_URL: str = "postgresql://admin:admin@db:5432/rastreamento_db"

    def is_development(self) -> bool:
        """ Verifica se o ambiente é de desenvolvimento. """
        return self.APP_ENV == AppEnvironment.DEVELOPMENT

    def is_production(self) -> bool:
        """ Verifica se o ambiente é de produção. """
        return self.APP_ENV == AppEnvironment.PRODUCTION