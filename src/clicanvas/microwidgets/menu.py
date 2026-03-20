from inputkit import Key, handleInput
from .__init__ import ANSIColor, HighlightMode
import sys

VERSION = "1.0.0"

def menu(prompt: str, choices: list[object], defaultIdx: int = 0, cursor: str = ">", color: ANSIColor | tuple[int, int, int] | None = None, highlightMode: HighlightMode = HighlightMode.INVERT) -> object:
    if not choices:
        return None

    pos: int = defaultIdx % len(choices)
    colorStr: str = f"\x1b[{color.value}m" if isinstance(color, ANSIColor) else f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m" if isinstance(color, tuple) else ''

    def draw() -> None:
        sys.stdout.write(f"{prompt}\r\n")

        for i, choice in enumerate(choices):
            sys.stdout.write(f"{colorStr if not (highlightMode == highlightMode.COLOR) else ''}{f"{cursor}" if i == pos else " "} {("\x1b[7m" if highlightMode == HighlightMode.INVERT else colorStr if highlightMode == highlightMode.COLOR else "\x1b[1m" if highlightMode == highlightMode.BOLD else '') if i == pos else ""} {choice} {"\x1b[0m" if (colorStr) or (i == pos) else ""}\r\n")

        sys.stdout.flush()

    draw()

    @handleInput
    def inputHandler(key: Key | str) -> bool:
        nonlocal pos
        match key:
            case Key.ENTER:
                return False

            case Key.UP:
                pos = (pos - 1) % len(choices)

            case Key.DOWN:
                pos = (pos + 1) % len(choices)

        sys.stdout.write(f"\x1b[{len(choices)+1}A")
        sys.stdout.flush()
        draw()

        return True

    return choices[pos]