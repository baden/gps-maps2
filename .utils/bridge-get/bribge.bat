@echo off

if exist C:\Python26\python.exe SET PY_PATH=C:\Python26\python.exe
if exist C:\Python27\python.exe SET PY_PATH=C:\Python27\python.exe

:loop

echo .
echo .
echo .

%PY_PATH% bridge.py 359587015371480 �좮�-2
%PY_PATH% bridge.py 353358017117115 GPS-8
%PY_PATH% bridge.py 359587015328522 ������-11
%PY_PATH% bridge.py 359587017100622 GPS-7
%PY_PATH% bridge.py 359587015340758 �좮�-6
%PY_PATH% bridge.py 356895035360612 �좮�-5
%PY_PATH% bridge.py 359587015565669 �좮�-4
%PY_PATH% bridge.py 353358019726996 �⫠��筠� ��⥬�
%PY_PATH% bridge.py 356895035358996 GPS-2
%PY_PATH% bridge.py 356895035376246 GPS-1
%PY_PATH% bridge.py 356895035359317 Omega-Caravan AE1829BE
%PY_PATH% bridge.py 353358016204856 �������-3

echo ===================================================
echo ^|^|  ��� ��⠭���� ᨭ孮����樨 ������ Ctrl-C   ^|^|
echo ===================================================
rem D:\Programs\mingw\bin\sleep.exe 60

rem %PY_PATH% pause.py

rem goto loop


