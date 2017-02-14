@echo off
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ok
) else (
    echo This program must be run from an administrator cmd prompt
    goto :fail
)

@echo on

pip install cloudshell-core cloudshell-cli cloudshell-snmp

pyinstaller --onefile driver.spec

taskkill /f /im Zlitest5.exe

timeout 3

set driverdir="c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers"
IF EXIST %driverdir% GOTO :havecs
set driverdir="c:\Program Files (x86)\QualiSystems\TestShell\Server\Drivers"
:havecs


copy dist\Zlitest5.exe                     %driverdir%
copy zlitest5_runtime_configuration.json %driverdir%



copy zlitest5_datamodel.xml               release\
copy dist\Zlitest5.exe                      release\
copy zlitest5_runtime_configuration.json  release\

:fail
