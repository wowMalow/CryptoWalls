from os import path


def root_path(filename: str = '') -> str:
    """
    Returns absolute path to file
    """
    return path.abspath(path.join(path.dirname(__file__), f'{filename}'))


PATH = root_path()
TEMPLATE = root_path(r'images\template.png')
WALLPAPER = root_path(r'images\wallpaper.png')
