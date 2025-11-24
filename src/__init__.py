import importlib.metadata

from .main import main_async as main_async
from .main import main_sync as main_sync
from .version import APP_NAME, APP_REVISION, APP_VER_MAJOR, APP_VER_SUB, APP_VERSION

__all__ = ('APP_NAME', 'APP_REVISION', 'APP_VERSION', 'APP_VER_MAJOR', 'APP_VER_SUB', 'main_async', 'main_sync')
__version__ = importlib.metadata.version(APP_NAME)
