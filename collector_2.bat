@echo off
:loop

set mon=%DATE:~5,2%
set day=%DATE:~8,2%
set year=%DATE:~0,4%
set h=%time:~0,2%
set m=%time:~3,2%
set s=%time:~6,2%
set _time=%h%_%m%_%s%
set "_time=%_time: =%"
set filename="%year%%mon%%day%_%_time%_col2.log"

"C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\python.exe" "C:\workspace\trader\morning_server\collectors\request_client.py" collector2 > "C:\workspace\trader\logs\%filename%" 2>&1

goto loop
