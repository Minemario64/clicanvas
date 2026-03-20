from inputkit import Key, handleInput
from typing import Callable, overload, Any
from io import StringIO
import sys

VERSION = "1.0.0"

def input(prompt: str, voidCtrlC: bool = True) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    inputBuf: StringIO = StringIO()
    cur: int = 0
    @handleInput(hideCursor=False)
    def inpHandler(key: Key | str) -> bool:
        nonlocal cur
        if isinstance(key, str):
            inputBuf.write(key)
            cur += 1
            sys.stdout.write(key)
            sys.stdout.flush()
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
                sys.stdout.write(f"\x1b[D{" "*(len(forwardInput)+1)}\x1b[{len(forwardInput)+1}D{f"{forwardInput}\x1b[{len(forwardInput)}D" if forwardInput else ""}")
                sys.stdout.flush()

            case Key.DEL:
                inputBuf.seek(cur+1)
                forwardInput = inputBuf.read()
                inputBuf.seek(cur)
                inputBuf.truncate()
                inputBuf.write(forwardInput)
                inputBuf.seek(cur)
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
                if cur == bufLength:
                    return True

                cur += 1
                inputBuf.seek(cur)
                sys.stdout.write("\x1b[C")
                sys.stdout.flush()

            case Key.LEFT:
                cur -= 1
                if cur < 0:
                    cur = 0

                else:
                    inputBuf.seek(cur)
                    sys.stdout.write("\x1b[D")
                    sys.stdout.flush()

        return True

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
    print(repr(input("Hello: ")))
    def isInt(input: str) -> bool:
        try:
            int(input)
            return True

        except Exception:
            return False

    print(customInput("Input an integer: ", [isInt], "Input an integer. Try Again.", transformers=[int]))