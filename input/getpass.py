from inputkit import Key, handleInput
from typing import overload
from io import StringIO
import sys

VERSION = "1.0.0"

class Counter:
    def __init__(self, value: int = 0) -> None:
        self.val = value

    def increment(self, amount: int = 1) -> None:
        self.val += amount

    def decrement(self, amount: int = 1) -> None:
        self.val -= amount

    def __int__(self) -> int:
        return self.val

def input(prompt: str = "Password: ", voidCtrlC: bool = True) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    inputBuf: StringIO = StringIO()
    cur: Counter = Counter()
    def inpHandler(key: Key | str) -> bool:
        if isinstance(key, str):
            inputBuf.write(key)
            cur.increment()
            return True

        match key:
            case Key.BACKSPACE:
                forwardInput = inputBuf.read()
                cur.decrement()
                if cur.val == -1:
                    cur.val = 0
                    return True

                inputBuf.seek(cur.val)
                inputBuf.truncate()
                inputBuf.write(forwardInput)
                inputBuf.seek(cur.val)

            case Key.DEL:
                inputBuf.seek(cur.val+1)
                forwardInput = inputBuf.read()
                inputBuf.seek(cur.val)
                inputBuf.truncate()
                inputBuf.write(forwardInput)
                inputBuf.seek(cur.val)

            case Key.ENTER:
                return False

            case Key.CTRL_C:
                if not voidCtrlC:
                    raise KeyboardInterrupt

            case Key.RIGHT:
                inputBuf.seek(0, 2)
                bufLength = inputBuf.tell()
                if cur.val == bufLength:
                    return True

                cur.increment()
                inputBuf.seek(cur.val)

            case Key.LEFT:
                cur.decrement()
                if cur.val < 0:
                    cur.val = 0

                else:
                    inputBuf.seek(cur.val)

        return True

    handleInput(inpHandler, False)
    print()

    res = inputBuf.getvalue()

    return res

@overload
def confirm() -> str: ...

@overload
def confirm(prompt: str = "Password: ", confirmPrompt: str = "Confirm password: ") -> str: ...

@overload
def confirm(prompt: str = "Password: ", confirmPrompt: str = "Confirm password: ", retry: bool = False) -> str | None: ...

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
    for attempt in range(tries):
        attemptedInput = input(prompt)
        if attemptedInput == password:
            return True

        if attempt < tries - 1:
            print(f"{"\x1b[31m" if color else ""}Incorrect. Try Again{"\x1b[0m" if color else ""}")

    return False

if __name__ == "__main__":
    password = check("123456")