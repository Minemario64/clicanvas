from inputkit import handleInput, Key
from io import StringIO
from ._lib import ANSIColor
import sys

VERSION = "1.0.0"

def percent(prompt: str, interval: float = 0.01, n: float = 0.0, width: int = 10, color: ANSIColor = ANSIColor.BRIGHT_WHITE) -> float:
    """Prompts the user and gets a percent, shown as a slider.

    Args:
        prompt (str): The prompt
        interval (float, optional): The change when moving the slider. Must be between 0.01 - 1. Defaults to 0.01.
        n (float, optional): Initial percent. Must be between 0 - 1. Defaults to 0.0.
        width (int, optional): The width of the slider. Defaults to 10.
        color (ANSIColor, optional): The color of the edges of the slider, the percent amount displayed, and the color of the full values in the slider. Defaults to ANSIColor.BRIGHT_WHITE.

    Raises:
        ValueError: if n is not between 0 - 1
        ValueError: if interval is not between 0.01 - 1

    Returns:
        float: the float representation of the percent
    """

    if not (0.0 <= n <= 1.0):
        raise ValueError(f"n must be between 0 - 1, not {n}")

    if not (0.01 <= interval <= 1.0):
        raise ValueError(f"interval must be between 0.01 - 1, not {n}")

    num: int = round(100 * n)
    step: int = round(100 * interval)

    def draw():
        n = 100 / (width*2)
        slide: StringIO = StringIO()
        for i in range(1, width+1):
            slide.write(f"\x1b[{color}m#" if num >= i * (n*2) else "\x1b[39m=" if (num >= (i-1) * (n*2)) and ((num / n) % 2 >= 1) else "\x1b[90m-" if (num > (i-1) * (n*2)) else " ")

        sys.stdout.write(f"\r\x1b[2K{prompt} \x1b[{color}m[{slide.getvalue()}\x1b[{color}m] {num}%\x1b[0m")

    draw()

    @handleInput
    def inputHandler(key: str | Key) -> bool:
        nonlocal num
        match key:
            case Key.ENTER:
                return False

            case Key.LEFT | Key.RIGHT:
                num += step if key == Key.RIGHT else -step
                if not (0 <= num <= 100):
                    num -= step if key == Key.RIGHT else -step

                draw()

        return True

    print()

    return num / 100