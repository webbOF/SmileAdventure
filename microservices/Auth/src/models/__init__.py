# Import all models to ensure they're registered with SQLAlchemy
from .user_model import User

__all__ = ["User"]
