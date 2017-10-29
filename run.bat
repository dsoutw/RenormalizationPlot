@echo off
rem 	Renormalization Plot - run.bat
rem 	Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.
rem 	This file is part of Renormalization Plot which is released under 
rem 	the terms of the GNU General Public License version 3 as published 
rem 	by the Free Software Foundation. See LICENSE.txt or 
rem 	go to <http://www.gnu.org/licenses/> for full license details.

echo Renormalization Plot
echo Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.

rem call pyuic5 -x ui/mainwindowUI.ui -o ui/mainwindowui.py
rem call pyuic5 -x ui/unimodalwindowui.ui -o ui/unimodalwindowui.py
python compile.py
python main.py