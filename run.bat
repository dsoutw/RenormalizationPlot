@echo off
call pyuic5 -x ui/mainwindowUI.ui -o ui/mainwindowui.py
call pyuic5 -x ui/unimodalwindowui.ui -o ui/unimodalwindowui.py
python main.py