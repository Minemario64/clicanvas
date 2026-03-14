from inputkit import Key, handleInput
from typing import Iterable, overload, Any, Iterator, TextIO
from pathlib import Path
from io import StringIO
import sys

VERSION = "1.0.0"

class maxList(list):
    @overload
    def __init__(self,*, maxLen: int = 50) -> None: ...

    @overload
    def __init__(self, iterable: Iterable,*, maxLen: int = 50) -> None: ...

    def __init__(self, iterable: Iterable | None = None,*, maxLen: int = 50) -> None:
        self.__maxLen: int = maxLen
        if iterable is None:
            super().__init__()
        else:
            super().__init__(iterable)

    def changeMaxLen(self, value: int) -> None:
        self.__maxLen = value
        if len(self) > self.__maxLen:
            while len(self) > self.__maxLen:
                self.pop(0)

    def shiftUntilLen(self, length: int) -> None:
        while len(self) > length:
            self.pop()

    def append(self, object: Any) -> None:
        if len(self) >= self.__maxLen:
            self.shiftUntilLen(self.__maxLen - 1)

        return super().insert(0, object)

    def extend(self, iterable: Iterable) -> None:
        if len(iterable) > self.__maxLen: # pyright: ignore[reportArgumentType]
            raise ValueError("Iterable too large")

        elif len(iterable) == self.__maxLen: # pyright: ignore[reportArgumentType]
            self.clear()
            super().extend(iterable)

        if (len(self) + len(iterable)) >= self.__maxLen: # pyright: ignore[reportArgumentType]
            self.shiftUntilLen(len(self) - len(iterable)) # pyright: ignore[reportArgumentType]

        self.reverse()
        super().extend(iterable)
        self.reverse()

class Counter:
    def __init__(self, value: int = 0) -> None:
        self.val = value

    def increment(self, amount: int = 1) -> None:
        self.val += amount

    def decrement(self, amount: int = 1) -> None:
        self.val -= amount

    def __int__(self) -> int:
        return self.val

class SharedStr:
    def __init__(self, val: str = '') -> None:
        self.str = val

    def update(self, val: str) -> None:
        self.str = val

_HIST = maxList([])

@overload
def maxHistory() -> int: ...

@overload
def maxHistory(value: int) -> None: ...

def maxHistory(value: int | None = None) -> int | None:
    if value is None:
        return _HIST._maxList__maxLen # pyright: ignore[reportAttributeAccessIssue]

    else:
        _HIST.changeMaxLen(value)

def loadHistory(file: str | Path | TextIO) -> None:
    if isinstance(file, Path):
        if not file.is_file():
            raise ValueError("Path object must be a file")

    if isinstance(file, str | Path):
        with (open(file, "r", encoding='utf8') if isinstance(file, str) else file.open("r", encoding='utf8')) as fileObj:
            _HIST.clear()
            _HIST.extend(fileObj.read().splitlines())

        return

    elif isinstance(file, TextIO):
        _HIST.clear()
        cursor: int = file.tell()
        file.seek(0)
        _HIST.extend(file.read().splitlines())
        file.seek(cursor)

def input(prompt: str, voidCtrlC: bool = True, connectHistory: bool = True) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    newInputText: SharedStr = SharedStr()
    inputBuf: StringIO = StringIO()
    cur: Counter = Counter()
    historyIdx: Counter = Counter(-1)
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

            case Key.UP | Key.DOWN:
                if connectHistory:
                    if historyIdx.val == -1:
                        newInputText.update(inputBuf.getvalue())

                    historyIdx.increment() if key == Key.UP else historyIdx.decrement()
                    if historyIdx.val < -1:
                        historyIdx.val = -1
                        return True

                    elif historyIdx.val == -1:
                        inputBuf.seek(0, 2)
                        bufLength = inputBuf.tell()
                        inputBuf.seek(cur.val)
                        sys.stdout.write(f"{f"\x1b[{bufLength}D{" "*bufLength}\x1b[{bufLength}D" if bufLength > 0 else ''}{newInputText.str}")
                        sys.stdout.flush()
                        if historyIdx.val == 0:
                            newInputText.update(inputBuf.getvalue())

                        inputBuf.seek(0)
                        inputBuf.truncate(0)
                        inputBuf.write(newInputText.str)
                        cur.val = inputBuf.tell()
                        return True

                    try:
                        inputBuf.seek(0, 2)
                        bufLength = inputBuf.tell()
                        inputBuf.seek(cur.val)
                        sys.stdout.write(f"{f"\x1b[{bufLength}D{" "*bufLength}\x1b[{bufLength}D" if bufLength > 0 else ''}{_HIST[historyIdx.val]}")
                        sys.stdout.flush()

                        inputBuf.seek(0)
                        inputBuf.truncate(0)
                        inputBuf.write(_HIST[historyIdx.val])
                        cur.val = inputBuf.tell()

                    except IndexError:
                        historyIdx.decrement()

        return True

    handleInput(inpHandler, False)
    print()

    res = inputBuf.getvalue()
    if connectHistory:
        _HIST.append(res)

    return res

if __name__ == "__main__":
    loadHistory(".hist")
    import time
    name = input("Name: ", connectHistory=False)
    print(f"Hello, {name}!")

    time.sleep(1)
    confirm = input("Confirm?(y/n): ", connectHistory=False)
    print("Confirmed!" if confirm in ["y", "yes", "ye", "yea", "yeah"] else "Denied.")

    while True:
        input(": ", voidCtrlC=False)