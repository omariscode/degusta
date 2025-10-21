"""Model package for api app.

Import the model modules here so Django discovers and registers them when it imports
``api.models``. Cross-model references use app-label strings (for example 'api.User')
to avoid circular import problems.
"""

# Import model modules so Django registers model classes
from . import user_model  # noqa: F401
from . import product_model  # noqa: F401
from . import order_model  # noqa: F401
from . import invoice_model  # noqa: F401

__all__ = [
	'user_model',
	'product_model',
	'order_model',
	'invoice_model',
]
