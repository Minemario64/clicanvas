from importlib.metadata import metadata
import os

def isOptionFlagEnabled(flag: str) -> bool:
    try:
        m = metadata("clicanvas")
        requested = m.get_all("Provides-Extra") or []
        return flag in requested

    except Exception:
        return False

if os.name == "nt" and isOptionFlagEnabled("thonny"):
    import os, sys, subprocess
    import ctypes, ctypes.wintypes as wintypes

    @lambda _: _()
    def ensureOutOfThonny():
        if sys.stdout.__class__.__name__ == "FakeOutputStream":
            subprocess.Popen(["python", os.path.abspath(sys.argv[0])], creationflags=subprocess.CREATE_NEW_CONSOLE)
            print("Re-launching in external console...")
            exit()

    def isANSIEnabled():
        kernel32 = ctypes.windll.kernel32
        h = kernel32.GetStdHandle(-11)   # STD_OUTPUT_HANDLE = -11
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(h, ctypes.byref(mode)) == 0:
            return False

        return bool(mode.value & 0x0004) # ENABLE_VIRTUAL_TERMINAL_PROCESSING

    def enableANSI():
        kernel32 = ctypes.windll.kernel32
        h = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        kernel32.GetConsoleMode(h, ctypes.byref(mode))
        kernel32.SetConsoleMode(h, mode.value | 0x0004)

    if not isANSIEnabled():
        enableANSI()

    class COORD(ctypes.Structure):
        _fields_ = [("X", wintypes.SHORT),
                    ("Y", wintypes.SHORT)]

    class SMALL_RECT(ctypes.Structure):
        _fields_ = [("Left", wintypes.SHORT),
                    ("Top", wintypes.SHORT),
                    ("Right", wintypes.SHORT),
                    ("Bottom", wintypes.SHORT)]

    class CONSOLE_SCREEN_BUFFER_INFOEX(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.ULONG),
            ("dwSize", COORD),
            ("dwCursorPosition", COORD),
            ("wAttributes", wintypes.WORD),
            ("srWindow", SMALL_RECT),
            ("dwMaximumWindowSize", COORD),
            ("wPopupAttributes", wintypes.WORD),
            ("bFullscreenSupported", wintypes.BOOL),
            ("ColorTable", wintypes.DWORD * 16)
        ]

    kernel32 = ctypes.windll.kernel32
    STDOUT = -11
    handle = kernel32.GetStdHandle(STDOUT)

    info = CONSOLE_SCREEN_BUFFER_INFOEX()
    info.cbSize = ctypes.sizeof(CONSOLE_SCREEN_BUFFER_INFOEX)

    kernel32.GetConsoleScreenBufferInfoEx(handle, ctypes.byref(info))

    def rgb(r: int, g: int, b: int) -> int:
        return (b << 16) | (g << 8) | r

    # Color Palette
    info.ColorTable[0] = rgb(24, 31, 40)
    info.ColorTable[4] = rgb(186, 7, 50)
    info.ColorTable[2] = rgb(26, 122, 62)
    info.ColorTable[6] = rgb(249, 163, 27)
    info.ColorTable[1] = rgb(40, 92, 196)
    info.ColorTable[5] = rgb(102, 25, 174)
    info.ColorTable[3] = rgb(0, 130, 125)
    info.ColorTable[7] = rgb(139, 147, 175)
    info.ColorTable[8] = rgb(51, 57, 65)
    info.ColorTable[12] = rgb(235, 58, 100)
    info.ColorTable[10] = rgb(57, 219, 117)
    info.ColorTable[14] = rgb(255, 252, 64)
    info.ColorTable[9] = rgb(36, 159, 222)
    info.ColorTable[13] = rgb(161, 47, 215)
    info.ColorTable[11] = rgb(40, 194, 149)
    info.ColorTable[15] = rgb(255, 255, 255)

    info.wAttributes = 0x07

    kernel32.SetConsoleScreenBufferInfoEx(handle, ctypes.byref(info))

    sys.stdout.write("\x1b[2J\x1b[3J\x1b[H")
    sys.stdout.flush()