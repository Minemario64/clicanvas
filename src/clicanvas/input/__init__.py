from .base import input as input
from .readline import input as readline, loadHistory, saveHistory, maxHistory
from .getpass import input as getpass
from .confirm import input as confirm

__all__ = ["input", "readline", "loadHistory", "saveHistory", "getpass", "confirm", "customInput", "getpassConfirm", "getpassCheck", "maxHistory"] # pyright: ignore[reportUnsupportedDunderAll]

def __getattr__(name: str):
    match name:
        case "customInput":
            from .base import customInput
            return customInput

        case "getpassConfirm":
            from .getpass import confirm
            return confirm

        case "getpassCheck":
            from .getpass import check
            return check

    raise AttributeError(name=name)