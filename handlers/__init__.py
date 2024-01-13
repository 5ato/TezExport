__all__ = [
    'handlers'
]

from .users import user_handlers
from .products import product_handlers


handlers = [
    *user_handlers,
    *product_handlers,
]