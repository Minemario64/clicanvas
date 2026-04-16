from PIL import Image as img
import numpy as np
from pathlib import Path
from io import StringIO
from typing import Callable, Any

def do(func: Callable, *args, **kwargs) -> Any | None:
    try:
        return func(*args, **kwargs)

    except:
        return None

def render(image: Path | str | img.Image, *, bgColor: tuple[int, int, int] | None = None) -> str:
    res: StringIO = StringIO()
    if not isinstance(image, img.Image):
        image = img.open(image)

    image = image.convert("RGBA")
    bgStr: str = f"\x1b[48;2;{bgColor[0]};{bgColor[1]};{bgColor[2]}m" if not (bgColor is None) else "\x1b[0m"
    x: int = 0
    y: int = 0
    buff: tuple[list[tuple[int, int, int, int]], list[tuple[int, int, int, int]]] = ([], [])

    def processShader(pixel):
        nonlocal x, y, buff
        r, g, b, a = pixel
        # Implement processing
        if x >= image.width:
            x = 0
            y = (y + 1) % 2

        buff[y].append((r, g, b, a))
        if (len(buff[0]) >= image.width) and (len(buff[1]) >= image.width):
            for i in range(image.width):
                rgbas: tuple[tuple[int, int, int, int], tuple[int, int, int, int]] = (buff[0][i], buff[1][i])
                if rgbas[0] == rgbas[1]:
                    res.write(f"{f"\x1b[38;2;{rgbas[0][0]};{rgbas[0][1]};{rgbas[0][2]}m█" if rgbas[0][3] > 0 else f"{bgStr} "}")

                else:
                    if rgbas[0][3] > 0:
                        res.write(f"{f"\x1b[48;2;{rgbas[1][0]};{rgbas[1][1]};{rgbas[1][2]}m" if rgbas[1][3] > 0 else bgStr}\x1b[38;2;{rgbas[0][0]};{rgbas[0][1]};{rgbas[0][2]}m▀")

                    else:
                        res.write(f"{bgStr}\x1b[38;2;{rgbas[1][0]};{rgbas[1][1]};{rgbas[1][2]}m▄")

            res.write("\x1b[0m\n")
            buff = ([], [])

        x += 1
        return r, g, b, a

    arr = np.array(image)
    np.apply_along_axis(processShader, 2, arr)

    return res.getvalue().strip()

if __name__ == "__main__":
    import sys
    print(render(Path(do(lambda: sys.argv[1]) or input(": ")), bgColor=(127, 127, 127)))