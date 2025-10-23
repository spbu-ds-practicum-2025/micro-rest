from .base_class import Base # noqa


# Импорт моделей — важно для create_all
from app.models.module import Module # noqa
from app.models.task import Task # noqa