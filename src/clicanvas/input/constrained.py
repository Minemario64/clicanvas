from inputkit import Key, handleInput
from typing import Callable, overload, Any
from io import StringIO
import sys
import regex as rgx

VERSION = "1.0.0"

def input(prompt: str, rgxRestrictions: list[rgx.Pattern], voidCtrlC: bool = True) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    inputBuf: StringIO = StringIO()
    cur: int = 0
    @handleInput(hideCursor=False)
    def inpHandler(key: Key | str) -> bool:
        nonlocal cur
        if isinstance(key, str):
            cur += 1
            inputBuf.write(key)
            if not any([pattern.match(inputBuf.getvalue(), partial=True) for pattern in rgxRestrictions]):
                cur -= 1
                inputBuf.seek(cur)
                inputBuf.truncate()
                return True

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
                if not any([pattern.match(inputBuf.getvalue(), partial=True) for pattern in rgxRestrictions]):
                    return True

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