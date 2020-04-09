@echo off
:loop

timeout /t 30 /nobreak > NUL

IF EXIST C:\workspace\trader\READY (
"C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\python.exe" "C:\workspace\trader\morning_server\collectors\request_client.py"
)

goto loop
