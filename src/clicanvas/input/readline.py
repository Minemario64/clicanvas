from inputkit import Key, handleInput
from typing import Iterable, overload, Any, TextIO
from pathlib import Path
from io import StringIO
import sys

VERSION = "1.0.0"

_ANSI_START = "\x1b["

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
            raise ValueError("Path object must be a file.")

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

def saveHistory(filepath: str | Path) -> None:
    if isinstance(filepath, Path):
        if filepath.is_dir():
            raise ValueError("Path must be able to be a file.")

    if not (pathObj := (Path().joinpath(filepath) if isinstance(filepath, str) else filepath)).exists():
        pathObj.touch()

    with pathObj.open("w") as file:
        file.write("\n".join(_HIST))

def input(prompt: str, voidCtrlC: bool = True, connectHistory: bool = True) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    newInputText: str = ''
    inputBuf: StringIO = StringIO()
    cur: int = 0
    historyIdx: int = -1
    @handleInput(hideCursor=False)
    def inpHandler(key: Key | str) -> bool:
        nonlocal newInputText
        nonlocal cur
        nonlocal historyIdx
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
                sys.stdout.write(f"{_ANSI_START}D{' '*(len(forwardInput)+1)}{_ANSI_START}{len(forwardInput)+1}D{f'{forwardInput}{_ANSI_START}{len(forwardInput)}D' if forwardInput else ''}")
                sys.stdout.flush()

            case Key.DEL:
                inputBuf.seek(cur+1)
                forwardInput = inputBuf.read()
                inputBuf.seek(cur)
                inputBuf.truncate()
                inputBuf.write(forwardInput)
                inputBuf.seek(cur)
                sys.stdout.write(f"{' '*(len(forwardInput)+1)}{_ANSI_START}{len(forwardInput)+1}D{f'{forwardInput}{_ANSI_START}{len(forwardInput)}D' if forwardInput else ''}")
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

            case Key.UP | Key.DOWN:
                if connectHistory:
                    if historyIdx == -1:
                        newInputText = inputBuf.getvalue()

                    historyIdx += 1 if key == Key.UP else -1
                    if historyIdx < -1:
                        historyIdx = -1
                        return True

                    elif historyIdx == -1:
                        inputBuf.seek(0, 2)
                        bufLength = inputBuf.tell()
                        inputBuf.seek(cur)
                        sys.stdout.write(f"{f'{_ANSI_START}{bufLength}D{""" """*bufLength}{_ANSI_START}{bufLength}D' if bufLength > 0 else ''}{newInputText}")
                        sys.stdout.flush()

                        inputBuf.seek(0)
                        inputBuf.truncate(0)
                        inputBuf.write(newInputText)
                        cur = inputBuf.tell()
                        return True

                    try:
                        inputBuf.seek(0, 2)
                        bufLength = inputBuf.tell()
                        inputBuf.seek(cur)
                        sys.stdout.write(f"{f'{_ANSI_START}{bufLength}D{""" """*bufLength}{_ANSI_START}{bufLength}D' if bufLength > 0 else ''}{_HIST[historyIdx]}")
                        sys.stdout.flush()

                        inputBuf.seek(0)
                        inputBuf.truncate(0)
                        inputBuf.write(_HIST[historyIdx])
                        cur = inputBuf.tell()

                    except IndexError:
                        historyIdx += 1

        return True

    print()

    res = inputBuf.getvalue()
    if connectHistory:
        _HIST.append(res)

    return res