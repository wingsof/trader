:loop

echo %time%
set h=%time:~0,2%
set m=%time:~3,2%
set s=%time:~6,2%
set _time=%h%_%m%_%s%
"C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\python.exe" "C:\workspace\trader\morning_server\collectors\request_client.py" > "C:\workspace\trader\logs\log%_time%.log" 2>&1

goto loop
