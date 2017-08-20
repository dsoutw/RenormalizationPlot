@echo off
call pyuic5 -x MainWindow.ui -o MainWindow.py
call pyuic5 -x PlotWindow.ui -o PlotWindow.py
python Main.py