@echo off

if exist C:\Python26\python.exe SET PY_PATH=C:\Python26\python.exe
if exist C:\Python27\python.exe SET PY_PATH=C:\Python27\python.exe

:loop

echo .
echo .
echo .

echo Opel-Omega
%PY_PATH% bridge.py 356895035359317

goto :EOF

echo GPS1
%PY_PATH% bridge.py 356895035376246


echo GPS2
%PY_PATH% bridge.py 356895035358996


echo GPS6
%PY_PATH% bridge.py 359587015340758


echo GPS7
%PY_PATH% bridge.py 359587017100622


echo ===================================================
echo ^|^|  Для остановки синхнонизации нажмите Ctrl-C   ^|^|
echo ===================================================
rem D:\Programs\mingw\bin\sleep.exe 60

%PY_PATH% pause.py

goto loop