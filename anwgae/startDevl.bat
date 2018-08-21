current=%CD%
start dev_appserver.py --port 8090 --admin_port 8091 --clear_datastore true anetwars
timeout 3
client.py
cd ..\anw\Server
start testgalaxy.bat
cd ..\..\anwgae