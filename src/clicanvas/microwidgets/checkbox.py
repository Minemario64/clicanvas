from inputkit import Key, handleInput
from ._lib import ANSIColor, HighlightMode, _ANSI_START
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
    """Prompts the user with a list of choices that can be turned on and off

    Args:
        prompt (str): The prompt
        choices (list[CheckboxChoice]): The list of choices and their default states
        cursor (str, optional): The character(s) that represent the cursor to let the user know where they are in the list. Defaults to ">".
        color (ANSIColor | tuple[int, int, int] | None, optional): The color that can either be for everything or the selected object. Defaults to None.
        highlightMode (HighlightMode, optional): The mode to highlight the selected option. Defaults to HighlightMode.INVERT.
        keepOnScreen (bool, optional): When done, will keep the choices and prompt on screen instead of deleting them. Defaults to False.

    Returns:
        list[object]: The list of objects put in the choices that were selected by the user
    """
    if not choices:
        return []

    pos: int = 0
    colorStr: str = f"\x1b[{color.value}m" if isinstance(color, ANSIColor) else f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m" if isinstance(color, tuple) else ''

    @runImmediately
    def draw() -> None:
        sys.stdout.write(f"{prompt}\r\n")

        for i, choice in enumerate(choices):
                                                                                                                                                                                                                                                                                                                                                                        # chr(88) is X
            sys.stdout.write(f"{colorStr if not (highlightMode == highlightMode.COLOR) else str()}{cursor if i == pos else chr(32)*len(cursor)} {(f'{_ANSI_START}7m' if highlightMode == HighlightMode.INVERT else colorStr if highlightMode == highlightMode.COLOR else f'{_ANSI_START}1m' if highlightMode == highlightMode.BOLD else str()) if i == pos else str()} [{chr(88) if choice.selected else chr(32)}] {choice.choice} {f'{_ANSI_START}0m' if (colorStr) or (i == pos) else str()}\r\n")

        sys.stdout.write(f"\r\n{colorStr if not (highlightMode == highlightMode.COLOR) else str()}{cursor if pos == len(choices) else chr(32)*len(cursor)} {(f'{_ANSI_START}7m' if highlightMode == HighlightMode.INVERT else colorStr if highlightMode == highlightMode.COLOR else f'{_ANSI_START}1m' if highlightMode == highlightMode.BOLD else str()) if pos == len(choices) else str()} Confirm {f'{_ANSI_START}0m' if (colorStr) or (pos == len(choices)) else str()}\r\n")

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