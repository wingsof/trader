@echo off
:loop

timeout /t 30 /nobreak > NUL

IF EXIST C:\workspace\trader\READY (
timeout /t 10 /nobreak > NUL
"C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\python.exe" "C:\workspace\trader\morning_server\collectors\request_client.py" collector1 
)

goto loop
