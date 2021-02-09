:RUNNING
echo %DATE:~4,10% %TIME% - Server running...
python PrintServer\server.py
goto RUNNING
echo done
