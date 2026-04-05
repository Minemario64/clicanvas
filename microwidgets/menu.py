from inputkit import Key, handleInput
from ._lib import ANSIColor, HighlightMode, _ANSI_START
import sys

VERSION = "1.0.0"

def menu(prompt: str, choices: list[object], defaultIdx: int = 0, cursor: str = ">", color: ANSIColor | tuple[int, int, int] | None = None, highlightMode: HighlightMode = HighlightMode.INVERT) -> object:
    """Prompts the user and gives them choices to pick from

    Args:
        prompt (str): The prompt
        choices (list[object]): The list of choices the user can pick from
        defaultIdx (int, optional): The index of the choices list where the cursor will start. Defaults to 0.
        cursor (str, optional): The character that represents what object the user is selecting visually. Defaults to ">".
        color (ANSIColor | tuple[int, int, int] | None, optional): The color either applied everywhere or just on the selected object, where None is no color. Defaults to None.
        highlightMode (HighlightMode, optional): The mode to highlight the current selected object. Defaults to HighlightMode.INVERT.

    Returns:
        object: The selected object
    """
    if not choices:
        return None

    pos: int = defaultIdx % len(choices)
    colorStr: str = f"\x1b[{color.value}m" if isinstance(color, ANSIColor) else f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m" if isinstance(color, tuple) else ''

    def draw() -> None:
        sys.stdout.write(f"{prompt}\r\n")

        for i, choice in enumerate(choices):
            sys.stdout.write(f"{colorStr if not (highlightMode == highlightMode.COLOR) else str()}{f'{cursor}' if i == pos else chr(32)} {(f'{_ANSI_START}7m' if highlightMode == HighlightMode.INVERT else colorStr if highlightMode == highlightMode.COLOR else f'{_ANSI_START}1m' if highlightMode == highlightMode.BOLD else str()) if i == pos else str()} {choice} {f'{_ANSI_START}0m' if (colorStr) or (i == pos) else str()}\r\n")

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


if __name__ == "__main__":
    print(menu("Select Language:", ["Python", "Rust", "Ruby", "Lua"], cursor="►", color=(255, 213, 64), highlightMode=HighlightMode.COLOR))