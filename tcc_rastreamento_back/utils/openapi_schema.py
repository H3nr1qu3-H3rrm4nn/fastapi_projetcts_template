from fastapi.openapi.utils import get_openapi
from utils.settings import settings

def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_name,
        version="1.0.0",
        description="Rastreamento Api",
        routes=app.routes,
    )
    openapi_schema['components']['securitySchemes'] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation.setdefault("security", [])
            operation["security"].append({"BearerAuth": []})
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
