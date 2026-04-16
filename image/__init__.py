try:
    import PIL
    import numpy

except ImportError:
    print("\x1b[1;91mYou need pillow and numpy to use the subpackage 'clicanvas.image'. To use this, install \x1b[93mpillow\x1b[91m and \x1b[93mnumpy\x1b[91m.\x1b[0m")
    exit(128)

