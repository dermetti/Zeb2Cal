import PyInstaller.__main__

PyInstaller.__main__.run([
    'Zeb2Cal_gui.py',
    '--onefile',
    '--windowed',
    '-n Zeb2Cal-0.1.1',
    '--icon=zeb2cal_icon.ico',
    '--upx-dir=C:/Users/derme/Documents/upx-4.1.0-win64'
    ])