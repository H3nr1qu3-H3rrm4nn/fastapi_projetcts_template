import logging
import logging.config
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import yaml
from utils.response_model import ResponseModel
from utils.exception_model import ExceptionModel

with open("logging.yaml", "rt") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)

class Exceptions():

    def __init__(self, app):
        self.app = app

        @app.exception_handler(ExceptionModel)
        async def exception_handling(request: Request, exc: ExceptionModel):
            logger.error(exc.message)
            return JSONResponse(
                status_code=exc.status_code,
                content=ResponseModel(
                    success=False,
                    object={},
                    message=exc.message
                ).model_response()
            )
        
        @app.exception_handler(HTTPException)
        async def exception_handling(request: Request, exc: HTTPException):
            logger.error(exc.detail)
            return JSONResponse(
                status_code=exc.status_code,
                content=ResponseModel(
                    success=False,
                    object={},
                    message=exc.detail
                ).model_response()
            )
        
        @app.exception_handler(RequestValidationError)
        async def exception_handling(request: Request, exc: RequestValidationError):
            errors = exc.errors()
            logger.error(exc)
            return JSONResponse(
                status_code=422,
                content=ResponseModel(
                    success=False,
                    object=str(exc),
                message='Oops.. Não foi possível processar a requisição! - RequestValidationError'
                ).model_response()
            )
        
        @app.exception_handler(IntegrityError)
        async def exception_handling(request: Request, exc: IntegrityError):
            logger.error('Oops.. Já existe uma entidade criada com estes dados! - IntegrityError'
                      if 'UniqueViolation' in str(exc) else 
                      'Oops.. Não foi possível realizar a operação no banco de dados, existem entidades vinculadas! - IntegrityError')
            return JSONResponse(
                status_code=409 if 'ForeignKeyViolation' in str(exc) else 400 ,
                content=ResponseModel(
                    success=False,
                    object={},
                    message='Oops.. Já existe uma entidade criada com estes dados! - IntegrityError'
                      if 'UniqueViolation' in str(exc) else 
                      'Oops.. Não foi possível realizar a operação no banco de dados, existem entidades vinculadas! - IntegrityError'
                ).model_response()
            )
        
        @app.exception_handler(AttributeError)
        async def exception_handling(request: Request, exc: AttributeError):
            logger.error(f'Oops.. Não foi possível concluir a tarefa com o atributo fornecido! - AttributeError {exc.args}')
            return JSONResponse(
                status_code=400,
                content=ResponseModel(
                    success=False,
                    object={},
                    message=f'Oops.. Não foi possível concluir a tarefa com o atributo fornecido! - AttributeError {exc.args}'
                ).model_response()
            )