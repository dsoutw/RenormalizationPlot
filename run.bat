@echo off
call pyuic5 -x MainWindowUI.ui -o MainWindowUI.py
call pyuic5 -x PlotWindowUI.ui -o PlotWindowUI.py
python Main.py