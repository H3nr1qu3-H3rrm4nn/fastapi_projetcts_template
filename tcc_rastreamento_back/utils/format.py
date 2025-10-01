import base64
import struct
from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy import and_, func, or_
from sqlalchemy.inspection import inspect


T = TypeVar("T")


def serialize_model(model):
    return {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}
    # serialized = {}
    # mapper = inspect(model).mapper

    # # Colunas
    # for column in mapper.column_attrs:
    #     serialized[column.key] = getattr(model, column.key)

    # # Relacionamentos
    # for relationship in mapper.relationships:
    #     value = getattr(model, relationship.key)
    #     if value is not None:
    #         if relationship.uselist:
    #             serialized[relationship.key] = [serialize_model(item) for item in value]
    #         else:
    #             serialized[relationship.key] = serialize_model(value)
    #     else:
    #         serialized[relationship.key] = None

    # return serialized


def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

def create_model_instance(model: T, new_data: Any):
    if not isinstance(new_data, dict):
        new_data = new_data.__dict__

    model_keys = set(model.__table__.columns.keys())
    filtered_new_data = {k: v for k, v in new_data.items() if k in model_keys}

    db_model = model(**filtered_new_data)
    db_model.created_at = datetime.now()

    return db_model

def format_update_instance(new_data: Any):
    if not isinstance(new_data, dict):
        new_data = new_data.__dict__

    new_data["updated_at"] = datetime.now()

    return new_data

def encodeIntToBase64(value):
    bytes_value = struct.pack(">i", value)
    base64_string = base64.b64encode(bytes_value).decode("utf-8")
    return base64_string

def format_number_for_view(num):

    if num is None:
        return num

    num = float(num)
    formatted_number = f"{num:.2f}"

    integer_part, decimal_part = formatted_number.split(".")

    reversed_integer = integer_part[::-1]

    grouped_integer = ".".join(
        [reversed_integer[i : i + 3] for i in range(0, len(reversed_integer), 3)]
    )

    final_result = grouped_integer[::-1] + "," + decimal_part
    return final_result


def apply_dynamic_filters(query, model, filters):
    operations = []
    last_condition = "AND"  # <-- Inicializa com um valor padrão

    operator_mapping = {
        "EQUALS": lambda f, v: f == v,
        "NOT_EQUALS": lambda f, v: func.upper(f) != func.upper(v),
        "GREATER_THAN": lambda f, v: func.upper(f) > func.upper(v),
        "LESS_THAN": lambda f, v: func.upper(f) < func.upper(v),
        "GREATER_THAN_OR_EQUAL": lambda f, v: func.upper(f) >= func.upper(v),
        "LESS_THAN_OR_EQUAL": lambda f, v: func.upper(f) <= func.upper(v),
        "CONTAINS": lambda f, v: func.upper(f).like(f"%{v.upper()}%"),
        "NOT_CONTAINS": lambda f, v: ~func.upper(f).like(f"%{v.upper()}%"),
        "BETWEEN": lambda f, v1, v2: f.between(v1, v2),
    }

    if filters and filters.filters:  # <-- Evita erro se filters for None ou []
        for filter_obj in filters.filters:
            attribute_parts = filter_obj.attribute.split(".")
            if len(attribute_parts) > 1:
                related_model = getattr(model, attribute_parts[0].lower())
                col = getattr(
                    related_model.property.mapper.class_, attribute_parts[1].lower()
                )
            elif hasattr(model, filter_obj.attribute.lower()):
                col = getattr(model, filter_obj.attribute.lower())
            else:
                raise AttributeError(
                    f"Atributo {filter_obj.attribute} não encontrado no modelo ou relacionamentos."
                )

            if filter_obj.operator.upper() == "BETWEEN":
                cond = operator_mapping[filter_obj.operator.upper()](
                    col, filter_obj.primary_value, filter_obj.secondary_value
                )
            else:
                cond = operator_mapping[filter_obj.operator.upper()](
                    col,
                    (
                        filter_obj.primary_value.upper()
                        if isinstance(filter_obj.primary_value, str)
                        else filter_obj.primary_value
                    ),
                )

            operations.append(cond)
            last_condition = filter_obj.condition.upper()

    if operations:  # <-- Só aplica filtros se houver condições
        if last_condition == "AND":
            query = query.filter(and_(*operations))
        else:
            query = query.filter(or_(*operations))

    return query

        
def greetings():
    current_time = datetime.now().hour

    if 6 <= current_time < 12:
        return "Bom dia"
    elif 12 <= current_time < 18:
        return "Boa tarde"
    else:
        return "Boa noite"
    
def dict_to_object(dict_data, class_type):
    obj = class_type()
    for key, value in dict_data.items():
        if hasattr(obj, key):  # Verifica se o atributo existe na classe
            setattr(obj, key, value)
    return obj