from datetime import datetime
from sqlalchemy_continuum import versioning_manager
from sqlalchemy import inspect
from utils.context_vars import user_id


def has_actual_changes(obj):
    insp = inspect(obj)
    
    for attr in insp.attrs:
        history = getattr(insp.attrs, attr.key).history
        if history.has_changes():
            if history.added and history.deleted:
                if history.added[0] != history.deleted[0]:
                    return True
    return False


