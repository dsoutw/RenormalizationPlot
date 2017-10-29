'''
Renormalization Plot - compile.py
    Compile source code before running the program
    Usage: python compile.py

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.
'''

import PyQt5.uic

with open('ui/unimodalwindowui.py', 'w', encoding='utf-8') as file:
    PyQt5.uic.compileUi('ui/unimodalwindowui.ui',file)

with open('ui/mainwindowui.py', 'w', encoding='utf-8') as file:
    PyQt5.uic.compileUi('ui/mainwindowui.ui',file)
