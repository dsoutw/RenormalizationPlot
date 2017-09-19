@echo off
call pyuic5 -x MainWindowUI.ui -o MainWindowUI.py
call pyuic5 -x UnimodalWindowUI.ui -o UnimodalWindowUI.py
python Main.py