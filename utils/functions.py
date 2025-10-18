from sqlalchemy import select, func
from utils.contexts import conditional_session

class Functions:
    # ...existing code...

    async def get_last_id(self, model, session=None):
        """
        Retorna o maior ID do modelo informado.
        """
        async with conditional_session(provided_session=session) as db:
            try:
                query = select(func.max(model.id))
                result = await db.execute(query)
                last_id = result.scalar()
                return last_id if last_id is not None else 0
            except Exception as e:
                # Adapte o logger conforme sua implementação
                print(f"Erro ao buscar o último ID: {str(e)}")
                raise e