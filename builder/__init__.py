"""Plugin Builder - компилятор многомодульных плагинов"""

from .compiler import compile_plugin
from .sender import send_to_saved

__version__ = "1.0.0"
__all__ = ["compile_plugin", "send_to_saved"]
