from enum import Enum


class TaskStatus(Enum):
    CREATED = 'CREATED'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    CANCELLED = 'CANCELLED'
    EXPIRED = 'EXPIRED'

    @classmethod
    def choices(cls):
        return [(key.value, key.name.capitalize()) for key in cls]
