from inputkit import handleInput, Key
import sys

def _inSlice(s: slice, n: int):
    start = s.start or 0
    step = s.step or 1
    stop = s.stop

    if stop is None:
        if step > 0:
            return n >= start and (n - start) % step == 0

        else:
            return n <= start and (start - n) % (-step) == 0

    if step > 0:
        return start <= n < stop and (n - start) % step == 0
    else:
        return stop < n <= start and (start - n) % (-step) == 0

def numInput(prompt: str, range: slice, n: int | None = None) -> int:
    """Prompts the user in the terminal with a custom input for a number spinner like `Threads: [4] 🠑🠓`

    Args:
        prompt (str): The prompt.
        range (slice): A slice for the min, max, and step for the limits of the input
        n (int | None, optional): The starting number, and must be in the range. Defaults to the lowest number in the range.

    Returns:
        int: The number the user picked.
    """

    if not _inSlice(range, n or range.start):
        raise ValueError("n is not in range")

    num: int = n or range.start

    def draw():
        sys.stdout.write(f"\r\x1b[2K{prompt} [{num}] \x1b[90m🠕🠗\x1b[0m")

    draw()

    @handleInput
    def inputHandler(key: str | Key) -> bool:
        nonlocal num
        match key:
            case Key.ENTER:
                return False

            case Key.UP | Key.DOWN:
                n = (range.step or 1) * (-1 if key == Key.DOWN else 1)
                if _inSlice(range, num + n):
                    num += n

                draw()

        return True

    print()

    return num