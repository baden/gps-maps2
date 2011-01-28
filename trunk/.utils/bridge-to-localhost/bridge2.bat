#!/bin/sh

rem killall bribge.py >/dev/null 2>&1

#echo Lvov-2

rem #echo GPS3 ַכאדמהא-3
python ./bribge.py 353358016204856 >nul 2>nul

rem exit

rem # 356895035360612 ֻüגמג-5
python ./bribge.py 356895035360612 >nul 2>nul

rem #echo GPS2
python ./bribge.py 356895035358996 >nul 2>nul

rem #echo GPS1
python ./bribge.py 356895035376246 >nul 2>nul


rem #echo GPS4
python ./bribge.py 359587015565669 >nul 2>nul

rem #echo GPS5
python ./bribge.py 356895035360612 >nul 2>nul

rem #echo GPS6
python ./bribge.py 359587015340758 >nul 2>nul

rem #echo GPS7
python ./bribge.py 359587017100622 >nul 2>nul

rem #echo GPS8
python ./bribge.py 353358017117115 >nul 2>nul

exit
