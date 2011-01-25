#!/bin/sh

rem killall bribge.py >/dev/null 2>&1

#echo Lvov-2

rem # 356895035360612 ֻüגמג-5
python ./bribge.py 356895035360612

rem #echo GPS2
python ./bribge.py 356895035358996

exit

rem #echo GPS1
./bribge.py 356895035376246 >/dev/null 2>&1 &


rem #echo GPS3
./bribge.py 353358016204856 >/dev/null 2>&1 &

rem #echo GPS4
./bribge.py 359587015565669 >/dev/null 2>&1 &

rem #echo GPS5
./bribge.py 356895035360612 >/dev/null 2>&1 &

rem #echo GPS6
./bribge.py 359587015340758 >/dev/null 2>&1 &

rem #echo GPS7
./bribge.py 359587017100622 >/dev/null 2>&1 &

rem #echo GPS8
#./bribge.py 353358017117115 >/dev/null 2>&1 &

