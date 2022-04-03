"""
Module places widgets on prepared template wallpaper.
Set widget position and allows to separately round image corners.
Supports multi monitors wallpapers.
"""
import win32api
import win32con
import win32gui
from PIL import Image, ImageDraw
from utils import PATH, TEMPLATE, WALLPAPER


def add_corners(im: Image, rad: float, all: bool = False,
                top_left: bool = False, top_right: bool = False,
                bottom_left: bool = False, bottom_right: bool = False) -> Image:
    """
    Round selected corners of the image
    """
    if all:
        top_left, top_right, bottom_left, bottom_right = True, True, True, True

    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size

    if top_left:
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    if bottom_left:
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    if top_right:
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    if bottom_right:
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def make_wallpaper() -> None:
    """
    Creates wallpaper image from template and widgets.
    Here you can customize wallpaper.
    """
    path_pie = rf'{PATH}\images\widgets\pie.png'
    path_table = rf'{PATH}\images\widgets\\table.png'
    path_chart_one = rf'{PATH}\images\widgets\chart1.png'
    path_chart_two = rf'{PATH}\images\widgets\chart2.png'

    # Initialize images
    background = Image.open(TEMPLATE)
    pie = Image.open(path_pie)
    table = Image.open(path_table)
    chart_one = Image.open(path_chart_one)
    chart_two = Image.open(path_chart_two)

    width = 1920
    heigth = 1080
    chart_x, chart_y = chart_one.size

    center_y = (heigth - chart_y*2) // 2

    # Adjust size and shape
    pie.thumbnail((400, 400), Image.ANTIALIAS)
    pie = add_corners(pie, 200, top_left=True)

    table.thumbnail((400, 1000), Image.ANTIALIAS)
    table = add_corners(table, 200, bottom_right=True)

    chart_one = add_corners(chart_one, 35, top_left=True, top_right=True)
    chart_two = add_corners(chart_two, 35, bottom_left=True, bottom_right=True)

    # Place widgets on template
    background.paste(table, (2400, 1530), table)
    background.paste(pie, (2400, 1180), pie)

    background.paste(chart_one, (2*width-center_y+20-chart_x,
                                 center_y-20), chart_one)
    background.paste(chart_two, (2*width-center_y+20-chart_x,
                                 chart_y+center_y-20), chart_two)

    background.save(WALLPAPER)


def set_wallpaper() -> None:
    key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,
                                r'Control Panel\Desktop', 0, win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "0")
    win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "1")
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, WALLPAPER, 1+2)


if __name__ == '__main__':
    make_wallpaper()
    set_wallpaper()