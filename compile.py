'''
Renormalization Plot - compile.py
    Compile source code before running the program
    Usage: python compile.py

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.

This file is part of Renormalization Plot which is released under 
the terms of the GNU General Public License version 3 as published 
by the Free Software Foundation. See LICENSE.txt or 
go to <http://www.gnu.org/licenses/> for full license details.
'''

import PyQt5.uic

with open('ui/unimodalwindowui.py', 'w', encoding='utf-8') as file:
    PyQt5.uic.compileUi('ui/unimodalwindowui.ui',file)

with open('ui/mainwindowui.py', 'w', encoding='utf-8') as file:
    PyQt5.uic.compileUi('ui/mainwindowui.ui',file)
