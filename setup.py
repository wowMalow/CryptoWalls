"""
Script to generate one executable file for running app
automatically at startup. Before converting, run main.py
and choose template wallpaper.
If you haven't binance.csv or coins.txt, don't forget
to comment lines 27 or 28.
"""
import PyInstaller.__main__
import os
import shutil
from utils import PATH


def convert_to_exe():
    dir = PATH.replace('\\', '/')

    PyInstaller.__main__.run([
        'main.py',
        '--onefile',
        '--noconfirm',
        '--windowed',
        '--name=CryptoWall',
        '--icon=icon.ico',
        f'--add-data={dir}/images;images/',
        f'--add-data={dir}/images/widgets;images/widgets/',
        f'--add-data={dir}/images/template.png;images/',
        f'--add-data={dir}/binance.csv;.',
        f'--add-data={dir}/coins.txt;.'
    ])
    os.remove('CryptoWall.spec')
    shutil.rmtree(rf'{PATH}\build', ignore_errors=True)


if __name__ == '__main__':
    convert_to_exe()

