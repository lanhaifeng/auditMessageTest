@echo off
taskkill -f -t -im javaw.exe

@rem kill last java.exe thread
@rem for /f "tokens=2" %%x in ('tasklist ^| findstr java.exe') do set PIDTOKILL=%%x
@rem for /f "tokens=2" %%x in ('tasklist ^| findstr java.exe ^| findstr %PIDTOKILL%') do taskkill /F /PID %%x
pause