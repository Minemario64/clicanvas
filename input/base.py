from inputkit import Key, handleInput
from typing import Callable, overload, Any
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

def input(prompt: str, voidCtrlC: bool = True) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    inputBuf: StringIO = StringIO()
    cur: Counter = Counter()
    def inpHandler(key: Key | str) -> bool:
        if isinstance(key, str):
            inputBuf.write(key)
            cur.increment()
            sys.stdout.write(key)
            sys.stdout.flush()
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
                sys.stdout.write(f"\x1b[D{" "*(len(forwardInput)+1)}\x1b[{len(forwardInput)+1}D{f"{forwardInput}\x1b[{len(forwardInput)}D" if forwardInput else ""}")
                sys.stdout.flush()

            case Key.DEL:
                inputBuf.seek(cur.val+1)
                forwardInput = inputBuf.read()
                inputBuf.seek(cur.val)
                inputBuf.truncate()
                inputBuf.write(forwardInput)
                inputBuf.seek(cur.val)
                sys.stdout.write(f"{" "*(len(forwardInput)+1)}\x1b[{len(forwardInput)+1}D{f"{forwardInput}\x1b[{len(forwardInput)}D" if forwardInput else ""}")
                sys.stdout.flush()

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
                sys.stdout.write("\x1b[C")
                sys.stdout.flush()

            case Key.LEFT:
                cur.decrement()
                if cur.val < 0:
                    cur.val = 0

                else:
                    inputBuf.seek(cur.val)
                    sys.stdout.write("\x1b[D")
                    sys.stdout.flush()

        return True

    handleInput(inpHandler, False)
    print()

    res = inputBuf.getvalue()

    return res

@overload
def customInput(prompt: str, validators: list[Callable[[str], bool]], failResponse: str = "Try Again.",*, inputFunc: Callable[[str], str] = input) -> str: ...

@overload
def customInput(prompt: str, validators: list[Callable[[str], bool]], failResponse: str = "Try Again.",*, transformers: list[Callable], inputFunc: Callable[[str], str] = input) -> Any: ...

def customInput(prompt: str, validators: list[Callable[[str], bool]], failResponse: str = "Try Again.",*, inputFunc: Callable[[str], str] = input, transformers: list[Callable] | None = None) -> str | Any:
    while True:
        inp = inputFunc(prompt)
        if all([validator(inp) for validator in validators]):
            break

        print(failResponse)

    if transformers is None:
        return inp

    res: Any = inp
    for transformer in transformers:
        res = transformer(res)

    return res

if __name__ == "__main__":
    input("Hello: ")
    def isInt(input: str) -> bool:
        try:
            int(input)
            return True

        except Exception:
            return False

    customInput("Input an integer: ", [isInt], "Input an integer. Try Again.", transformers=[int])