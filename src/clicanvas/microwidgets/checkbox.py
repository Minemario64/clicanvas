from inputkit import Key, handleInput
from .__init__ import ANSIColor, HighlightMode
from dataclasses import dataclass
from typing import Callable
import sys

def runImmediately(func: Callable) -> Callable:
    func()
    return func

@dataclass
class CheckboxChoice:
    choice: object
    selected: bool = False

VERSION = "1.0.0"

def checkbox(prompt: str, choices: list[CheckboxChoice], cursor: str = ">", color: ANSIColor | tuple[int, int, int] | None = None, highlightMode: HighlightMode = HighlightMode.INVERT, keepOnScreen: bool = False) -> list[object]:
    if not choices:
        return []

    pos: int = 0
    colorStr: str = f"\x1b[{color.value}m" if isinstance(color, ANSIColor) else f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m" if isinstance(color, tuple) else ''

    @runImmediately
    def draw() -> None:
        sys.stdout.write(f"{prompt}\r\n")

        for i, choice in enumerate(choices):
            sys.stdout.write(f"{colorStr if not (highlightMode == highlightMode.COLOR) else ''}{cursor if i == pos else " "*len(cursor)} {("\x1b[7m" if highlightMode == HighlightMode.INVERT else colorStr if highlightMode == highlightMode.COLOR else "\x1b[1m" if highlightMode == highlightMode.BOLD else '') if i == pos else ""} [{"X" if choice.selected else " "}] {choice.choice} {"\x1b[0m" if (colorStr) or (i == pos) else ""}\r\n")

        sys.stdout.write(f"\r\n{colorStr if not (highlightMode == highlightMode.COLOR) else ''}{cursor if pos == len(choices) else " "*len(cursor)} {("\x1b[7m" if highlightMode == HighlightMode.INVERT else colorStr if highlightMode == highlightMode.COLOR else "\x1b[1m" if highlightMode == highlightMode.BOLD else '') if pos == len(choices) else ""} Confirm {"\x1b[0m" if (colorStr) or (pos == len(choices)) else ""}\r\n")

        sys.stdout.flush()

    @handleInput
    def inputHandler(key: Key | str) -> bool:
        nonlocal pos
        match (key.lower() if isinstance(key, str) else key):
            case Key.CTRL_Q | "q":
                return False

            case Key.UP | Key.DOWN:
                pos = (pos + (-1 if key == Key.UP else 1)) % (len(choices) + 1)

            case Key.ENTER:
                if pos == len(choices):
                    return False

                choices[pos].selected = not choices[pos].selected

        sys.stdout.write(f"\x1b[{len(choices)+3}A")
        sys.stdout.flush()
        draw()

        return True

    if not keepOnScreen:
        for _ in range(len(choices) + 3):
            sys.stdout.write(f"\x1b[A\x1b[2K")

        sys.stdout.flush()

    return [choice.choice for choice in choices if choice.selected]

if __name__ == "__main__":
    print(checkbox("Select Features:", [
        CheckboxChoice("Math", True),
        CheckboxChoice("Logging")
    ], cursor="►", color=ANSIColor.BRIGHT_GREEN, highlightMode=HighlightMode.COLOR))