from .base import customInput

VERSION = "1.0.0"

def isYesOrNo(text: str) -> bool:
    if text.lower() in ['y', "n", "ye", "no", "yes", "yea", "yeah", "noo"]:
        return True

    return False

def strToBool(text: str) -> bool:
    if text in ['y', 'ye', 'yes', 'yea', 'yeah']:
        return True

    return False

def input(prompt: str) -> bool:
    """An alias to confirm something"""
    return customInput(prompt, [isYesOrNo], "Must be yes or no. Try Again", transformers=[lambda text: text.lower(), strToBool])