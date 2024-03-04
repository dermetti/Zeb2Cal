import PyInstaller.__main__

PyInstaller.__main__.run([
    'AIRCal_gui_win.py',
    '--onedir',
    '--windowed',
    '-n AIRCal-0.1.0',
    #'--add-data', 'AIRCal_icon.ico;.',
    '-iAIRCal_icon.ico',
    '--upx-dir=C:/Users/derme/Documents/upx-4.1.0-win64'
    ])