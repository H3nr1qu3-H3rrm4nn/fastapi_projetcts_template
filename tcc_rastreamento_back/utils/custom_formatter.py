import logging
import random
import string
from datetime import datetime
from utils.context_vars import user_id
from utils.context_vars import tenant_id

class CustomFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        now = datetime.now()
        seed = int(now.timestamp() * 1000)  # Converte o horário atual para milissegundos
        random.seed(seed)
        self.user_id_getter = user_id.get()
        self.tenant_id_getter = tenant_id.get()

    def format(self, record):
        record.code = self.generate_code()
        record.user_id = self.get_user_id()
        record.tenant_id = self.get_tenant_id()
        return super().format(record)

    def generate_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def get_user_id(self):
        if self.user_id_getter:
            return self.user_id_getter
        return 'unknown_user'
    
    def get_tenant_id(self):
        if self.tenant_id_getter:
            return self.tenant_id_getter
        return 'unknown_tenant'