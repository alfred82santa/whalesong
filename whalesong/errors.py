class WhalesongException(Exception):
    pass


class ManagerNotFound(WhalesongException):
    pass


class UnknownError(WhalesongException):
    pass


class ChatNotFoundError(WhalesongException):
    pass


class ContactNotFoundError(WhalesongException):
    pass


class StopMonitor(StopAsyncIteration, WhalesongException):
    pass


class StopIterator(StopAsyncIteration, WhalesongException):
    pass


class RequiredExecutionId(WhalesongException):
    pass


class RequiredCommandName(WhalesongException):
    pass


class ModelNotFound(WhalesongException):
    pass
