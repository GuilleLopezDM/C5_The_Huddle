# Expone el blueprint que recibe logs por POST.
from .logs_post import logs_post_bp
# Expone el blueprint que consulta logs por GET.
from .logs_get import logs_get_bp

# Define que objetos se exportan al hacer `from routes import ...`.
__all__ = ["logs_post_bp", "logs_get_bp"]
