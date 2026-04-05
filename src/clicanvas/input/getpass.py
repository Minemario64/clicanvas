from inputkit import Key, handleInput
from typing import overload
from io import StringIO
import sys

VERSION = "1.0.0"

_ANSI_START = "\x1b["

def input(prompt: str = "Password: ", voidCtrlC: bool = True) -> str:
    """A mirror to getpass.getpass() which doesn't display the user input

    Args:
        prompt (str, optional): The user prompt. Defaults to "Password: ".
        voidCtrlC (bool, optional): If Ctrl+C would be voided and not raise a KeyboardInterrupt. Defaults to True.

    Raises:
        KeyboardInterrupt: If the user presses Ctrl+C and voidCtrlC is False

    Returns:
        str: The user input
    """
    sys.stdout.write(prompt)
    sys.stdout.flush()
    inputBuf: StringIO = StringIO()
    cur: int = 0
    @handleInput(hideCursor=True)
    def inpHandler(key: Key | str) -> bool:
        nonlocal cur
        if isinstance(key, str):
            inputBuf.write(key)
            cur += 1
            return True

        match key:
            case Key.BACKSPACE:
                forwardInput = inputBuf.read()
                cur -= 1
                if cur == -1:
                    cur = 0
                    return True

                inputBuf.seek(cur)
                inputBuf.truncate()
                inputBuf.write(forwardInput)
                inputBuf.seek(cur)

            case Key.DEL:
                inputBuf.seek(cur+1)
                forwardInput = inputBuf.read()
                inputBuf.seek(cur)
                inputBuf.truncate()
                inputBuf.write(forwardInput)
                inputBuf.seek(cur)

            case Key.ENTER:
                return False

            case Key.CTRL_C:
                if not voidCtrlC:
                    raise KeyboardInterrupt

            case Key.RIGHT:
                inputBuf.seek(0, 2)
                bufLength = inputBuf.tell()
                if cur == bufLength:
                    return True

                cur += 1
                inputBuf.seek(cur)

            case Key.LEFT:
                cur -= 1
                if cur < 0:
                    cur = 0

                else:
                    inputBuf.seek(cur)

        return True

    print()

    res = inputBuf.getvalue()

    return res

@overload
def confirm() -> str: """An alias to confirm a password with retries"""

@overload
def confirm(prompt: str = "Password: ", confirmPrompt: str = "Confirm password: ") -> str: """An alias to confirm a password with retries"""

@overload
def confirm(prompt: str = "Password: ", confirmPrompt: str = "Confirm password: ", retry: bool = False) -> str | None: """An alias to confirm a password but without retries"""

def confirm(prompt: str = "Password: ", confirmPrompt: str = "Confirm password: ", retry: bool = True) -> str | None:
    while True:
        password: str = input(prompt)
        confirmedPassword: str = input(confirmPrompt)
        if not (password == confirmedPassword):
            if not retry:
                return None

        else:
            break

    return password

def check(password: str, prompt: str = "Password: ", tries: int = 3, color: bool = True) -> bool:
    """An alias to check if a password matches the user input

    Args:
        password (str): The correct password
        prompt (str, optional): The prompt for the user. Defaults to "Password: ".
        tries (int, optional): The amount of tries the user gets before failing. Defaults to 3.
        color (bool, optional): If the response to if the user input is incorrect should have color. Defaults to True.

    Returns:
        bool: If the check passed, and they got the password correct
    """
    for attempt in range(tries):
        attemptedInput = input(prompt)
        if attemptedInput == password:
            return True

        if attempt < tries - 1:
            print(f"{f'{_ANSI_START}31m' if color else ''}Incorrect. Try Again{f'{_ANSI_START}0m' if color else ''}")

    return False

if __name__ == "__main__":
    password = check("123456")