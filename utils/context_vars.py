from asyncio import AbstractEventLoop
from contextvars import ContextVar

user_id: ContextVar[int] = ContextVar("user_id", default=None)
loop_async: ContextVar[AbstractEventLoop] = ContextVar("loop_async", default=None)
admin: ContextVar[bool] = ContextVar("admin", default=False)